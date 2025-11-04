from manage.models import OrganizationUnitStandards
from manage.services.standards.schemas import (
    OrganizationUnitStandardsRead,
    OrganizationUnitStandardsCreate, 
    OrganizationUnitStandardsUpdate
)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from manage.database import SessionLocal
from endpoints.user_api import get_current_active_user
import uuid
from sqlalchemy import text

apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

# Get all organization_unit_standards
@apiRouter.get("/organization_unit_standards/", response_model=list, dependencies=[Depends(get_current_active_user)])
async def get_organization_unit_standards(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        text("""
        SELECT     
            ous.*,
            hcl.name as classification_name,
            out.name as org_unit_type_name
        FROM public.organization_unit_standards ous
        JOIN public.hippo_classification hcl  ON hcl.id = ous.classification_id
        JOIN public.organization_unit_type out ON ous.org_unit_type_id = out.id
        """)
    )
    org_unit_standards = result.all()
    return org_unit_standards

# Find organization_unit_standards by UUID
@apiRouter.get("/organization_unit_standards/{org_standard_uuid}", response_model=OrganizationUnitStandardsRead, dependencies=[Depends(get_current_active_user)])
async def get_organization_unit_standard(org_standard_uuid: uuid.UUID, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(OrganizationUnitStandards)
        .where(OrganizationUnitStandards.uuid == uuid.UUID(str(org_standard_uuid)))
        .where(OrganizationUnitStandards.i2ce_hidden == 0)
    )
    org_unit_standard = result.scalar_one_or_none()
    if not org_unit_standard:
        raise HTTPException(status_code=404, detail="Organization unit standard not found")
    return org_unit_standard

# Create new organization_unit_standards
@apiRouter.post("/organization_unit_standards/", response_model=OrganizationUnitStandardsRead, dependencies=[Depends(get_current_active_user)])
async def create_organization_unit_standard(
    org_standard: OrganizationUnitStandardsCreate,
    session: AsyncSession = Depends(get_session),
):
    org_standard_data = org_standard.dict()
    org_standard_data['uuid'] = uuid.uuid4()
    
    new_org_standard = OrganizationUnitStandards(**org_standard_data)
    session.add(new_org_standard)
    await session.commit()
    await session.refresh(new_org_standard)
    return new_org_standard

# Update existing organization_unit_standards
@apiRouter.put("/organization_unit_standards/{org_standard_uuid}", response_model=OrganizationUnitStandardsRead, dependencies=[Depends(get_current_active_user)])
async def update_organization_unit_standard(
    org_standard_uuid: uuid.UUID, 
    org_standard: OrganizationUnitStandardsUpdate, 
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(OrganizationUnitStandards)
        .where(OrganizationUnitStandards.uuid == org_standard_uuid)
        .where(OrganizationUnitStandards.i2ce_hidden == 0)
    )
    existing_org_standard = result.scalar_one_or_none()
    if not existing_org_standard:
        raise HTTPException(status_code=404, detail="Organization unit standard not found")
    
    for key, value in org_standard.dict(exclude_unset=True).items():
        if value is not None and key != 'created' and key != 'uuid':
            setattr(existing_org_standard, key, value)
    
    await session.commit()
    await session.refresh(existing_org_standard)
    return existing_org_standard

# Delete organization_unit_standards (soft delete using i2ce_hidden)
@apiRouter.delete("/organization_unit_standards/{org_standard_uuid}", dependencies=[Depends(get_current_active_user)])
async def delete_organization_unit_standard(
    org_standard_uuid: uuid.UUID, 
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(OrganizationUnitStandards)
        .where(OrganizationUnitStandards.uuid == org_standard_uuid)
        .where(OrganizationUnitStandards.i2ce_hidden == 0)
    )
    existing_org_standard = result.scalar_one_or_none()
    if not existing_org_standard:
        raise HTTPException(status_code=404, detail="Organization unit standard not found")
    
    # Soft delete by setting i2ce_hidden to 1
    existing_org_standard.i2ce_hidden = 1
    await session.commit()
    return {"detail": "Organization unit standard deleted successfully"}