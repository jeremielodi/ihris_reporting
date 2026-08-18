# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

# SQLAlchemy ORM query builder
from sqlalchemy.future import select
from sqlalchemy import text

# FastAPI utilities
from fastapi import APIRouter, HTTPException, Depends, status

# Async database session
from sqlalchemy.ext.asyncio import AsyncSession

# Dashboard schemas
from manage.services.dashboard.schemas import Dashboard, RoleDashboardAssign

# Authentication dependency
from endpoints.user_api import get_current_active_user

# ORM model
from manage.models import HippoDashboard

# Database session factory
from manage.database import SessionLocal

# Standard typing
from typing import Any, Dict, List, Annotated

# UUID generator
import uuid


# Create router
router = APIRouter()


# ---------------------------------------------------------
# Dependency: Get Async DB Session
# ---------------------------------------------------------
async def get_session() -> AsyncSession:
    """
    Provides async database session.
    Ensures proper session lifecycle.
    """
    async with SessionLocal() as session:
        yield session


# =========================================================
# GET ALL DASHBOARDS
# =========================================================

@router.get("/dashboards/", response_model=list[Dashboard])
async def get_dashboards(session: AsyncSession = Depends(get_session)):
    """
    Retrieve all dashboards.

    Returns:
        List of dashboards stored in hippo_dashboard table.
    """
    try:
        result = await session.execute(select(HippoDashboard))
        dashboards = result.scalars().all()
        return dashboards
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching dashboards: {str(e)}"
        )


# =========================================================
# GET DASHBOARD BY UUID
# =========================================================

@router.get("/dashboards/{dashboard_uuid}", response_model=Dashboard)
async def get_dashboard_by_uuid(
    dashboard_uuid: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Retrieve a specific dashboard by UUID.
    """
    result = await session.execute(
        select(HippoDashboard).where(HippoDashboard.uuid == dashboard_uuid)
    )

    dashboard = result.scalar_one_or_none()

    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    return dashboard


# =========================================================
# CREATE DASHBOARD
# =========================================================

@router.post(
    "/dashboards/",
    response_model=Dashboard,
    status_code=status.HTTP_201_CREATED
)
async def create_dashboard(
    data: Dashboard,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_active_user),
):
    """
    Create a new dashboard.

    - Generates UUID automatically.
    - Stores audit fields (created_by, last_modified_by).
    """
    try:
        data_dict = data.model_dump()

        # Prevent registering the same Metabase dashboard twice
        existing = await session.execute(
            select(HippoDashboard).where(HippoDashboard.mb_dashboard_id == data_dict['mb_dashboard_id'])
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This Metabase dashboard is already registered"
            )

        # Generate unique UUID
        data_dict['uuid'] = str(uuid.uuid4())

        # Audit fields
        data_dict['created_by'] = current_user_id
        data_dict['last_modified_by'] = current_user_id

        new_dashboard = HippoDashboard(**data_dict)

        session.add(new_dashboard)
        await session.commit()
        await session.refresh(new_dashboard)

        return new_dashboard

    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating dashboard: {str(e)}"
        )


# =========================================================
# UPDATE DASHBOARD
# =========================================================

@router.put("/dashboards/{dashboardUuid}", response_model=Dashboard)
async def update_dashboard(
    dashboardUuid: str,
    data: Dashboard,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_active_user)
):
    """
    Update an existing dashboard.

    - Validates UUID format.
    - Only allows specific fields to be updated.
    - Automatically updates audit field.
    """
    try:
        # Validate UUID format
        try:
            uuid_obj = uuid.UUID(dashboardUuid)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid UUID format")

        dashboard_uuid_str = str(uuid_obj)

        # Fetch existing dashboard
        result = await session.execute(
            select(HippoDashboard).where(HippoDashboard.uuid == dashboard_uuid_str)
        )
        existing_dashboard = result.scalar_one_or_none()

        if not existing_dashboard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard not found"
            )

        # Only allow controlled fields
        allowed_update_fields = ['mb_dashboard_id', 'label']

        update_data = data.model_dump(exclude_unset=True)

        # Prevent updating to a Metabase dashboard already registered under another entry
        new_mb_id = update_data.get('mb_dashboard_id')
        if new_mb_id is not None and new_mb_id != existing_dashboard.mb_dashboard_id:
            duplicate = await session.execute(
                select(HippoDashboard).where(
                    HippoDashboard.mb_dashboard_id == new_mb_id,
                    HippoDashboard.uuid != dashboard_uuid_str,
                )
            )
            if duplicate.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="This Metabase dashboard is already registered"
                )

        for field, value in update_data.items():
            if field in allowed_update_fields:
                if isinstance(value, uuid.UUID):
                    value = str(value)
                setattr(existing_dashboard, field, value)

        # Always update audit field
        existing_dashboard.last_modified_by = current_user_id

        await session.commit()
        await session.refresh(existing_dashboard)

        return existing_dashboard

    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating dashboard: {str(e)}"
        )


# =========================================================
# DELETE DASHBOARD
# =========================================================

@router.delete("/dashboards/{dashboard_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dashboard(
    dashboard_uuid: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Delete dashboard by UUID.
    """

    try:
        result = await session.execute(
            select(HippoDashboard).where(HippoDashboard.uuid == dashboard_uuid)
        )
        dashboard = result.scalar_one_or_none()

        if not dashboard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard not found"
            )

        # Clean up role assignments (no FK/cascade on hippo_role_dashboard)
        await session.execute(
            text("DELETE FROM hippo_role_dashboard WHERE dashboard_uuid = :dashboard_uuid"),
            {"dashboard_uuid": dashboard_uuid}
        )

        await session.delete(dashboard)
        await session.commit()

    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deleting dashboard: {str(e)}"
        )


# =========================================================
# GET DASHBOARDS FOR ROLE (WITH ASSIGNMENT FLAG)
# =========================================================

@router.get("/dashboards/role/{role_id}")
async def get_dashboards_for_role(
    role_id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Retrieve all dashboards and mark which ones are assigned to a given role.

    Returns:
        affected = 1 if assigned
        affected = 0 if not assigned
    """

    page_sql = text("""
       SELECT 
            d.uuid,
            d.mb_dashboard_id,
            d.label,
            CASE WHEN rd.dashboard_uuid IS NOT NULL THEN 1 ELSE 0 END as affected    
        FROM  hippo_dashboard  as d
        LEFT JOIN (
            SELECT dashboard_uuid
            FROM hippo_role_dashboard 
            WHERE role_id = :role_id
        ) rd ON rd.dashboard_uuid = d.uuid
    """)

    pages_res = await session.execute(page_sql, {"role_id": role_id})
    return pages_res.mappings().all()


# =========================================================
# GET DASHBOARDS ASSIGNED TO CURRENT USER
# =========================================================

@router.get("/dashboards/user/assigned")
async def get_dashboards_for_user(
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_active_user),
):
    """
    Retrieve dashboards assigned to current user
    through role membership.
    """

    sql = text("""
       SELECT DISTINCT
            d.uuid,
            d.mb_dashboard_id,
            d.label   
        FROM hippo_dashboard d
        JOIN (
            SELECT dashboard_uuid
            FROM hippo_role_dashboard 
            WHERE role_id IN (
                SELECT role_id
                FROM hippo_user_role
                WHERE user_id = :user_id
            )
        ) rd ON rd.dashboard_uuid = d.uuid
    """)

    pages_res = await session.execute(sql, {"user_id": current_user_id})
    return pages_res.mappings().all()


# =========================================================
# ASSIGN DASHBOARDS TO ROLE
# =========================================================

@router.post("/dashboards/role", status_code=status.HTTP_201_CREATED)
async def assign_dashboards_to_role(
    data: RoleDashboardAssign,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_active_user),
):
    """
    Assign dashboards to a role.

    Process:
    1. Validate role exists
    2. Validate dashboards exist
    3. Delete previous assignments
    4. Insert new assignments in bulk
    """

    # Validate role
    role_exists = await session.execute(
        text("SELECT 1 FROM hippo_role WHERE id = :role_id"),
        {"role_id": data.role_id},
    )
    if role_exists.scalar() is None:
        raise HTTPException(status_code=404, detail="Role not found")

    try:
        # Remove old assignments
        await session.execute(
            text("DELETE FROM hippo_role_dashboard WHERE role_id = :role_id"),
            {"role_id": data.role_id}
        )

        # Insert new assignments
        if data.dashboard_uuids:
            rows = [
                {
                    "uuid": str(uuid.uuid4()),
                    "role_id": data.role_id,
                    "dashboard_uuid": str(dashboard_uuid),
                    "created_by": current_user_id,
                    "last_modified_by": current_user_id
                }
                for dashboard_uuid in data.dashboard_uuids
            ]

            await session.execute(
                text("""
                    INSERT INTO hippo_role_dashboard 
                    (uuid, role_id, dashboard_uuid, created_by, last_modified_by)
                    VALUES (:uuid, :role_id, :dashboard_uuid, :created_by, :last_modified_by)
                """),
                rows
            )

        await session.commit()

        return {
            "role_id": data.role_id,
            "dashboards_assigned": data.dashboard_uuids or []
        }

    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error assigning dashboards to role: {str(e)}"
        )