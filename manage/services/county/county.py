

from manage.models import HippoCounty
from manage.services.county.schemas import HippoCountyRead, HippoCountyCreate, HippoCountyUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user


apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

# Get all counties
@apiRouter.get("/counties/", response_model=list[HippoCountyRead], dependencies=[Depends(get_current_active_user)],)
async def get_counties(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoCounty).order_by(HippoCounty.name))
    counties = result.scalars().all()
    return counties


# find a County by id
@apiRouter.get("/counties/{county_id}", response_model=HippoCountyRead, dependencies=[Depends(get_current_active_user)],)
async def get_County(county_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoCounty).where(HippoCounty.id == county_id))
    County = result.scalar_one_or_none()
    if not County:
        raise HTTPException(status_code=404, detail="County not found")
    return County

@apiRouter.post("/counties/", response_model=HippoCountyRead, dependencies=[Depends(get_current_active_user)])
async def create_County(
    County:HippoCountyCreate,
    session: AsyncSession = Depends(get_session),
):
    County_data = County.dict()  # get dict from pydantic model
    County_data['id'] = f"county|{County.name}"
    
    new_County = HippoCounty(**County_data)
    session.add(new_County)
    await session.commit()
    await session.refresh(new_County)
    return new_County

# update an existing County
@apiRouter.put("/counties/{county_id}", response_model=HippoCountyRead)
async def update_County(county_id: str, County:HippoCountyUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoCounty).where(HippoCounty.id == county_id))
    existing_County = result.scalar_one_or_none()
    if not existing_County:
        raise HTTPException(status_code=404, detail="County not found")
    
    for key, value in County.dict().items():
        if value is not None:
            setattr(existing_County, key, value)
    
    await session.commit()
    await session.refresh(existing_County)
    return existing_County  

# delete a County
@apiRouter.delete("/counties/{county_id}")
async def delete_County(county_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoCounty).where(HippoCounty.id == county_id))
    existing_County = result.scalar_one_or_none()
    if not existing_County:
        raise HTTPException(status_code=404, detail="County not found")
    
    await session.delete(existing_County)
    await session.commit()
    return {"detail": "County deleted successfully"}


