

from manage.models import HippoJobType, HippoEntityMap
from manage.services.job_type.schemas import HippoJobTypeRead, HippoJobTypeCreate, HippoJobTypeUpdate
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

# Get all job_types
@apiRouter.get("/job_types/", response_model=list[HippoJobTypeRead], dependencies=[Depends(get_current_active_user)],)
async def get_job_types(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoJobType).order_by(HippoJobType.name))
    job_types = result.scalars().all()
    return job_types


# find a Job_type by id
@apiRouter.get("/job_types/{job_type_id}", response_model=HippoJobTypeRead, dependencies=[Depends(get_current_active_user)],)
async def get_Job_type(job_type_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoJobType).where(HippoJobType.id == job_type_id))
    Job_type = result.scalar_one_or_none()
    if not Job_type:
        raise HTTPException(status_code=404, detail="Job_type not found")
    return Job_type

@apiRouter.post("/job_types/", response_model=HippoJobTypeRead, dependencies=[Depends(get_current_active_user)])
async def create_Job_type(
    Job_type:HippoJobTypeCreate,
    session: AsyncSession = Depends(get_session),
):
    Job_type_data = Job_type.dict()  # get dict from pydantic model
    Job_type_data['id'] = f"job_type|{Job_type.name}"
    
    new_Job_type = HippoJobType(**Job_type_data)
    session.add(new_Job_type)
    await session.commit()
    await session.refresh(new_Job_type)
    return new_Job_type



# --- new BULK endpoint ---
@apiRouter.post(
    "/job_types/import",
    response_model=list[HippoJobTypeRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_user)]
)
async def bulk_create_classifications(
    job_types: list[HippoJobTypeCreate],
    session: AsyncSession = Depends(get_session),
):
    if not job_types:
        raise HTTPException(status_code=400, detail="Empty payload.")

    # Normalize payload -> list of dicts
    maxNumber = await entity_map.getMaxNumber("job_type", session)
    maxNumber = maxNumber + 1

    rows = []
    classId = None
    entityName = 'job_type'
    for item in job_types:
        try:
            data = item.model_dump()
        except AttributeError:
            data = item.dict()

        # generate id the same way as single-create
        classId = f"{entityName}|{maxNumber}"
        data["id"] = classId
        rows.append(data)
        maxNumber += 1

    # Postgres bulk insert with ON CONFLICT DO NOTHING + RETURNING
    # Choose the unique/PK column for conflict target (id here).
    stmt = (
        pg_insert(HippoJobType.__table__)
        .values(rows)
        .on_conflict_do_nothing(index_elements=['id'])
        .returning(*HippoJobType.__table__.c)  # return inserted rows
    )

    result = await session.execute(stmt)
    inserted = result.mappings().all()  # list[Mapping]

    new_entity_map = HippoEntityMap(id = classId, entity_type = entityName, max_number = maxNumber)
    session.add(new_entity_map)

    # Commit once for the whole batch
    await session.commit()

    # If some were duplicates, they won’t be returned by RETURNING (do-nothing).
    # We still return what was actually inserted.
    # Convert MappingRow -> dict for Pydantic response_model
    return [dict(row) for row in inserted]

# update an existing Job_type
@apiRouter.put("/job_types/{job_type_id}", response_model=HippoJobTypeRead)
async def update_Job_type(job_type_id: str, Job_type:HippoJobTypeUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoJobType).where(HippoJobType.id == job_type_id))
    existing_Job_type = result.scalar_one_or_none()
    if not existing_Job_type:
        raise HTTPException(status_code=404, detail="Job_type not found")
    
    for key, value in Job_type.dict().items():
        if value is not None:
            setattr(existing_Job_type, key, value)
    
    await session.commit()
    await session.refresh(existing_Job_type)
    return existing_Job_type  

# delete a Job_type
@apiRouter.delete("/job_types/{job_type_id}")
async def delete_Job_type(job_type_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoJobType).where(HippoJobType.id == job_type_id))
    existing_Job_type = result.scalar_one_or_none()
    if not existing_Job_type:
        raise HTTPException(status_code=404, detail="Job_type not found")
    
    await session.delete(existing_Job_type)
    await session.commit()
    return {"detail": "Job_type deleted successfully"}


