from manage.models import HippoEmployeeStatus
from manage.services.employee_status.schemas import HippoEmployeeStatusRead
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from manage.database import SessionLocal
from endpoints.user_api import get_current_active_user


apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

# Get all employeeStatus
@apiRouter.get("/employee_status/", response_model=list[HippoEmployeeStatusRead], dependencies=[Depends(get_current_active_user)],)
async def get_employeeStatus(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoEmployeeStatus))
    employeeStatus = result.scalars().all()
    return employeeStatus


# find a status by id
@apiRouter.get("/employee_status/{statusId}", response_model=HippoEmployeeStatusRead, dependencies=[Depends(get_current_active_user)],)
async def get_status(statusId: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoEmployeeStatus).where(HippoEmployeeStatus.id == statusId))
    status = result.scalar_one_or_none()
    if not status:
        raise HTTPException(status_code=404, detail="Employee status not found")
    return status
