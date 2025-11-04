

from manage.models import HippoDistrict
from manage.services.district.schemas import HippoDistrictRead, HippoDistrictCreate, HippoDistrictUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user


apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

# Get all districts
@apiRouter.get("/districts/", response_model=list[HippoDistrictRead], dependencies=[Depends(get_current_active_user)],)
async def get_districts(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoDistrict).order_by(HippoDistrict.name))
    districts = result.scalars().all()
    return districts


# find a District by id
@apiRouter.get("/districts/{district_id}", response_model=HippoDistrictRead, dependencies=[Depends(get_current_active_user)],)
async def get_District(district_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoDistrict).where(HippoDistrict.id == district_id))
    District = result.scalar_one_or_none()
    if not District:
        raise HTTPException(status_code=404, detail="District not found")
    return District

@apiRouter.post("/districts/", response_model=HippoDistrictRead, dependencies=[Depends(get_current_active_user)])
async def create_District(
    District:HippoDistrictCreate,
    session: AsyncSession = Depends(get_session),
):
    District_data = District.dict()  # get dict from pydantic model
    District_data['id'] = f"district|{District.name}"
    
    new_District = HippoDistrict(**District_data)
    session.add(new_District)
    await session.commit()
    await session.refresh(new_District)
    return new_District

# update an existing District
@apiRouter.put("/districts/{district_id}", response_model=HippoDistrictRead)
async def update_District(district_id: str, District:HippoDistrictUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoDistrict).where(HippoDistrict.id == district_id))
    existing_District = result.scalar_one_or_none()
    if not existing_District:
        raise HTTPException(status_code=404, detail="District not found")
    
    for key, value in District.dict().items():
        if value is not None:
            setattr(existing_District, key, value)
    
    await session.commit()
    await session.refresh(existing_District)
    return existing_District  

# delete a District
@apiRouter.delete("/districts/{district_id}")
async def delete_District(district_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoDistrict).where(HippoDistrict.id == district_id))
    existing_District = result.scalar_one_or_none()
    if not existing_District:
        raise HTTPException(status_code=404, detail="District not found")
    
    await session.delete(existing_District)
    await session.commit()
    return {"detail": "District deleted successfully"}


