

from manage.models import HippoFacility
from manage.services.facility.schemas import HippoFacilityRead, HippoFacilityCreate, HippoFacilityUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user


apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

# Get all facilities
@apiRouter.get("/facilities/", response_model=list[HippoFacilityRead], dependencies=[Depends(get_current_active_user)],)
async def get_facilities(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoFacility).order_by(HippoFacility.name).limit(100))
    facilities = result.scalars().all()
    return facilities


# find a Facility by id
@apiRouter.get("/facilities/{facility_id}", response_model=HippoFacilityRead, dependencies=[Depends(get_current_active_user)],)
async def get_Facility(facility_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoFacility).where(HippoFacility.id == facility_id))
    Facility = result.scalar_one_or_none()
    if not Facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    return Facility

@apiRouter.post("/facilities/", response_model=HippoFacilityRead, dependencies=[Depends(get_current_active_user)])
async def create_Facility(
    Facility:HippoFacilityCreate,
    session: AsyncSession = Depends(get_session),
):
    Facility_data = Facility.dict()  # get dict from pydantic model
    Facility_data['id'] = f"facility|{Facility.name}"
    
    new_Facility = HippoFacility(**Facility_data)
    session.add(new_Facility)
    await session.commit()
    await session.refresh(new_Facility)
    return new_Facility

# update an existing Facility
@apiRouter.put("/facilities/{facility_id}", response_model=HippoFacilityRead)
async def update_Facility(facility_id: str, Facility:HippoFacilityUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoFacility).where(HippoFacility.id == facility_id))
    existing_Facility = result.scalar_one_or_none()
    if not existing_Facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    
    for key, value in Facility.dict().items():
        if value is not None:
            setattr(existing_Facility, key, value)
    
    await session.commit()
    await session.refresh(existing_Facility)
    return existing_Facility  

# delete a Facility
@apiRouter.delete("/facilities/{facility_id}")
async def delete_Facility(facility_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoFacility).where(HippoFacility.id == facility_id))
    existing_Facility = result.scalar_one_or_none()
    if not existing_Facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    
    await session.delete(existing_Facility)
    await session.commit()
    return {"detail": "Facility deleted successfully"}


