# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

# ORM model
from manage.models import HippoDashboardQuery

# Pydantic schemas (validation + serialization)
from manage.services.dashboard_query.schemas import (
    DashboardQueryRead,
    DashboardQueryCreate,
    DashboardQueryUpdate,
    DashboardQueryRun
)

# Async database session
from sqlalchemy.ext.asyncio import AsyncSession

# FastAPI utilities
from fastapi import APIRouter, Depends, HTTPException, status

# SQLAlchemy ORM query builder
from sqlalchemy.future import select
from sqlalchemy import text

# Database session factory
from manage.database import SessionLocal

# Authentication dependency
from endpoints.user_api import get_current_active_user

# UUID handling
import uuid as uuid_lib
import re


# Create router
apiRouter = APIRouter()

# Only allow read-only statements through the ad-hoc SQL runner below.
_DISALLOWED_SQL_KEYWORDS = re.compile(
    r"\b(insert|update|delete|drop|alter|create|truncate|grant|revoke|"
    r"attach|copy|vacuum|call|do|execute|merge)\b",
    re.IGNORECASE,
)


def _assert_read_only_sql(sql: str) -> None:
    statements = [s.strip() for s in sql.split(";") if s.strip()]
    if len(statements) != 1:
        raise HTTPException(status_code=400, detail="Only a single SELECT statement is allowed")
    statement = statements[0]
    if not statement.lower().startswith(("select", "with")):
        raise HTTPException(status_code=400, detail="Only SELECT statements are allowed")
    if _DISALLOWED_SQL_KEYWORDS.search(statement):
        raise HTTPException(status_code=400, detail="Statement contains a disallowed keyword")


# ---------------------------------------------------------
# Dependency: Get Async DB Session
# ---------------------------------------------------------
async def get_session() -> AsyncSession:
    """
    Provides async database session.
    Ensures safe session lifecycle management.
    """
    async with SessionLocal() as session:
        yield session


# =========================================================
# RUN CUSTOM DASHBOARD QUERY
# =========================================================

@apiRouter.post(
    "/dashboard_queries/run",
    dependencies=[Depends(get_current_active_user)],
)
async def post_run_dashboard_queries(
    data: DashboardQueryRun,
    session: AsyncSession = Depends(get_session)
):
    """
    Execute a dashboard-authored SQL query.

    Restricted to a single read-only SELECT/WITH statement (see
    _assert_read_only_sql) and requires authentication, since this
    endpoint otherwise gives direct SQL access to the database.
    """

    _assert_read_only_sql(data.sql)

    try:
        result = await session.execute(text(data.sql), data.parameters or {})
        return result.mappings().all()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )


# =========================================================
# GET ALL DASHBOARD QUERIES
# =========================================================

@apiRouter.get(
    "/dashboard_queries/",
    response_model=list[DashboardQueryRead],
    dependencies=[Depends(get_current_active_user)],
)
async def get_dashboard_queries(session: AsyncSession = Depends(get_session)):
    """
    Retrieve all dashboard queries.
    """

    result = await session.execute(select(HippoDashboardQuery))
    dashboard_queries = result.scalars().all()
    return dashboard_queries


# =========================================================
# GET DASHBOARD QUERIES BY DASHBOARD UUID
# =========================================================

@apiRouter.get(
    "/dashboard_queries/for/{dashboard_uuid}",
    response_model=list[DashboardQueryRead],
    dependencies=[Depends(get_current_active_user)],
)
async def get_dashboard_queries_for_dashboard(
    dashboard_uuid: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieve all queries linked to a specific dashboard.
    """

    result = await session.execute(
        select(HippoDashboardQuery).where(
            HippoDashboardQuery.dashboard_uuid == dashboard_uuid
        )
    )

    dashboard_queries = result.scalars().all()
    return dashboard_queries


# =========================================================
# GET DASHBOARD QUERY BY UUID
# =========================================================

@apiRouter.get(
    "/dashboard_queries/{queryUuid}",
    response_model=DashboardQueryRead,
    dependencies=[Depends(get_current_active_user)],
)
async def get_dashboard_query(
    queryUuid: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieve a dashboard query by UUID.
    """

    try:
        uuid_obj = uuid_lib.UUID(queryUuid)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    result = await session.execute(
        select(HippoDashboardQuery).where(
            HippoDashboardQuery.uuid == uuid_obj
        )
    )

    dashboard_query = result.scalar_one_or_none()

    if not dashboard_query:
        raise HTTPException(status_code=404, detail="Dashboard query not found")

    return dashboard_query


# =========================================================
# CREATE DASHBOARD QUERY
# =========================================================

@apiRouter.post(
    "/dashboard_queries/",
    response_model=DashboardQueryRead,
    status_code=status.HTTP_201_CREATED
)
async def create_dashboard_query(
    query_data: DashboardQueryCreate,
    session: AsyncSession = Depends(get_session),
    current_user: str = Depends(get_current_active_user)
):
    """
    Create a new dashboard query.

    - Prevent duplicate query strings.
    - Store layout position (row_index, col_index).
    - Store parameters JSON.
    """

    # Prevent duplicate query text
    existing_result = await session.execute(
        select(HippoDashboardQuery).where(
            HippoDashboardQuery.query == query_data.query
        )
    )

    existing_query = existing_result.scalar_one_or_none()

    if existing_query:
        raise HTTPException(status_code=400, detail="Query already exists")

    new_query = HippoDashboardQuery(
        dashboard_uuid=query_data.dashboard_uuid,
        query=query_data.query,
        parameters=query_data.parameters or {},
        row_index=query_data.row_index,
        col_index=query_data.col_index,
        created_by=current_user,
        last_modified_by=current_user
    )

    session.add(new_query)
    await session.commit()
    await session.refresh(new_query)

    return new_query


# =========================================================
# UPDATE DASHBOARD QUERY
# =========================================================

@apiRouter.put("/dashboard_queries/{queryUuid}", response_model=DashboardQueryRead)
async def update_dashboard_query(
    queryUuid: str,
    query_data: DashboardQueryUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: str = Depends(get_current_active_user)
):
    """
    Update an existing dashboard query.

    - Validates UUID format.
    - Prevents duplicate query text.
    - Updates audit field.
    """

    try:
        uuid_obj = uuid_lib.UUID(queryUuid)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    result = await session.execute(
        select(HippoDashboardQuery).where(
            HippoDashboardQuery.uuid == uuid_obj
        )
    )

    existing_query = result.scalar_one_or_none()

    if not existing_query:
        raise HTTPException(status_code=404, detail="Dashboard query not found")

    # Prevent duplicate query text
    if query_data.query and query_data.query != existing_query.query:
        duplicate_result = await session.execute(
            select(HippoDashboardQuery).where(
                HippoDashboardQuery.query == query_data.query
            )
        )
        duplicate_query = duplicate_result.scalar_one_or_none()
        if duplicate_query:
            raise HTTPException(status_code=400, detail="Query already exists")

    # Update fields dynamically
    update_data = query_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if hasattr(existing_query, field):
            setattr(existing_query, field, value)

    # Update audit field
    existing_query.last_modified_by = current_user

    await session.commit()
    await session.refresh(existing_query)

    return existing_query


# =========================================================
# DELETE DASHBOARD QUERY
# =========================================================

@apiRouter.delete("/dashboard_queries/{queryUuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dashboard_query(
    queryUuid: str,
    session: AsyncSession = Depends(get_session),
    current_user: str = Depends(get_current_active_user)
):
    """
    Delete a dashboard query by UUID.
    """

    try:
        uuid_obj = uuid_lib.UUID(queryUuid)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    result = await session.execute(
        select(HippoDashboardQuery).where(
            HippoDashboardQuery.uuid == uuid_obj
        )
    )

    dashboard_query = result.scalar_one_or_none()

    if not dashboard_query:
        raise HTTPException(status_code=404, detail="Dashboard query not found")

    await session.delete(dashboard_query)
    await session.commit()

    return None


# =========================================================
# SEARCH DASHBOARD QUERIES
# =========================================================

@apiRouter.get(
    "/dashboard_queries/search/",
    response_model=list[DashboardQueryRead],
    dependencies=[Depends(get_current_active_user)],
)
async def search_dashboard_queries(
    query: str = None,
    dashboard_uuid: str = None,
    session: AsyncSession = Depends(get_session)
):
    """
    Search dashboard queries.

    Supports:
    - Partial text search on query field
    - Filter by dashboard UUID
    """

    stmt = select(HippoDashboardQuery)

    if query:
        stmt = stmt.where(
            HippoDashboardQuery.query.ilike(f"%{query}%")
        )

    if dashboard_uuid:
        try:
            uuid_obj = uuid_lib.UUID(dashboard_uuid)
            stmt = stmt.where(
                HippoDashboardQuery.dashboard_uuid == uuid_obj
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid dashboard UUID format")

    result = await session.execute(stmt)
    dashboard_queries = result.scalars().all()

    return dashboard_queries