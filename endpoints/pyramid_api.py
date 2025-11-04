from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from manage.database import SessionLocal
from manage.models import HippoDistrict as District, HippoCounty as County, HippoHealthArea as HealthArea, HippoFacility as Facility
router = APIRouter(prefix="/pyramid")


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


@router.get('/district/{country_id}')
async def district(country_id: str, filter: int = 1, db: AsyncSession = Depends(get_db)):
    if filter == 1:
        stmt = select(District).where(
            District.i2ce_hidden == 0,
            District.id.in_([
                'district|702', 'district|748', 'district|752', 'district|750',
                'district|812', 'district|703', 'district|816', 'district|757',
                'district|805', 'district|806', 'district|807', 'district|813'
            ])
        )
    else:
        stmt = select(District).where(District.i2ce_hidden == 0)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get('/county/{district_id}')
async def county(district_id: str, db: AsyncSession = Depends(get_db)):
    print(f"Fetching counties for district: {district_id}")
    stmt = select(County).where(
        County.i2ce_hidden == 0,
        County.parent == district_id
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get('/health_area/{county_id}')
async def Health_area(county_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(HealthArea).where(
        HealthArea.i2ce_hidden == 0,
        HealthArea.county == county_id
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get('/facility/{health_area_id}')
async def facilities(health_area_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Facility).where(
        Facility.i2ce_hidden == 0,
        Facility.location == health_area_id
    )
    result = await db.execute(stmt)
    return result.scalars().all()
