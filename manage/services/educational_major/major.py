

from manage.models import HippoEducationalMajor, HippoEntityMap
from manage.services.educational_major.schemas import HippoEducationalMajorRead, HippoEducationalMajorCreate, HippoEducationalMajorUpdate
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

# Get all educational_majors
@apiRouter.get("/educational_majors/", response_model=list[HippoEducationalMajorRead], dependencies=[Depends(get_current_active_user)],)
async def get_educational_majors(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoEducationalMajor).order_by(HippoEducationalMajor.name))
    educational_majors = result.scalars().all()
    return educational_majors


# find a Educational_major by id
@apiRouter.get("/educational_majors/{educational_major_id}", response_model=HippoEducationalMajorRead, dependencies=[Depends(get_current_active_user)],)
async def get_Educational_major(educational_major_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoEducationalMajor).where(HippoEducationalMajor.id == educational_major_id))
    Educational_major = result.scalar_one_or_none()
    if not Educational_major:
        raise HTTPException(status_code=404, detail="Educational_major not found")
    return Educational_major

@apiRouter.post("/educational_majors/", response_model=HippoEducationalMajorRead, dependencies=[Depends(get_current_active_user)])
async def create_Educational_major(
    Educational_major:HippoEducationalMajorCreate,
    session: AsyncSession = Depends(get_session),
):
    Educational_major_data = Educational_major.dict()  # get dict from pydantic model
    Educational_major_data['id'] = f"educational_major|{Educational_major.name}"
    
    new_Educational_major = HippoEducationalMajor(**Educational_major_data)
    session.add(new_Educational_major)
    await session.commit()
    await session.refresh(new_Educational_major)
    return new_Educational_major



# --- new BULK endpoint ---
@apiRouter.post(
    "/educational_majors/import",
    response_model=list[HippoEducationalMajorRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_user)]
)
async def bulk_create_classifications(
    majorTypes: list[HippoEducationalMajorCreate],
    session: AsyncSession = Depends(get_session),
):
    if not majorTypes:
        raise HTTPException(status_code=400, detail="Empty payload.")

    # Normalize payload -> list of dicts
    maxNumber = await entity_map.getMaxNumber("educational_major", session)
    maxNumber = maxNumber + 1

    rows = []
    majorId = None
    for item in majorTypes:
        try:
            data = item.model_dump()
        except AttributeError:
            data = item.dict()

        # generate id the same way as single-create
        majorId = f"educational_major|{maxNumber}"
        data["id"] = majorId
        rows.append(data)
        maxNumber += 1

    # Postgres bulk insert with ON CONFLICT DO NOTHING + RETURNING
    # Choose the unique/PK column for conflict target (id here).
    stmt = (
        pg_insert(HippoEducationalMajor.__table__)
        .values(rows)
        .on_conflict_do_nothing(index_elements=["id"])
        .returning(*HippoEducationalMajor.__table__.c)  # return inserted rows
    )

    result = await session.execute(stmt)
    inserted = result.mappings().all()  # list[Mapping]

    new_entity_map = HippoEntityMap(id= majorId, entity_type="educational_major", max_number=maxNumber)
    session.add(new_entity_map)

    # Commit once for the whole batch
    await session.commit()

    # If some were duplicates, they won’t be returned by RETURNING (do-nothing).
    # We still return what was actually inserted.
    # Convert MappingRow -> dict for Pydantic response_model
    return [dict(row) for row in inserted]


# update an existing Educational_major
@apiRouter.put("/educational_majors/{educational_major_id}", response_model=HippoEducationalMajorRead)
async def update_Educational_major(educational_major_id: str, Educational_major:HippoEducationalMajorUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoEducationalMajor).where(HippoEducationalMajor.id == educational_major_id))
    existing_Educational_major = result.scalar_one_or_none()
    if not existing_Educational_major:
        raise HTTPException(status_code=404, detail="Educational_major not found")
    
    for key, value in Educational_major.dict().items():
        if value is not None:
            setattr(existing_Educational_major, key, value)
    
    await session.commit()
    await session.refresh(existing_Educational_major)
    return existing_Educational_major  

# delete a Educational_major
@apiRouter.delete("/educational_majors/{educational_major_id}")
async def delete_Educational_major(educational_major_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoEducationalMajor).where(HippoEducationalMajor.id == educational_major_id))
    existing_Educational_major = result.scalar_one_or_none()
    if not existing_Educational_major:
        raise HTTPException(status_code=404, detail="Educational_major not found")
    
    await session.delete(existing_Educational_major)
    await session.commit()
    return {"detail": "Educational_major deleted successfully"}


