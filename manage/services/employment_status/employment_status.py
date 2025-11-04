

from manage.models import HippoEmploymentStatus
from manage.services.employment_status.schemas import HippoEmploymentStatusRead, HippoEmploymentStatusCreate, HippoEmploymentStatusUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user


apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

# Get all employment_status
@apiRouter.get("/employment_status/", response_model=list[HippoEmploymentStatusRead], dependencies=[Depends(get_current_active_user)],)
async def get_employment_status(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoEmploymentStatus).order_by(HippoEmploymentStatus.name))
    employment_status = result.scalars().all()
    return employment_status


# find a Employment_status by id
@apiRouter.get("/employment_status/{employment_status_id}", response_model=HippoEmploymentStatusRead, dependencies=[Depends(get_current_active_user)],)
async def get_Employment_status(employment_status_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoEmploymentStatus).where(HippoEmploymentStatus.id == employment_status_id))
    Employment_status = result.scalar_one_or_none()
    if not Employment_status:
        raise HTTPException(status_code=404, detail="Employment_status not found")
    return Employment_status

@apiRouter.post("/employment_status/", response_model=HippoEmploymentStatusRead, dependencies=[Depends(get_current_active_user)])
async def create_Employment_status(
    Employment_status:HippoEmploymentStatusCreate,
    session: AsyncSession = Depends(get_session),
):
    Employment_status_data = Employment_status.dict()  # get dict from pydantic model
    Employment_status_data['id'] = f"employment_status|{Employment_status.name}"
    
    new_Employment_status = HippoEmploymentStatus(**Employment_status_data)
    session.add(new_Employment_status)
    await session.commit()
    await session.refresh(new_Employment_status)
    return new_Employment_status

# update an existing Employment_status
@apiRouter.put("/employment_status/{employment_status_id}", response_model=HippoEmploymentStatusRead)
async def update_Employment_status(employment_status_id: str, Employment_status:HippoEmploymentStatusUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoEmploymentStatus).where(HippoEmploymentStatus.id == employment_status_id))
    existing_Employment_status = result.scalar_one_or_none()
    if not existing_Employment_status:
        raise HTTPException(status_code=404, detail="Employment_status not found")
    
    for key, value in Employment_status.dict().items():
        if value is not None:
            setattr(existing_Employment_status, key, value)
    
    await session.commit()
    await session.refresh(existing_Employment_status)
    return existing_Employment_status  

# delete a Employment_status
@apiRouter.delete("/employment_status/{employment_status_id}")
async def delete_Employment_status(employment_status_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoEmploymentStatus).where(HippoEmploymentStatus.id == employment_status_id))
    existing_Employment_status = result.scalar_one_or_none()
    if not existing_Employment_status:
        raise HTTPException(status_code=404, detail="Employment_status not found")
    
    await session.delete(existing_Employment_status)
    await session.commit()
    return {"detail": "Employment_status deleted successfully"}


