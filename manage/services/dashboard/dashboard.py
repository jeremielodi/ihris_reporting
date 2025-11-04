from sqlalchemy.future import select
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import  text
from manage.services.dashboard.schemas import Dashboard, RoleDashboardAssign
from endpoints.user_api import get_current_active_user
from manage.models import HippoDashboard
from manage.database import SessionLocal
from typing import Any, Dict, List, Annotated
import uuid

router = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

@router.get("/dashboards/", response_model=list[Dashboard])
async def get_dashboards(session: AsyncSession = Depends(get_session)):
    try:
        result = await session.execute(select(HippoDashboard))
        dashboards = result.scalars().all()
        return dashboards
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching dashboards: {str(e)}"
        )
# In get_dashboard_by_uuid and other UUID parameter methods

# In get_dashboard_by_uuid and other UUID parameter methods
@router.get("/dashboards/{dashboard_uuid}", response_model=Dashboard)
async def get_dashboard_by_uuid(
    dashboard_uuid: str,  # Change from uuid.UUID to str
    session: AsyncSession = Depends(get_session),
):
    
    result = await session.execute(
        select(HippoDashboard).where(HippoDashboard.uuid == dashboard_uuid)
    )
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return row

@router.post("/dashboards/", response_model=Dashboard, status_code=status.HTTP_201_CREATED)
async def create_dashboard(
    data: Dashboard,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_active_user),
):
    try:
        data_dict = data.dict()
        # Convert UUID to string for database insertion
        data_dict['uuid'] = str(uuid.uuid4())
        data_dict['created_by'] = current_user_id
        data_dict['last_modified_by'] = current_user_id
        
        new_dashboard = HippoDashboard(**data_dict)
        session.add(new_dashboard)
        await session.commit()
        await session.refresh(new_dashboard)
        return new_dashboard
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating dashboard: {str(e)}"
        )
    
@router.put("/dashboards/{dashboardUuid}", response_model=Dashboard)
async def update_dashboard(
    dashboardUuid: str,
    data: Dashboard,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_active_user)
):
    try:
        # Validate UUID format
        try:
            uuid_obj = uuid.UUID(dashboardUuid)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid UUID format")

        # Convert UUID to string for database query
        dashboard_uuid_str = str(uuid_obj)
        
        # Find existing dashboard
        result = await session.execute(
            select(HippoDashboard).where(HippoDashboard.uuid == dashboard_uuid_str)
        )
        existing_dashboard = result.scalar_one_or_none()
        
        if not existing_dashboard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard not found"
            )
        
        # Define fields that can be updated
        allowed_update_fields = ['mb_dashboard_uuid', 'label', 'last_modified_by']
        
        # Update only allowed fields
        update_data = data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if field in allowed_update_fields:
                # Convert UUID values to strings if needed
                if isinstance(value, uuid.UUID):
                    value = str(value)
                setattr(existing_dashboard, field, value)
        
        # Always update audit fields
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

# Optional: Add delete endpoint
@router.delete("/dashboards/{dashboard_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dashboard(
    dashboard_uuid: str,
    session: AsyncSession = Depends(get_session),
):
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


# get dashboards and pages for a user by user id
@router.get("/dashboards/role/{role_id}")
async def get_dashboards_for_user(
    role_id: str,
    session: AsyncSession = Depends(get_session),
):
   
    # 2) Per-module pages with affected flag, use hippo_user_role to know user's roles and dashboards
    page_sql = text("""
       SELECT 
            d.uuid,
            d.mb_dashboard_id,
            d.label,
            CASE WHEN rd.dashboard_uuid IS NOT NULL THEN 1 ELSE 0 END as affected    
        FROM  hippo_dashboard  as d
        LEFT JOIN (
				SELECT dashboard_uuid
				FROM public.hippo_role_dashboard 
			    WHERE role_id = :role_id
		
		)rd ON rd.dashboard_uuid = d.uuid
    """)
   

    pages_res = await session.execute(page_sql, {"role_id": role_id })
    return pages_res.mappings().all()  



# get dashboards and pages for a user by user id
@router.get("/dashboards/user/assinged")
async def get_dashboards_for_user(
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_active_user),
):
    sql = text("""
       SELECT DISTINCT
            d.uuid,
            d.mb_dashboard_id,
            d.label   
        FROM  hippo_dashboard  as d
        JOIN (
				SELECT dashboard_uuid
				FROM public.hippo_role_dashboard 
			    WHERE role_id IN (
                    SELECT role_id
                    FROM  public.hippo_user_role
                    WHERE user_id = :user_id
                )
		)rd ON rd.dashboard_uuid = d.uuid
    """)
   

    pages_res = await session.execute(sql, {"user_id": current_user_id })
    return pages_res.mappings().all()  

@router.post("/dashboards/role", status_code=status.HTTP_201_CREATED)
async def assign_dashboards_to_role(
    data: RoleDashboardAssign,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_active_user),
):
    # Verify role exists
    role_exists = await session.execute(
        text("SELECT 1 FROM hippo_role WHERE id = :role_id"),
        {"role_id": data.role_id},
    )
    if role_exists.scalar() is None:
        raise HTTPException(status_code=404, detail="Role not found")

    # Verify all dashboard UUIDs exist (convert to strings)
    if data.dashboard_uuids:
        dashboard_uuids_str = [str(uuid) for uuid in data.dashboard_uuids if uuid]
        placeholders = ", ".join([f"'{uuid_str}'" for uuid_str in dashboard_uuids_str])
        
        existing_dashboards = await session.execute(
            text(f"SELECT uuid FROM hippo_dashboard WHERE uuid IN ({placeholders})")
        )
        existing_uuids = {str(row[0]) for row in existing_dashboards}
        
        missing_uuids = set(dashboard_uuids_str) - existing_uuids
        if missing_uuids:
            raise HTTPException(
                status_code=404,
                detail=f"Dashboards not found: {', '.join(missing_uuids)}"
            )

    # Transaction: delete old assignments and insert new ones
    try:
        # Delete current assignments for this role
        await session.execute(
            text("DELETE FROM hippo_role_dashboard WHERE role_id = :role_id"),
            {"role_id": data.role_id}
        )

        # Bulk insert new assignments (convert UUIDs to strings)
        if data.dashboard_uuids:
            rows = [
                {
                    "uuid": str(uuid.uuid4()),
                    "role_id": data.role_id,
                    "dashboard_uuid": str(dashboard_uuid),  # Convert to string
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