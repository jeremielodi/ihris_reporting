# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

# ORM models
from manage.models import HippoClassification, HippoEntityMap

# Pydantic schemas (request & response validation)
from manage.services.classification.schemas import (
    HippoClassificationRead,
    HippoClassificationCreate,
    HippoClassificationUpdate
)

# Async database session
from sqlalchemy.ext.asyncio import AsyncSession

# FastAPI utilities
from fastapi import APIRouter, Depends, HTTPException, status

# SQLAlchemy query builder
from sqlalchemy.future import select

# Database session factory
from manage.database import SessionLocal, engine

# Authentication dependency
from endpoints.user_api import get_current_active_user

# PostgreSQL-specific insert (for bulk insert with conflict handling)
from sqlalchemy.dialects.postgresql import insert as pg_insert

# Service to manage incremental entity numbering
from manage.services.entity_map import entity_map


# Create API router
apiRouter = APIRouter()


# ---------------------------------------------------------
# Dependency: Get Async DB Session
# ---------------------------------------------------------
async def get_session() -> AsyncSession:
    """
    Provides an async database session to endpoints.
    Ensures proper session lifecycle management.
    """
    async with SessionLocal() as session:
        yield session


# ---------------------------------------------------------
# GET ALL CLASSIFICATIONS
# ---------------------------------------------------------
@apiRouter.get(
    "/classifications/",
    response_model=list[HippoClassificationRead],
    dependencies=[Depends(get_current_active_user)],
)
async def get_classifications(session: AsyncSession = Depends(get_session)):
    """
    Retrieve all classifications.
    Requires authenticated user.
    """
    result = await session.execute(select(HippoClassification))
    classifications = result.scalars().all()
    return classifications


# ---------------------------------------------------------
# GET CLASSIFICATION BY ID
# ---------------------------------------------------------
@apiRouter.get(
    "/classifications/{Classification_id}",
    response_model=HippoClassificationRead,
    dependencies=[Depends(get_current_active_user)],
)
async def get_Classification(
    Classification_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieve a single Classification by its ID.
    Returns 404 if not found.
    """
    result = await session.execute(
        select(HippoClassification).where(
            HippoClassification.id == Classification_id
        )
    )

    Classification = result.scalar_one_or_none()

    if not Classification:
        raise HTTPException(
            status_code=404,
            detail="Classification not found"
        )

    return Classification


# ---------------------------------------------------------
# CREATE SINGLE CLASSIFICATION
# ---------------------------------------------------------
@apiRouter.post(
    "/classifications/",
    response_model=HippoClassificationRead,
    dependencies=[Depends(get_current_active_user)]
)
async def create_classification(
    classification: HippoClassificationCreate,
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new Classification.
    ID format: 'classification|<classification.name>'
    """

    # Convert Pydantic model to dictionary
    classification_data = classification.model_dump()

    # Generate custom ID
    classification_data['id'] = f"classification|{classification.name}"

    # Create ORM instance
    new_classification = HippoClassification(**classification_data)

    # Persist to database
    session.add(new_classification)
    await session.commit()
    await session.refresh(new_classification)

    return new_classification


# ---------------------------------------------------------
# BULK IMPORT CLASSIFICATIONS
# ---------------------------------------------------------
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
    """
    Bulk insert classifications.

    - Automatically generates sequential IDs using entity_map.
    - Uses PostgreSQL ON CONFLICT DO NOTHING to ignore duplicates.
    - Returns only successfully inserted records.
    """

    # Validate payload
    if not classifications:
        raise HTTPException(status_code=400, detail="Empty payload.")

    # Retrieve current max number for classification entity
    maxNumber = await entity_map.getMaxNumber("classification", session)
    maxNumber = maxNumber + 1

    rows = []
    classId = None

    # Prepare rows for bulk insertion
    for item in classifications:
        data = item.model_dump()

        # Generate sequential ID
        classId = f"classification|{maxNumber}"
        data["id"] = classId

        rows.append(data)
        maxNumber += 1

    # PostgreSQL bulk insert with conflict handling
    stmt = (
        pg_insert(HippoClassification.__table__)
        .values(rows)
        .on_conflict_do_nothing(index_elements=["id"])  # Ignore duplicates
        .returning(*HippoClassification.__table__.c)    # Return inserted rows
    )

    result = await session.execute(stmt)
    inserted = result.mappings().all()

    # Update entity_map table with latest max number
    new_entity_map = HippoEntityMap(
        id=classId,
        entity_type="classification",
        max_number=maxNumber
    )
    session.add(new_entity_map)

    # Commit transaction once for full batch
    await session.commit()

    # Return inserted records only
    return [dict(row) for row in inserted]


# ---------------------------------------------------------
# UPDATE CLASSIFICATION
# ---------------------------------------------------------
@apiRouter.put(
    "/classifications/{Classification_id}",
    response_model=HippoClassificationRead
)
async def update_Classification(
    Classification_id: str,
    Classification: HippoClassificationUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    Update an existing Classification.

    - Only non-null fields are updated.
    - 'created' field is protected and cannot be modified.
    - Returns 404 if record does not exist.
    """

    result = await session.execute(
        select(HippoClassification).where(
            HippoClassification.id == Classification_id
        )
    )

    existing_Classification = result.scalar_one_or_none()

    if not existing_Classification:
        raise HTTPException(
            status_code=404,
            detail="Classification not found"
        )

    # Update fields dynamically (excluding protected fields)
    for key, value in Classification.model_dump().items():
        if (value is not None) and (key != 'created'):
            setattr(existing_Classification, key, value)

    await session.commit()
    await session.refresh(existing_Classification)

    return existing_Classification


# ---------------------------------------------------------
# DELETE CLASSIFICATION
# ---------------------------------------------------------
@apiRouter.delete("/classifications/{Classification_id}")
async def delete_Classification(
    Classification_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete a Classification by ID.
    Returns 404 if not found.
    """

    result = await session.execute(
        select(HippoClassification).where(
            HippoClassification.id == Classification_id
        )
    )

    existing_Classification = result.scalar_one_or_none()

    if not existing_Classification:
        raise HTTPException(
            status_code=404,
            detail="Classification not found"
        )

    await session.delete(existing_Classification)
    await session.commit()

    return {"detail": "Classification deleted successfully"}