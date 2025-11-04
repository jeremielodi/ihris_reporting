from manage.models import HippoSalaryGrade, HippoEntityMap
from manage.services.grade.schemas import HippoGradeRead, HippoGradeCreate, HippoGradeUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user

from sqlalchemy.dialects.postgresql import insert as pg_insert
from manage.services.entity_map import entity_map

apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

# Get all grades
@apiRouter.get("/grades/", response_model=list[HippoGradeRead], dependencies=[Depends(get_current_active_user)],)
async def get_grades(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoSalaryGrade).order_by(HippoSalaryGrade.name))
    grades = result.scalars().all()
    return grades


# find a Grade by id
@apiRouter.get("/grades/{grade_id}", response_model=HippoGradeRead, dependencies=[Depends(get_current_active_user)],)
async def get_Grade(grade_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoSalaryGrade).where(HippoSalaryGrade.id == grade_id))
    Grade = result.scalar_one_or_none()
    if not Grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    return Grade

@apiRouter.post("/grades/", response_model=HippoGradeRead, dependencies=[Depends(get_current_active_user)])
async def create_Grade(
    Grade: HippoGradeCreate,
    session: AsyncSession = Depends(get_session),
):
    Grade_data = Grade.dict()  # get dict from pydantic model
    Grade_data['id'] = f"salary_grade|{Grade.name}"
    
    new_Grade = HippoSalaryGrade(**Grade_data)
    session.add(new_Grade)
    await session.commit()
    await session.refresh(new_Grade)
    return new_Grade



# --- new BULK endpoint ---
@apiRouter.post(
    "/grades/import",
    response_model=list[HippoGradeRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_user)]
)
async def bulk_create_classifications(
    grades: list[HippoGradeCreate],
    session: AsyncSession = Depends(get_session),
):
    if not grades:
        raise HTTPException(status_code=400, detail="Empty payload.")

    # Normalize payload -> list of dicts
    maxNumber = await entity_map.getMaxNumber("salary_grade", session)
    maxNumber = maxNumber + 1

    rows = []
    gradeId = None
    for item in grades:
        try:
            data = item.model_dump()
        except AttributeError:
            data = item.dict()

        # generate id the same way as single-create
        gradeId = f"salary_grade|{maxNumber}"
        data["id"] = gradeId
        rows.append(data)
        maxNumber += 1

    # Postgres bulk insert with ON CONFLICT DO NOTHING + RETURNING
    # Choose the unique/PK column for conflict target (id here).
    stmt = (
        pg_insert(HippoSalaryGrade.__table__)
        .values(rows)
        .on_conflict_do_nothing(index_elements=["id"])
        .returning(*HippoSalaryGrade.__table__.c)  # return inserted rows
    )

    result = await session.execute(stmt)
    inserted = result.mappings().all()  # list[Mapping]

    new_entity_map = HippoEntityMap(id=  gradeId, entity_type="salary_grade", max_number=maxNumber)
    session.add(new_entity_map)

    # Commit once for the whole batch
    await session.commit()

    # If some were duplicates, they won’t be returned by RETURNING (do-nothing).
    # We still return what was actually inserted.
    # Convert MappingRow -> dict for Pydantic response_model
    return [dict(row) for row in inserted]


# update an existing Grade
@apiRouter.put("/grades/{grade_id}", response_model=HippoGradeRead)
async def update_Grade(grade_id: str, Grade: HippoGradeUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoSalaryGrade).where(HippoSalaryGrade.id == grade_id))
    existing_Grade = result.scalar_one_or_none()
    if not existing_Grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    
    for key, value in Grade.dict().items():
        if value is not None:
            setattr(existing_Grade, key, value)
    
    await session.commit()
    await session.refresh(existing_Grade)
    return existing_Grade  

# delete a Grade
@apiRouter.delete("/grades/{grade_id}")
async def delete_Grade(grade_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoSalaryGrade).where(HippoSalaryGrade.id == grade_id))
    existing_Grade = result.scalar_one_or_none()
    if not existing_Grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    
    await session.delete(existing_Grade)
    await session.commit()
    return {"detail": "Grade deleted successfully"}