# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

# ORM models
from manage.models import HippoJobType, HippoEntityMap

# Pydantic schemas (validation + serialization)
from manage.services.job_type.schemas import (
    HippoJobTypeRead,
    HippoJobTypeCreate,
    HippoJobTypeUpdate
)

# Async DB session
from sqlalchemy.ext.asyncio import AsyncSession

# FastAPI utilities
from fastapi import APIRouter, Depends, HTTPException, status

# SQLAlchemy ORM query builder
from sqlalchemy.future import select

# Database session factory
from manage.database import SessionLocal, engine

# Authentication dependency
from endpoints.user_api import get_current_active_user

# PostgreSQL bulk insert utility
from sqlalchemy.dialects.postgresql import insert as pg_insert

# Service managing incremental numbering for entities
from manage.services.entity_map import entity_map


# Create API router
apiRouter = APIRouter()


# ---------------------------------------------------------
# Dependency: Get Async Database Session
# ---------------------------------------------------------
async def get_session() -> AsyncSession:
    """
    Provides an async database session.
    Ensures proper open/close lifecycle handling.
    """
    async with SessionLocal() as session:
        yield session


# =========================================================
# GET ALL JOB TYPES
# =========================================================

@apiRouter.get(
    "/job_types/",
    response_model=list[HippoJobTypeRead],
    dependencies=[Depends(get_current_active_user)],
)
async def get_job_types(session: AsyncSession = Depends(get_session)):
    """
    Retrieve all job types ordered alphabetically by name.

    Example:
    - Permanent
    - Contractual
    - Volunteer
    """
    result = await session.execute(
        select(HippoJobType).order_by(HippoJobType.name)
    )

    job_types = result.scalars().all()
    return job_types


# =========================================================
# GET JOB TYPE BY ID
# =========================================================

@apiRouter.get(
    "/job_types/{job_type_id}",
    response_model=HippoJobTypeRead,
    dependencies=[Depends(get_current_active_user)],
)
async def get_job_type(
    job_type_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieve a specific Job Type by ID.
    Returns 404 if not found.
    """

    result = await session.execute(
        select(HippoJobType).where(
            HippoJobType.id == job_type_id
        )
    )

    job_type = result.scalar_one_or_none()

    if not job_type:
        raise HTTPException(status_code=404, detail="Job type not found")

    return job_type


# =========================================================
# CREATE JOB TYPE
# =========================================================

@apiRouter.post(
    "/job_types/",
    response_model=HippoJobTypeRead,
    dependencies=[Depends(get_current_active_user)]
)
async def create_job_type(
    job_type: HippoJobTypeCreate,
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new Job Type.

    ID format:
        job_type|<name>

    NOTE:
    If names are not unique, you should add a uniqueness check.
    """

    job_type_data = job_type.dict()

    # Generate ID using name
    job_type_data['id'] = f"job_type|{job_type.name}"

    new_job_type = HippoJobType(**job_type_data)

    session.add(new_job_type)
    await session.commit()
    await session.refresh(new_job_type)

    return new_job_type


# =========================================================
# BULK IMPORT JOB TYPES
# =========================================================

@apiRouter.post(
    "/job_types/import",
    response_model=list[HippoJobTypeRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_user)]
)
async def bulk_create_job_types(
    job_types: list[HippoJobTypeCreate],
    session: AsyncSession = Depends(get_session),
):
    """
    Bulk insert job types.

    Logic:
    - Retrieve current max number from entity_map
    - Generate sequential IDs (job_type|<number>)
    - Insert all rows using PostgreSQL ON CONFLICT DO NOTHING
    - Update entity_map with latest max_number
    """

    if not job_types:
        raise HTTPException(status_code=400, detail="Empty payload.")

    # Get next sequence number
    maxNumber = await entity_map.getMaxNumber("job_type", session)
    maxNumber = maxNumber + 1

    rows = []
    classId = None
    entityName = 'job_type'

    # Normalize payload and generate IDs
    for item in job_types:
        try:
            data = item.model_dump()  # Pydantic v2
        except AttributeError:
            data = item.dict()        # Pydantic v1 fallback

        classId = f"{entityName}|{maxNumber}"
        data["id"] = classId

        rows.append(data)
        maxNumber += 1

    # Bulk insert using PostgreSQL-specific statement
    stmt = (
        pg_insert(HippoJobType.__table__)
        .values(rows)
        .on_conflict_do_nothing(index_elements=['id'])  # Skip duplicates
        .returning(*HippoJobType.__table__.c)
    )

    result = await session.execute(stmt)
    inserted = result.mappings().all()

    # Update entity_map with new max number
    new_entity_map = HippoEntityMap(
        id=classId,
        entity_type=entityName,
        max_number=maxNumber
    )

    session.add(new_entity_map)

    # Single commit for whole batch
    await session.commit()

    # Return only inserted records
    return [dict(row) for row in inserted]


# =========================================================
# UPDATE JOB TYPE
# =========================================================

@apiRouter.put(
    "/job_types/{job_type_id}",
    response_model=HippoJobTypeRead
)
async def update_job_type(
    job_type_id: str,
    job_type: HippoJobTypeUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    Update an existing Job Type.

    - Applies partial update (non-null fields only).
    - Returns 404 if not found.
    """

    result = await session.execute(
        select(HippoJobType).where(
            HippoJobType.id == job_type_id
        )
    )

    existing_job_type = result.scalar_one_or_none()

    if not existing_job_type:
        raise HTTPException(status_code=404, detail="Job type not found")

    for key, value in job_type.dict().items():
        if value is not None:
            setattr(existing_job_type, key, value)

    await session.commit()
    await session.refresh(existing_job_type)

    return existing_job_type


# =========================================================
# DELETE JOB TYPE
# =========================================================

@apiRouter.delete("/job_types/{job_type_id}")
async def delete_job_type(
    job_type_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete a Job Type by ID.

    WARNING:
    If referenced in employment records, deletion should be prevented
    or replaced by soft delete.
    """

    result = await session.execute(
        select(HippoJobType).where(
            HippoJobType.id == job_type_id
        )
    )

    existing_job_type = result.scalar_one_or_none()

    if not existing_job_type:
        raise HTTPException(status_code=404, detail="Job type not found")

    await session.delete(existing_job_type)
    await session.commit()

    return {"detail": "Job type deleted successfully"}