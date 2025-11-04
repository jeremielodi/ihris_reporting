from manage.models import HippoFacilityType
from manage.services.facility_type.schemas import HippoFacilityTypeRead, HippoFacilityTypeCreate, HippoFacilityTypeUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user


apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

# Get all facility_types
@apiRouter.get("/facility_types/", response_model=list[HippoFacilityTypeRead], dependencies=[Depends(get_current_active_user)],)
async def get_facility_types(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoFacilityType).order_by(HippoFacilityType.name))
    facility_types = result.scalars().all()
    return facility_types


# find a Facility_type by id
@apiRouter.get("/facility_types/{facility_type_id}", response_model=HippoFacilityTypeRead, dependencies=[Depends(get_current_active_user)],)
async def get_Facility_type(facility_type_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoFacilityType).where(HippoFacilityType.id == facility_type_id))
    Facility_type = result.scalar_one_or_none()
    if not Facility_type:
        raise HTTPException(status_code=404, detail="Facility_type not found")
    return Facility_type

@apiRouter.post("/facility_types/", response_model=HippoFacilityTypeRead, dependencies=[Depends(get_current_active_user)])
async def create_Facility_type(
    Facility_type:HippoFacilityTypeCreate,
    session: AsyncSession = Depends(get_session),
):
    Facility_type_data = Facility_type.dict()  # get dict from pydantic model
    Facility_type_data['id'] = f"facility_type|{Facility_type.name}"
    
    new_Facility_type = HippoFacilityType(**Facility_type_data)
    session.add(new_Facility_type)
    await session.commit()
    await session.refresh(new_Facility_type)
    return new_Facility_type

# update an existing Facility_type
@apiRouter.put("/facility_types/{facility_type_id}", response_model=HippoFacilityTypeRead)
async def update_Facility_type(facility_type_id: str, Facility_type:HippoFacilityTypeUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoFacilityType).where(HippoFacilityType.id == facility_type_id))
    existing_Facility_type = result.scalar_one_or_none()
    if not existing_Facility_type:
        raise HTTPException(status_code=404, detail="Facility_type not found")
    
    for key, value in Facility_type.dict().items():
        if value is not None:
            setattr(existing_Facility_type, key, value)
    
    await session.commit()
    await session.refresh(existing_Facility_type)
    return existing_Facility_type  

# delete a Facility_type
@apiRouter.delete("/facility_types/{facility_type_id}")
async def delete_Facility_type(facility_type_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoFacilityType).where(HippoFacilityType.id == facility_type_id))
    existing_Facility_type = result.scalar_one_or_none()
    if not existing_Facility_type:
        raise HTTPException(status_code=404, detail="Facility_type not found")
    
    await session.delete(existing_Facility_type)
    await session.commit()
    return {"detail": "Facility_type deleted successfully"}


