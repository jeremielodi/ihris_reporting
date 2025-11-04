

from manage.models import HippoReasonDeparture
from manage.services.reason_departure.schemas import HippoReasonDepartureRead, HippoReasonDepartureCreate, HippoReasonDepartureUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user


apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

# Get all reason_departures
@apiRouter.get("/reason_departures/", response_model=list[HippoReasonDepartureRead], dependencies=[Depends(get_current_active_user)],)
async def get_reason_departures(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoReasonDeparture).order_by(HippoReasonDeparture.name))
    reason_departures = result.scalars().all()
    return reason_departures


# find a Reason_departure by id
@apiRouter.get("/reason_departures/{reason_departure_id}", response_model=HippoReasonDepartureRead, dependencies=[Depends(get_current_active_user)],)
async def get_Reason_departure(reason_departure_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoReasonDeparture).where(HippoReasonDeparture.id == reason_departure_id))
    Reason_departure = result.scalar_one_or_none()
    if not Reason_departure:
        raise HTTPException(status_code=404, detail="Reason_departure not found")
    return Reason_departure

@apiRouter.post("/reason_departures/", response_model=HippoReasonDepartureRead, dependencies=[Depends(get_current_active_user)])
async def create_Reason_departure(
    Reason_departure:HippoReasonDepartureCreate,
    session: AsyncSession = Depends(get_session),
):
    Reason_departure_data = Reason_departure.dict()  # get dict from pydantic model
    Reason_departure_data['id'] = f"reason_departure|{Reason_departure.name}"
    
    new_Reason_departure = HippoReasonDeparture(**Reason_departure_data)
    session.add(new_Reason_departure)
    await session.commit()
    await session.refresh(new_Reason_departure)
    return new_Reason_departure

# update an existing Reason_departure
@apiRouter.put("/reason_departures/{reason_departure_id}", response_model=HippoReasonDepartureRead)
async def update_Reason_departure(reason_departure_id: str, Reason_departure:HippoReasonDepartureUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoReasonDeparture).where(HippoReasonDeparture.id == reason_departure_id))
    existing_Reason_departure = result.scalar_one_or_none()
    if not existing_Reason_departure:
        raise HTTPException(status_code=404, detail="Reason_departure not found")
    
    for key, value in Reason_departure.dict().items():
        if value is not None:
            setattr(existing_Reason_departure, key, value)
    
    await session.commit()
    await session.refresh(existing_Reason_departure)
    return existing_Reason_departure  

# delete a Reason_departure
@apiRouter.delete("/reason_departures/{reason_departure_id}")
async def delete_Reason_departure(reason_departure_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoReasonDeparture).where(HippoReasonDeparture.id == reason_departure_id))
    existing_Reason_departure = result.scalar_one_or_none()
    if not existing_Reason_departure:
        raise HTTPException(status_code=404, detail="Reason_departure not found")
    
    await session.delete(existing_Reason_departure)
    await session.commit()
    return {"detail": "Reason_departure deleted successfully"}


