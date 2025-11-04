from manage.models import HippoClassification, HippoEntityMap
from manage.services.classification.schemas import HippoClassificationRead, HippoClassificationCreate, HippoClassificationUpdate
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

# Get all classifications
@apiRouter.get("/classifications/", response_model=list[HippoClassificationRead], dependencies=[Depends(get_current_active_user)],)
async def get_classifications(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoClassification))
    classifications = result.scalars().all()
    return classifications


# find a Classification by id
@apiRouter.get("/classifications/{Classification_id}", response_model=HippoClassificationRead, dependencies=[Depends(get_current_active_user)],)
async def get_Classification(Classification_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoClassification).where(HippoClassification.id == Classification_id))
    Classification = result.scalar_one_or_none()
    if not Classification:
        raise HTTPException(status_code=404, detail="Classification not found")
    return Classification

@apiRouter.post("/classifications/", response_model=HippoClassificationRead, dependencies=[Depends(get_current_active_user)])
async def create_classification(
    classification: HippoClassificationCreate,
    session: AsyncSession = Depends(get_session),
):
    classification_data = classification.dict()  # get dict from pydantic model
    classification_data['id'] = f"classification|{classification.name}"
    
    new_classification = HippoClassification(**classification_data)
    session.add(new_classification)
    await session.commit()
    await session.refresh(new_classification)
    return new_classification


# --- new BULK endpoint ---
@apiRouter.post(
    "/classifications/import",
    response_model=list[HippoClassificationRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_user)]
)
async def bulk_create_classifications(
    classifications: list[HippoClassificationCreate],
    session: AsyncSession = Depends(get_session),
):
    if not classifications:
        raise HTTPException(status_code=400, detail="Empty payload.")

    # Normalize payload -> list of dicts
    maxNumber = await entity_map.getMaxNumber("classification", session)
    maxNumber = maxNumber + 1

    rows = []
    classId = None
    for item in classifications:
        try:
            data = item.model_dump()
        except AttributeError:
            data = item.dict()

        # generate id the same way as single-create
        classId = f"classification|{maxNumber}"
        data["id"] = classId
        rows.append(data)
        maxNumber += 1

    # Postgres bulk insert with ON CONFLICT DO NOTHING + RETURNING
    # Choose the unique/PK column for conflict target (id here).
    stmt = (
        pg_insert(HippoClassification.__table__)
        .values(rows)
        .on_conflict_do_nothing(index_elements=["id"])
        .returning(*HippoClassification.__table__.c)  # return inserted rows
    )

    result = await session.execute(stmt)
    inserted = result.mappings().all()  # list[Mapping]

    new_entity_map = HippoEntityMap(id=  classId, entity_type="classification", max_number=maxNumber)
    session.add(new_entity_map)

    # Commit once for the whole batch
    await session.commit()

    # If some were duplicates, they won’t be returned by RETURNING (do-nothing).
    # We still return what was actually inserted.
    # Convert MappingRow -> dict for Pydantic response_model
    return [dict(row) for row in inserted]

# update an existing Classification
@apiRouter.put("/classifications/{Classification_id}", response_model=HippoClassificationRead)
async def update_Classification(Classification_id: str, Classification: HippoClassificationUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoClassification).where(HippoClassification.id == Classification_id))
    existing_Classification = result.scalar_one_or_none()
    if not existing_Classification:
        raise HTTPException(status_code=404, detail="Classification not found")
    
    for key, value in Classification.dict().items():
        if (value is not None) and (key != 'created'):
            setattr(existing_Classification, key, value)
    
    await session.commit()
    await session.refresh(existing_Classification)
    return existing_Classification  

# delete a Classification
@apiRouter.delete("/classifications/{Classification_id}")
async def delete_Classification(Classification_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoClassification).where(HippoClassification.id == Classification_id))
    existing_Classification = result.scalar_one_or_none()
    if not existing_Classification:
        raise HTTPException(status_code=404, detail="Classification not found")
    
    await session.delete(existing_Classification)
    await session.commit()
    return {"detail": "Classification deleted successfully"}