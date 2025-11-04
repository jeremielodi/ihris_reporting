

from manage.models import HippoHealthArea
from manage.services.health_area.schemas import HippoHealthAreaRead, HippoHealthAreaCreate, HippoHealthAreaUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user
from sqlalchemy import text

apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

# Get all healthareas
@apiRouter.get("/health_areas/", response_model=list[HippoHealthAreaRead], dependencies=[Depends(get_current_active_user)],)
async def get_healthareas(db: AsyncSession = Depends(get_session)):
    result = await db.execute(text("""
        SELECT ha.*,  hc.name as county_name
        FROM hippo_health_area as ha
        JOIN hippo_county hc ON hc.id =  ha.county  
        ORDER BY hc.name
    """))
    rows = result.mappings().all()   # returns list of dict-like rows
    return rows


# find a HealthArea by id
@apiRouter.get("/health_areas/{healtharea_id}", response_model=HippoHealthAreaRead, dependencies=[Depends(get_current_active_user)],)
async def get_HealthArea(healtharea_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoHealthArea).where(HippoHealthArea.id == healtharea_id))
    HealthArea = result.scalar_one_or_none()
    if not HealthArea:
        raise HTTPException(status_code=404, detail="HealthArea not found")
    return HealthArea

@apiRouter.post("/health_areas/", response_model=HippoHealthAreaRead, dependencies=[Depends(get_current_active_user)])
async def create_HealthArea(
    HealthArea:HippoHealthAreaCreate,
    session: AsyncSession = Depends(get_session),
):
    HealthArea_data = HealthArea.dict()  # get dict from pydantic model
    HealthArea_data['id'] = f"healtharea|{HealthArea.name}"
    
    new_HealthArea = HippoHealthArea(**HealthArea_data)
    session.add(new_HealthArea)
    await session.commit()
    await session.refresh(new_HealthArea)
    return new_HealthArea

# update an existing HealthArea
@apiRouter.put("/health_areas/{healtharea_id}", response_model=HippoHealthAreaRead)
async def update_HealthArea(healtharea_id: str, HealthArea:HippoHealthAreaUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoHealthArea).where(HippoHealthArea.id == healtharea_id))
    existing_HealthArea = result.scalar_one_or_none()
    if not existing_HealthArea:
        raise HTTPException(status_code=404, detail="HealthArea not found")
    
    for key, value in HealthArea.dict().items():
        if value is not None:
            setattr(existing_HealthArea, key, value)
    
    await session.commit()
    await session.refresh(existing_HealthArea)
    return existing_HealthArea  

# delete a HealthArea
@apiRouter.delete("/health_areas/{healtharea_id}")
async def delete_HealthArea(healtharea_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoHealthArea).where(HippoHealthArea.id == healtharea_id))
    existing_HealthArea = result.scalar_one_or_none()
    if not existing_HealthArea:
        raise HTTPException(status_code=404, detail="HealthArea not found")
    
    await session.delete(existing_HealthArea)
    await session.commit()
    return {"detail": "HealthArea deleted successfully"}


