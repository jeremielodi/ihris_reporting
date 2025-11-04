from manage.models import HippoGender
from manage.services.gender.schemas import HippoGenderRead
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from manage.database import SessionLocal
from endpoints.user_api import get_current_active_user


apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

# Get all Genders
@apiRouter.get("/genders/", response_model=list[HippoGenderRead])
async def get_genders(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoGender))
    Genders = result.scalars().all()
    return Genders


# find a Gender by id
@apiRouter.get("/genders/{genderId}", response_model=HippoGenderRead, dependencies=[Depends(get_current_active_user)],)
async def get_gender(genderId: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoGender).where(HippoGender.id == genderId))
    Gender = result.scalar_one_or_none()
    if not Gender:
        raise HTTPException(status_code=404, detail="Gender not found")
    return Gender
