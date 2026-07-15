"""
Educational Level API Endpoints
-------------------------------

This module manages CRUD and BULK IMPORT operations for
HippoEducationalLevel.

EducationalLevel represents the level of academic attainment
(e.g., Secondary, Diploma, Bachelor, Master, PhD, etc.).

Includes:
- Standard CRUD operations
- PostgreSQL optimized bulk insert
- EntityMap incremental ID tracking

All endpoints require authenticated active users.
"""

from manage.models import HippoEducationalLevel, HippoEntityMap
from manage.services.educational_level.schemas import (
    HippoEducationalLevelRead,
    HippoEducationalLevelCreate,
    HippoEducationalLevelUpdate
)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user
from sqlalchemy.dialects.postgresql import insert as pg_insert
from manage.services.entity_map import entity_map


# Initialize API router
apiRouter = APIRouter()


async def get_session() -> AsyncSession:
    """
    Provides an asynchronous database session.

    - Opens AsyncSession
    - Yields session during request lifecycle
    - Automatically closes after completion
    """
    async with SessionLocal() as session:
        yield session


# -------------------------------------------------------------------
# GET ALL EDUCATIONAL LEVELS
# -------------------------------------------------------------------
@apiRouter.get(
    "/educational_levels/",
    response_model=list[HippoEducationalLevelRead],
    dependencies=[Depends(get_current_active_user)],
)
async def get_educational_levels(session: AsyncSession = Depends(get_session)):
    """
    Retrieve all educational levels ordered alphabetically by name.

    Returns:
        List[HippoEducationalLevelRead]
    """
    result = await session.execute(
        select(HippoEducationalLevel)
        .order_by(HippoEducationalLevel.name)
    )
    educational_levels = result.scalars().all()
    return educational_levels


# -------------------------------------------------------------------
# GET EDUCATIONAL LEVEL BY ID
# -------------------------------------------------------------------
@apiRouter.get(
    "/educational_levels/{educational_level_id}",
    response_model=HippoEducationalLevelRead,
    dependencies=[Depends(get_current_active_user)],
)
async def get_Educational_level(
    educational_level_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieve a specific educational level by ID.

    Raises:
        HTTPException(404) if record not found.
    """
    result = await session.execute(
        select(HippoEducationalLevel)
        .where(HippoEducationalLevel.id == educational_level_id)
    )
    Educational_level = result.scalar_one_or_none()

    if not Educational_level:
        raise HTTPException(status_code=404, detail="Educational_level not found")

    return Educational_level


# -------------------------------------------------------------------
# CREATE SINGLE EDUCATIONAL LEVEL
# -------------------------------------------------------------------
@apiRouter.post(
    "/educational_levels/",
    response_model=HippoEducationalLevelRead,
    dependencies=[Depends(get_current_active_user)]
)
async def create_Educational_level(
    Educational_level: HippoEducationalLevelCreate,
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new educational level.

    Process:
        1. Convert Pydantic model to dict.
        2. Generate deterministic ID:
           "educational_level|<name>".
        3. Insert record.
        4. Commit and refresh.

    Returns:
        HippoEducationalLevelRead
    """

    Educational_level_data = Educational_level.model_dump()

    # Generate ID using naming convention
    Educational_level_data['id'] = (
        f"educational_level|{Educational_level.name}"
    )

    new_Educational_level = HippoEducationalLevel(**Educational_level_data)

    session.add(new_Educational_level)
    await session.commit()
    await session.refresh(new_Educational_level)

    return new_Educational_level


# -------------------------------------------------------------------
# BULK IMPORT EDUCATIONAL LEVELS
# -------------------------------------------------------------------
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
    """
    Bulk insert educational levels.

    Features:
        - Efficient PostgreSQL bulk insert
        - ON CONFLICT DO NOTHING (skip duplicates)
        - RETURNING inserted rows only
        - EntityMap tracking for incremental numbering

    Raises:
        HTTPException(400) if payload is empty.

    Returns:
        List[HippoEducationalLevelRead] (newly inserted records only)
    """

    if not educationLevels:
        raise HTTPException(status_code=400, detail="Empty payload.")

    # Retrieve and increment max number for entity
    maxNumber = await entity_map.getMaxNumber("education_level", session)
    maxNumber = maxNumber + 1

    rows = []
    gradeId = None

    # Normalize payload into list of dicts
    for item in educationLevels:
        data = item.model_dump()

        # Generate sequential ID
        gradeId = f"education_level|{maxNumber}"
        data["id"] = gradeId

        rows.append(data)
        maxNumber += 1

    # PostgreSQL optimized bulk insert
    stmt = (
        pg_insert(HippoEducationalLevel.__table__)
        .values(rows)
        .on_conflict_do_nothing(index_elements=["id"])
        .returning(*HippoEducationalLevel.__table__.c)
    )

    result = await session.execute(stmt)
    inserted = result.mappings().all()

    # Update entity_map with latest max number
    new_entity_map = HippoEntityMap(
        id=gradeId,
        entity_type="education_level",
        max_number=maxNumber
    )
    session.add(new_entity_map)

    # Commit once for entire batch
    await session.commit()

    # Convert MappingRow to dict for response_model
    return [dict(row) for row in inserted]


# -------------------------------------------------------------------
# UPDATE EDUCATIONAL LEVEL
# -------------------------------------------------------------------
@apiRouter.put(
    "/educational_levels/{educational_level_id}",
    response_model=HippoEducationalLevelRead
)
async def update_Educational_level(
    educational_level_id: str,
    Educational_level: HippoEducationalLevelUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    Update an existing educational level.

    - Updates only provided (non-null) fields.
    - Commits changes and refreshes entity.

    Raises:
        HTTPException(404) if record not found.
    """

    result = await session.execute(
        select(HippoEducationalLevel)
        .where(HippoEducationalLevel.id == educational_level_id)
    )
    existing_Educational_level = result.scalar_one_or_none()

    if not existing_Educational_level:
        raise HTTPException(status_code=404, detail="Educational_level not found")

    # Apply partial update
    for key, value in Educational_level.model_dump().items():
        if value is not None:
            setattr(existing_Educational_level, key, value)

    await session.commit()
    await session.refresh(existing_Educational_level)

    return existing_Educational_level


# -------------------------------------------------------------------
# DELETE EDUCATIONAL LEVEL
# -------------------------------------------------------------------
@apiRouter.delete("/educational_levels/{educational_level_id}")
async def delete_Educational_level(
    educational_level_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete an educational level record.

    Raises:
        HTTPException(404) if record not found.

    Returns:
        dict: Success confirmation message.
    """

    result = await session.execute(
        select(HippoEducationalLevel)
        .where(HippoEducationalLevel.id == educational_level_id)
    )
    existing_Educational_level = result.scalar_one_or_none()

    if not existing_Educational_level:
        raise HTTPException(status_code=404, detail="Educational_level not found")

    await session.delete(existing_Educational_level)
    await session.commit()

    return {"detail": "Educational_level deleted successfully"}