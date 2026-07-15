"""
Educational Major API Endpoints
-------------------------------

This module manages CRUD and BULK IMPORT operations for
HippoEducationalMajor.

EducationalMajor represents fields of study or academic
specializations (e.g., Medicine, Nursing, Public Health,
Pharmacy, Laboratory Sciences, etc.).

Includes:
- Standard CRUD operations
- PostgreSQL optimized bulk insert
- EntityMap incremental ID tracking

All endpoints require authenticated active users.
"""

from manage.models import HippoEducationalMajor, HippoEntityMap
from manage.services.educational_major.schemas import (
    HippoEducationalMajorRead,
    HippoEducationalMajorCreate,
    HippoEducationalMajorUpdate
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
# GET ALL EDUCATIONAL MAJORS
# -------------------------------------------------------------------
@apiRouter.get(
    "/educational_majors/",
    response_model=list[HippoEducationalMajorRead],
    dependencies=[Depends(get_current_active_user)],
)
async def get_educational_majors(session: AsyncSession = Depends(get_session)):
    """
    Retrieve all educational majors ordered alphabetically by name.

    Returns:
        List[HippoEducationalMajorRead]
    """
    result = await session.execute(
        select(HippoEducationalMajor)
        .order_by(HippoEducationalMajor.name)
    )
    educational_majors = result.scalars().all()
    return educational_majors


# -------------------------------------------------------------------
# GET EDUCATIONAL MAJOR BY ID
# -------------------------------------------------------------------
@apiRouter.get(
    "/educational_majors/{educational_major_id}",
    response_model=HippoEducationalMajorRead,
    dependencies=[Depends(get_current_active_user)],
)
async def get_Educational_major(
    educational_major_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieve a specific educational major by ID.

    Raises:
        HTTPException(404) if record not found.
    """
    result = await session.execute(
        select(HippoEducationalMajor)
        .where(HippoEducationalMajor.id == educational_major_id)
    )
    Educational_major = result.scalar_one_or_none()

    if not Educational_major:
        raise HTTPException(status_code=404, detail="Educational_major not found")

    return Educational_major


# -------------------------------------------------------------------
# CREATE SINGLE EDUCATIONAL MAJOR
# -------------------------------------------------------------------
@apiRouter.post(
    "/educational_majors/",
    response_model=HippoEducationalMajorRead,
    dependencies=[Depends(get_current_active_user)]
)
async def create_Educational_major(
    Educational_major: HippoEducationalMajorCreate,
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new educational major.

    Process:
        1. Convert Pydantic model to dict.
        2. Generate deterministic ID:
           "educational_major|<name>".
        3. Insert record.
        4. Commit and refresh.

    Returns:
        HippoEducationalMajorRead
    """

    Educational_major_data = Educational_major.model_dump()

    # Generate ID using naming convention
    Educational_major_data['id'] = (
        f"educational_major|{Educational_major.name}"
    )

    new_Educational_major = HippoEducationalMajor(**Educational_major_data)

    session.add(new_Educational_major)
    await session.commit()
    await session.refresh(new_Educational_major)

    return new_Educational_major


# -------------------------------------------------------------------
# BULK IMPORT EDUCATIONAL MAJORS
# -------------------------------------------------------------------
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
    """
    Bulk insert educational majors.

    Features:
        - Efficient PostgreSQL bulk insert
        - ON CONFLICT DO NOTHING (skip duplicates)
        - RETURNING inserted rows only
        - EntityMap tracking for incremental numbering

    Raises:
        HTTPException(400) if payload is empty.

    Returns:
        List[HippoEducationalMajorRead] (newly inserted records only)
    """

    if not majorTypes:
        raise HTTPException(status_code=400, detail="Empty payload.")

    # Retrieve and increment max number for entity
    maxNumber = await entity_map.getMaxNumber("educational_major", session)
    maxNumber = maxNumber + 1

    rows = []
    majorId = None

    # Normalize payload into list of dicts
    for item in majorTypes:
        data = item.model_dump()

        # Generate sequential ID
        majorId = f"educational_major|{maxNumber}"
        data["id"] = majorId

        rows.append(data)
        maxNumber += 1

    # PostgreSQL optimized bulk insert
    stmt = (
        pg_insert(HippoEducationalMajor.__table__)
        .values(rows)
        .on_conflict_do_nothing(index_elements=["id"])
        .returning(*HippoEducationalMajor.__table__.c)
    )

    result = await session.execute(stmt)
    inserted = result.mappings().all()

    # Update entity_map with latest max number
    new_entity_map = HippoEntityMap(
        id=majorId,
        entity_type="educational_major",
        max_number=maxNumber
    )
    session.add(new_entity_map)

    # Commit once for entire batch
    await session.commit()

    # Convert MappingRow to dict for response_model
    return [dict(row) for row in inserted]


# -------------------------------------------------------------------
# UPDATE EDUCATIONAL MAJOR
# -------------------------------------------------------------------
@apiRouter.put(
    "/educational_majors/{educational_major_id}",
    response_model=HippoEducationalMajorRead
)
async def update_Educational_major(
    educational_major_id: str,
    Educational_major: HippoEducationalMajorUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    Update an existing educational major.

    - Updates only provided (non-null) fields.
    - Commits changes and refreshes entity.

    Raises:
        HTTPException(404) if record not found.
    """

    result = await session.execute(
        select(HippoEducationalMajor)
        .where(HippoEducationalMajor.id == educational_major_id)
    )
    existing_Educational_major = result.scalar_one_or_none()

    if not existing_Educational_major:
        raise HTTPException(status_code=404, detail="Educational_major not found")

    # Apply partial update
    for key, value in Educational_major.model_dump().items():
        if value is not None:
            setattr(existing_Educational_major, key, value)

    await session.commit()
    await session.refresh(existing_Educational_major)

    return existing_Educational_major


# -------------------------------------------------------------------
# DELETE EDUCATIONAL MAJOR
# -------------------------------------------------------------------
@apiRouter.delete("/educational_majors/{educational_major_id}")
async def delete_Educational_major(
    educational_major_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete an educational major record.

    Raises:
        HTTPException(404) if record not found.

    Returns:
        dict: Success confirmation message.
    """

    result = await session.execute(
        select(HippoEducationalMajor)
        .where(HippoEducationalMajor.id == educational_major_id)
    )
    existing_Educational_major = result.scalar_one_or_none()

    if not existing_Educational_major:
        raise HTTPException(status_code=404, detail="Educational_major not found")

    await session.delete(existing_Educational_major)
    await session.commit()

    return {"detail": "Educational_major deleted successfully"}