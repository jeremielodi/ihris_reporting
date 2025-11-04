from manage.models import HippoCountry
from manage.services.country.schemas import HippoCountryRead
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from manage.database import SessionLocal
from endpoints.user_api import get_current_active_user


apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

# Get all Countrys
@apiRouter.get("/countries/", response_model=list[HippoCountryRead])
async def get_Countrys(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoCountry))
    Countrys = result.scalars().all()
    return Countrys


# find a Country by id
@apiRouter.get("/countries/{CountryId}", response_model=HippoCountryRead, dependencies=[Depends(get_current_active_user)],)
async def get_Country(CountryId: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoCountry).where(HippoCountry.id == CountryId))
    Country = result.scalar_one_or_none()
    if not Country:
        raise HTTPException(status_code=404, detail="Country not found")
    return Country
