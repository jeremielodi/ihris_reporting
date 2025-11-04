

from manage.models import HippoEducationalLevel, HippoEntityMap
from manage.services.educational_level.schemas import HippoEducationalLevelRead, HippoEducationalLevelCreate, HippoEducationalLevelUpdate
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

# Get all educational_levels
@apiRouter.get("/educational_levels/", response_model=list[HippoEducationalLevelRead], dependencies=[Depends(get_current_active_user)],)
async def get_educational_levels(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoEducationalLevel).order_by(HippoEducationalLevel.name))
    educational_levels = result.scalars().all()
    return educational_levels


# find a Educational_level by id
@apiRouter.get("/educational_levels/{educational_level_id}", response_model=HippoEducationalLevelRead, dependencies=[Depends(get_current_active_user)],)
async def get_Educational_level(educational_level_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoEducationalLevel).where(HippoEducationalLevel.id == educational_level_id))
    Educational_level = result.scalar_one_or_none()
    if not Educational_level:
        raise HTTPException(status_code=404, detail="Educational_level not found")
    return Educational_level

@apiRouter.post("/educational_levels/", response_model=HippoEducationalLevelRead, dependencies=[Depends(get_current_active_user)])
async def create_Educational_level(
    Educational_level:HippoEducationalLevelCreate,
    session: AsyncSession = Depends(get_session),
):
    Educational_level_data = Educational_level.dict()  # get dict from pydantic model
    Educational_level_data['id'] = f"educational_level|{Educational_level.name}"
    
    new_Educational_level = HippoEducationalLevel(**Educational_level_data)
    session.add(new_Educational_level)
    await session.commit()
    await session.refresh(new_Educational_level)
    return new_Educational_level




# --- new BULK endpoint ---
@apiRouter.post(
    "/educational_levels/import",
    response_model=list[HippoEducationalLevelRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_user)]
)
async def bulk_create_classifications(
    educationLevels: list[HippoEducationalLevelCreate],
    session: AsyncSession = Depends(get_session),
):
    if not educationLevels:
        raise HTTPException(status_code=400, detail="Empty payload.")

    # Normalize payload -> list of dicts
    maxNumber = await entity_map.getMaxNumber("education_level", session)
    maxNumber = maxNumber + 1

    rows = []
    gradeId = None
    for item in educationLevels:
        try:
            data = item.model_dump()
        except AttributeError:
            data = item.dict()

        # generate id the same way as single-create
        gradeId = f"education_level|{maxNumber}"
        data["id"] = gradeId
        rows.append(data)
        maxNumber += 1

    # Postgres bulk insert with ON CONFLICT DO NOTHING + RETURNING
    # Choose the unique/PK column for conflict target (id here).
    stmt = (
        pg_insert(HippoEducationalLevel.__table__)
        .values(rows)
        .on_conflict_do_nothing(index_elements=["id"])
        .returning(*HippoEducationalLevel.__table__.c)  # return inserted rows
    )

    result = await session.execute(stmt)
    inserted = result.mappings().all()  # list[Mapping]

    new_entity_map = HippoEntityMap(id=  gradeId, entity_type="education_level", max_number=maxNumber)
    session.add(new_entity_map)

    # Commit once for the whole batch
    await session.commit()

    # If some were duplicates, they won’t be returned by RETURNING (do-nothing).
    # We still return what was actually inserted.
    # Convert MappingRow -> dict for Pydantic response_model
    return [dict(row) for row in inserted]

# update an existing Educational_level
@apiRouter.put("/educational_levels/{educational_level_id}", response_model=HippoEducationalLevelRead)
async def update_Educational_level(educational_level_id: str, Educational_level:HippoEducationalLevelUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoEducationalLevel).where(HippoEducationalLevel.id == educational_level_id))
    existing_Educational_level = result.scalar_one_or_none()
    if not existing_Educational_level:
        raise HTTPException(status_code=404, detail="Educational_level not found")
    
    for key, value in Educational_level.dict().items():
        if value is not None:
            setattr(existing_Educational_level, key, value)
    
    await session.commit()
    await session.refresh(existing_Educational_level)
    return existing_Educational_level  

# delete a Educational_level
@apiRouter.delete("/educational_levels/{educational_level_id}")
async def delete_Educational_level(educational_level_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoEducationalLevel).where(HippoEducationalLevel.id == educational_level_id))
    existing_Educational_level = result.scalar_one_or_none()
    if not existing_Educational_level:
        raise HTTPException(status_code=404, detail="Educational_level not found")
    
    await session.delete(existing_Educational_level)
    await session.commit()
    return {"detail": "Educational_level deleted successfully"}


