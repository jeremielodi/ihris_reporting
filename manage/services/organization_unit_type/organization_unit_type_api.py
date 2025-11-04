from manage.models import OrganizationUnitType
from manage.services.organization_unit_type.schemas import (
    OrganizationUnitTypeRead, 
    OrganizationUnitTypeCreate, 
    OrganizationUnitTypeUpdate
)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select

from manage.database import SessionLocal
from endpoints.user_api import get_current_active_user

apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

# Get all organization_unit_types
@apiRouter.get("/organization_unit_types/", response_model=list[OrganizationUnitTypeRead], dependencies=[Depends(get_current_active_user)])
async def get_organization_unit_types(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(OrganizationUnitType)
    )
    org_unit_types = result.scalars().all()
    return org_unit_types

# Find organization_unit_type by id
@apiRouter.get("/organization_unit_types/{org_unit_type_id}", response_model=OrganizationUnitTypeRead, dependencies=[Depends(get_current_active_user)])
async def get_organization_unit_type(org_unit_type_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(OrganizationUnitType).where(OrganizationUnitType.id == org_unit_type_id)
    )
    org_unit_type = result.scalar_one_or_none()
    if not org_unit_type:
        raise HTTPException(status_code=404, detail="Organization unit type not found")
    return org_unit_type

# Create new organization_unit_type
@apiRouter.post("/organization_unit_types/", response_model=OrganizationUnitTypeRead, dependencies=[Depends(get_current_active_user)])
async def create_organization_unit_type(
    org_unit_type: OrganizationUnitTypeCreate,
    session: AsyncSession = Depends(get_session),
):
    # Check if name already exists
    result = await session.execute(
        select(OrganizationUnitType).where(OrganizationUnitType.name == org_unit_type.name)
    )
    existing_type = result.scalar_one_or_none()
    if existing_type:
        raise HTTPException(status_code=400, detail="Organization unit type with this name already exists")
    
    org_unit_type_data = org_unit_type.dict()
    org_unit_type_data['id'] = f"org_unit_type|{org_unit_type.name.upper()}"
    
    new_org_unit_type = OrganizationUnitType(**org_unit_type_data)
    session.add(new_org_unit_type)
    await session.commit()
    await session.refresh(new_org_unit_type)
    return new_org_unit_type

# Update existing organization_unit_type
@apiRouter.put("/organization_unit_types/{org_unit_type_id}", response_model=OrganizationUnitTypeRead, dependencies=[Depends(get_current_active_user)])
async def update_organization_unit_type(
    org_unit_type_id: str, 
    org_unit_type: OrganizationUnitTypeUpdate, 
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(OrganizationUnitType).where(OrganizationUnitType.id == org_unit_type_id)
    )
    existing_org_unit_type = result.scalar_one_or_none()
    if not existing_org_unit_type:
        raise HTTPException(status_code=404, detail="Organization unit type not found")
    
    # Check if new name already exists (if name is being updated)
    if org_unit_type.name and org_unit_type.name != existing_org_unit_type.name:
        name_result = await session.execute(
            select(OrganizationUnitType).where(OrganizationUnitType.name == org_unit_type.name)
        )
        duplicate_type = name_result.scalar_one_or_none()
        if duplicate_type:
            raise HTTPException(status_code=400, detail="Organization unit type with this name already exists")
    
    for key, value in org_unit_type.dict(exclude_unset=True).items():
        if value is not None:
            setattr(existing_org_unit_type, key, value)
    
    await session.commit()
    await session.refresh(existing_org_unit_type)
    return existing_org_unit_type

# Delete organization_unit_type
@apiRouter.delete("/organization_unit_types/{org_unit_type_id}", dependencies=[Depends(get_current_active_user)])
async def delete_organization_unit_type(
    org_unit_type_id: str, 
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(OrganizationUnitType).where(OrganizationUnitType.id == org_unit_type_id)
    )
    existing_org_unit_type = result.scalar_one_or_none()
    if not existing_org_unit_type:
        raise HTTPException(status_code=404, detail="Organization unit type not found")
    
    await session.delete(existing_org_unit_type)
    await session.commit()
    return {"detail": "Organization unit type deleted successfully"}