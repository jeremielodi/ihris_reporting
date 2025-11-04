

from manage.models import HippoPersonTimesheet
from manage.services.timesheet.schemas import HippoTimesheetRead, HippoTimesheetCreate, HippoTimesheetUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user
from manage.services.entity_map import entity_map
from sqlalchemy import text
from manage.models import  HippoEntityMap

apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

# Get all person_timesheets
@apiRouter.get("/timesheets/", response_model=list[HippoTimesheetRead], dependencies=[Depends(get_current_active_user)],)
async def get_person_timesheets(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoPersonTimesheet))
    person_timesheets = result.scalars().all()
    return person_timesheets



# Get all person_timesheets
@apiRouter.get("/timesheets/person/{personId}", response_model=list[HippoTimesheetRead], dependencies=[Depends(get_current_active_user)],)
async def get_person_timesheets(personId:str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoPersonTimesheet).where(HippoPersonTimesheet.person_id == personId).order_by(HippoPersonTimesheet.month_year.desc()))
    person_timesheets = result.scalars().all()
    return person_timesheets



# find a Person_Timesheet by id
@apiRouter.get("/timesheets/{person_timesheet_id}", response_model=HippoTimesheetRead, dependencies=[Depends(get_current_active_user)],)
async def get_Person_Timesheet(person_timesheet_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoPersonTimesheet).where(HippoPersonTimesheet.id == person_timesheet_id))
    Person_Timesheet = result.scalar_one_or_none()
    if not Person_Timesheet:
        raise HTTPException(status_code=404, detail="Person_Timesheet not found")
    return Person_Timesheet


@apiRouter.post("/timesheets/", response_model=HippoTimesheetRead, dependencies=[Depends(get_current_active_user)])
async def create_Person_Timesheet(
    timesheet:HippoTimesheetCreate,
    session: AsyncSession = Depends(get_session),
):
    print(timesheet)
    result = await session.execute(
    text("""
        SELECT t.id, t.person_id, t.year, t.month
        FROM (
            SELECT
                id,
                person_id,
                EXTRACT(YEAR FROM month_year)::int AS year,
                EXTRACT(MONTH FROM month_year)::int AS month
            FROM hippo_person_timesheet
        ) AS t
        WHERE t.person_id = :person_id
          AND t.year = :year
          AND t.month = :month
    """),
    {
        "person_id": timesheet.person_id,
        "year": timesheet.month_year.year,
        "month": timesheet.month_year.month,
    }
    )
    existing_Person_Timesheet = result.scalar_one_or_none()
    if  existing_Person_Timesheet:
        raise HTTPException(status_code=409, detail=f"A Timesheet for '{timesheet.person_id}' exists for  this month")
    

    maxNumber = await entity_map.getMaxNumber("timesheet", session)
    maxNumber = maxNumber + 1

    Person_Timesheet_data = timesheet.dict()  # get dict from pydantic model
    Person_Timesheet_data['id'] = f"person_timesheet|{maxNumber}"
    
    new_Person_Timesheet = HippoPersonTimesheet(**Person_Timesheet_data)
    session.add(new_Person_Timesheet)

    new_entity_map = HippoEntityMap(id= Person_Timesheet_data['id'], entity_type="timesheet", max_number=maxNumber)
    session.add(new_entity_map)

    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise

    await session.refresh(new_Person_Timesheet)
    return new_Person_Timesheet

# update an existing Person_Timesheet
@apiRouter.put("/timesheets/{person_timesheet_id}", response_model=HippoTimesheetRead)
async def update_Person_Timesheet(person_timesheet_id: str, Person_Timesheet:HippoTimesheetUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoPersonTimesheet).where(HippoPersonTimesheet.id == person_timesheet_id))
    existing_Person_Timesheet = result.scalar_one_or_none()
    if not existing_Person_Timesheet:
        raise HTTPException(status_code=404, detail="Person_Timesheet not found")
    
    for key, value in Person_Timesheet.dict().items():
        if value is not None:
            setattr(existing_Person_Timesheet, key, value)
    
    await session.commit()
    await session.refresh(existing_Person_Timesheet)
    return existing_Person_Timesheet  

# delete a Person_Timesheet
@apiRouter.delete("/timesheets/{person_timesheet_id}")
async def delete_Person_Timesheet(person_timesheet_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoPersonTimesheet).where(HippoPersonTimesheet.id == person_timesheet_id))
    existing_Person_Timesheet = result.scalar_one_or_none()
    if not existing_Person_Timesheet:
        raise HTTPException(status_code=404, detail="Person_Timesheet not found")
    
    await session.delete(existing_Person_Timesheet)
    await session.commit()
    return {"detail": "Person_Timesheet deleted successfully"}


