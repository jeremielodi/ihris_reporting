from manage.models import HippoMaritalStatus
from manage.services.marital_status.schemas import HippoMaritalStatusRead
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from manage.database import SessionLocal
from endpoints.user_api import get_current_active_user


apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

# Get all maritalStatus
@apiRouter.get("/marital_status/", response_model=list[HippoMaritalStatusRead])
async def get_maritalStatus(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoMaritalStatus))
    maritalStatus = result.scalars().all()
    return maritalStatus


# find a maritalStatus by id
@apiRouter.get("/marital_status/{maritalStatusId}", response_model=HippoMaritalStatusRead, dependencies=[Depends(get_current_active_user)],)
async def get_maritalStatus(maritalStatusId: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoMaritalStatus).where(HippoMaritalStatus.id == maritalStatusId))
    maritalStatus = result.scalar_one_or_none()
    if not maritalStatus:
        raise HTTPException(status_code=404, detail="Marital status not found")
    return maritalStatus
