# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

# ORM model
from manage.models import HippoIdentificationType

# Pydantic schemas (validation + serialization)
from manage.services.identification_type.schemas import (
    HippoIdentificationTypeRead,
    HippoIdentificationTypeCreate,
    HippoIdentificationTypeUpdate
)

# Async database session
from sqlalchemy.ext.asyncio import AsyncSession

# FastAPI utilities
from fastapi import APIRouter, Depends, HTTPException

# SQLAlchemy ORM query builder
from sqlalchemy.future import select

# Database session factory
from manage.database import SessionLocal, engine

# Authentication dependency
from endpoints.user_api import get_current_active_user


# Create API router
apiRouter = APIRouter()


# ---------------------------------------------------------
# Dependency: Get Async Database Session
# ---------------------------------------------------------
async def get_session() -> AsyncSession:
    """
    Provides an async database session.
    Ensures proper lifecycle handling (open/close).
    """
    async with SessionLocal() as session:
        yield session


# =========================================================
# GET ALL IDENTIFICATION TYPES
# =========================================================

@apiRouter.get(
    "/identification_types/",
    response_model=list[HippoIdentificationTypeRead],
    dependencies=[Depends(get_current_active_user)],
)
async def get_identification_types(session: AsyncSession = Depends(get_session)):
    """
    Retrieve all identification types ordered alphabetically by name.

    Example:
    - National ID
    - Passport
    - Driver License
    - Work Permit
    """

    result = await session.execute(
        select(HippoIdentificationType).order_by(HippoIdentificationType.name)
    )

    identification_types = result.scalars().all()
    return identification_types


# =========================================================
# GET IDENTIFICATION TYPE BY ID
# =========================================================

@apiRouter.get(
    "/identification_types/{identification_type_id}",
    response_model=HippoIdentificationTypeRead,
    dependencies=[Depends(get_current_active_user)],
)
async def get_identification_type(
    identification_type_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieve a specific identification type by ID.

    Returns:
    - 404 if not found.
    """

    result = await session.execute(
        select(HippoIdentificationType).where(
            HippoIdentificationType.id == identification_type_id
        )
    )

    identification_type = result.scalar_one_or_none()

    if not identification_type:
        raise HTTPException(status_code=404, detail="Identification type not found")

    return identification_type


# =========================================================
# CREATE IDENTIFICATION TYPE
# =========================================================

@apiRouter.post(
    "/identification_types/",
    response_model=HippoIdentificationTypeRead,
    dependencies=[Depends(get_current_active_user)]
)
async def create_identification_type(
    identification_type: HippoIdentificationTypeCreate,
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new identification type.

    ID format:
        identification_type|<name>

    NOTE:
    Consider validating uniqueness of name before insert.
    """

    identification_type_data = identification_type.model_dump()

    # Generate ID based on name
    identification_type_data['id'] = (
        f"identification_type|{identification_type.name}"
    )

    new_identification_type = HippoIdentificationType(**identification_type_data)

    session.add(new_identification_type)
    await session.commit()
    await session.refresh(new_identification_type)

    return new_identification_type


# =========================================================
# UPDATE IDENTIFICATION TYPE
# =========================================================

@apiRouter.put(
    "/identification_types/{identification_type_id}",
    response_model=HippoIdentificationTypeRead
)
async def update_identification_type(
    identification_type_id: str,
    identification_type: HippoIdentificationTypeUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    Update an existing identification type.

    - Only non-null fields are updated.
    - Returns 404 if not found.
    """

    result = await session.execute(
        select(HippoIdentificationType).where(
            HippoIdentificationType.id == identification_type_id
        )
    )

    existing_identification_type = result.scalar_one_or_none()

    if not existing_identification_type:
        raise HTTPException(status_code=404, detail="Identification type not found")

    for key, value in identification_type.model_dump().items():
        if value is not None:
            setattr(existing_identification_type, key, value)

    await session.commit()
    await session.refresh(existing_identification_type)

    return existing_identification_type


# =========================================================
# DELETE IDENTIFICATION TYPE
# =========================================================

@apiRouter.delete("/identification_types/{identification_type_id}")
async def delete_identification_type(
    identification_type_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete an identification type.

    WARNING:
    If referenced in person_identification records,
    deletion should be prevented or replaced with soft delete.
    """

    result = await session.execute(
        select(HippoIdentificationType).where(
            HippoIdentificationType.id == identification_type_id
        )
    )

    existing_identification_type = result.scalar_one_or_none()

    if not existing_identification_type:
        raise HTTPException(status_code=404, detail="Identification type not found")

    await session.delete(existing_identification_type)
    await session.commit()

    return {"detail": "Identification type deleted successfully"}