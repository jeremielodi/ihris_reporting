from manage.models import HippoDashboardQuery
from manage.services.dashboard_query.schemas import DashboardQueryRead, DashboardQueryCreate, DashboardQueryUpdate, DashboardQueryRun
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.future import select
from manage.database import SessionLocal
from endpoints.user_api import get_current_active_user
import uuid as uuid_lib

apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

# Get all Dashboard Queries
@apiRouter.post("/dashboard_queries/run")
async def post_run_dashboard_queries(data:DashboardQueryRun, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoDashboardQuery))

    try:
        result = await session.execute(data.sql)
        return result.all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


# Get all Dashboard Queries
@apiRouter.get("/dashboard_queries/", response_model=list[DashboardQueryRead])
async def get_dashboard_queries(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoDashboardQuery))
    dashboard_queries = result.scalars().all()
    return dashboard_queries


# Get all Dashboard Queries
@apiRouter.get("/dashboard_queries/for/{dashboard_uuid}", response_model=list[DashboardQueryRead])
async def get_dashboard_queries(dashboard_uuid:str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoDashboardQuery).where(HippoDashboardQuery.dashboard_uuid==dashboard_uuid))
    dashboard_queries = result.scalars().all()
    return dashboard_queries


# Find a Dashboard Query by UUID
@apiRouter.get("/dashboard_queries/{queryUuid}", response_model=DashboardQueryRead)
async def get_dashboard_query(queryUuid: str, session: AsyncSession = Depends(get_session)):
    try:
        uuid_obj = uuid_lib.UUID(queryUuid)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    result = await session.execute(select(HippoDashboardQuery).where(HippoDashboardQuery.uuid == uuid_obj))
    dashboard_query = result.scalar_one_or_none()
    if not dashboard_query:
        raise HTTPException(status_code=404, detail="Dashboard query not found")
    return dashboard_query

# Get Dashboard Queries by Dashboard UUID
@apiRouter.get("/dashboards/{dashboardUuid}/queries/", response_model=list[DashboardQueryRead])
async def get_dashboard_queries_by_dashboard(dashboardUuid: str, session: AsyncSession = Depends(get_session)):
    try:
        uuid_obj = uuid_lib.UUID(dashboardUuid)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    result = await session.execute(
        select(HippoDashboardQuery).where(HippoDashboardQuery.dashboard_uuid == uuid_obj)
    )
    dashboard_queries = result.scalars().all()
    return dashboard_queries

# Create a new Dashboard Query
@apiRouter.post("/dashboard_queries/", response_model=DashboardQueryRead, status_code=status.HTTP_201_CREATED)
async def create_dashboard_query(
    query_data: DashboardQueryCreate,
    session: AsyncSession = Depends(get_session),
    current_user: str = Depends(get_current_active_user)
):
    # Check if query already exists
    existing_result = await session.execute(
        select(HippoDashboardQuery).where(HippoDashboardQuery.query == query_data.query)
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

# Update a Dashboard Query
@apiRouter.put("/dashboard_queries/{queryUuid}", response_model=DashboardQueryRead)
async def update_dashboard_query(
    queryUuid: str,
    query_data: DashboardQueryUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: str = Depends(get_current_active_user)
):
    try:
        uuid_obj = uuid_lib.UUID(queryUuid)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    # Find existing query
    result = await session.execute(select(HippoDashboardQuery).where(HippoDashboardQuery.uuid == uuid_obj))
    existing_query = result.scalar_one_or_none()
    if not existing_query:
        raise HTTPException(status_code=404, detail="Dashboard query not found")
    
    # Check if new query value already exists (if being updated)
    if query_data.query and query_data.query != existing_query.query:
        existing_result = await session.execute(
            select(HippoDashboardQuery).where(HippoDashboardQuery.query == query_data.query)
        )
        duplicate_query = existing_result.scalar_one_or_none()
        if duplicate_query:
            raise HTTPException(status_code=400, detail="Query already exists")
    
    # Update fields
    update_data = query_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(existing_query, field):
            setattr(existing_query, field, value)
    
    # Always update audit fields
    existing_query.last_modified_by = current_user
    
    await session.commit()
    await session.refresh(existing_query)
    return existing_query

# Delete a Dashboard Query
@apiRouter.delete("/dashboard_queries/{queryUuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dashboard_query(
    queryUuid: str,
    session: AsyncSession = Depends(get_session),
    current_user: str = Depends(get_current_active_user)
):
    try:
        uuid_obj = uuid_lib.UUID(queryUuid)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    result = await session.execute(select(HippoDashboardQuery).where(HippoDashboardQuery.uuid == uuid_obj))
    dashboard_query = result.scalar_one_or_none()
    if not dashboard_query:
        raise HTTPException(status_code=404, detail="Dashboard query not found")
    
    await session.delete(dashboard_query)
    await session.commit()
    return None

# Search Dashboard Queries
@apiRouter.get("/dashboard_queries/search/", response_model=list[DashboardQueryRead])
async def search_dashboard_queries(
    query: str = None,
    dashboard_uuid: str = None,
    session: AsyncSession = Depends(get_session)
):
    stmt = select(HippoDashboardQuery)
    
    if query:
        stmt = stmt.where(HippoDashboardQuery.query.ilike(f"%{query}%"))
    
    if dashboard_uuid:
        try:
            uuid_obj = uuid_lib.UUID(dashboard_uuid)
            stmt = stmt.where(HippoDashboardQuery.dashboard_uuid == uuid_obj)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid dashboard UUID format")
    
    result = await session.execute(stmt)
    dashboard_queries = result.scalars().all()
    return dashboard_queries