

from manage.models import HippoRegion
from manage.services.region.schemas import HippoRegionRead, HippoRegionCreate, HippoRegionUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user


apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

# Get all regions
@apiRouter.get("/regions/", response_model=list[HippoRegionRead], dependencies=[Depends(get_current_active_user)],)
async def get_regions(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoRegion).order_by(HippoRegion.name))
    regions = result.scalars().all()
    return regions


# find a Region by id
@apiRouter.get("/regions/{region_id}", response_model=HippoRegionRead, dependencies=[Depends(get_current_active_user)],)
async def get_Region(region_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoRegion).where(HippoRegion.id == region_id))
    Region = result.scalar_one_or_none()
    if not Region:
        raise HTTPException(status_code=404, detail="Region not found")
    return Region

@apiRouter.post("/regions/", response_model=HippoRegionRead, dependencies=[Depends(get_current_active_user)])
async def create_Region(
    Region:HippoRegionCreate,
    session: AsyncSession = Depends(get_session),
):
    Region_data = Region.dict()  # get dict from pydantic model
    Region_data['id'] = f"region|{Region.name}"
    
    new_Region = HippoRegion(**Region_data)
    session.add(new_Region)
    await session.commit()
    await session.refresh(new_Region)
    return new_Region

# update an existing Region
@apiRouter.put("/regions/{region_id}", response_model=HippoRegionRead)
async def update_Region(region_id: str, Region:HippoRegionUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoRegion).where(HippoRegion.id == region_id))
    existing_Region = result.scalar_one_or_none()
    if not existing_Region:
        raise HTTPException(status_code=404, detail="Region not found")
    
    for key, value in Region.dict().items():
        if value is not None:
            setattr(existing_Region, key, value)
    
    await session.commit()
    await session.refresh(existing_Region)
    return existing_Region  

# delete a Region
@apiRouter.delete("/regions/{region_id}")
async def delete_Region(region_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoRegion).where(HippoRegion.id == region_id))
    existing_Region = result.scalar_one_or_none()
    if not existing_Region:
        raise HTTPException(status_code=404, detail="Region not found")
    
    await session.delete(existing_Region)
    await session.commit()
    return {"detail": "Region deleted successfully"}


