# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

# Base model (if needed for metadata) and ORM model
from manage.models import Base, HippoSpeciality

# Pydantic schemas (validation + serialization)
from manage.services.speciality.schemas import (
    HippoSpecialityRead,
    HippoSpecialityCreate,
    HippoSpecialityUpdate
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
# GET ALL SPECIALITIES
# =========================================================

@apiRouter.get(
    "/specialities/",
    response_model=list[HippoSpecialityRead],
    dependencies=[Depends(get_current_active_user)],
)
async def get_specialities(session: AsyncSession = Depends(get_session)):
    """
    Retrieve all specialities ordered alphabetically by name.

    Example:
    - Cardiology
    - Dermatology
    - Neurology
    - Pediatrics
    """

    result = await session.execute(
        select(HippoSpeciality).order_by(HippoSpeciality.name)
    )

    specialities = result.scalars().all()
    return specialities

# =========================================================
# GET SPECIALITY BY ID
# =========================================================

@apiRouter.get(
    "/specialities/{speciality_id}",
    response_model=HippoSpecialityRead,
    dependencies=[Depends(get_current_active_user)],
)
async def get_speciality(speciality_id: str, session: AsyncSession = Depends(get_session)):
    """
    Retrieve a specific speciality by ID.

    Returns:
    - 404 if the speciality does not exist.
    """

    result = await session.execute(
        select(HippoSpeciality).where(
            HippoSpeciality.id == speciality_id
        )
    )

    speciality = result.scalar_one_or_none()

    if not speciality:
        raise HTTPException(status_code=404, detail="Speciality not found")

    return speciality

# =========================================================
# CREATE SPECIALITY
# =========================================================

@apiRouter.post(
    "/specialities/",
    response_model=HippoSpecialityRead,
    dependencies=[Depends(get_current_active_user)],
)
async def create_speciality(
    speciality: HippoSpecialityCreate,
    session: AsyncSession = Depends(get_session)
):
    """
    Create a new speciality.

    ID format:
        speciality|<name>

    NOTE:
    Consider validating uniqueness of name before insertion.
    """

    speciality_data = speciality.dict()
    # Generate ID based on speciality name
    speciality_data['id'] = f"speciality|{speciality.name}"

    new_speciality = HippoSpeciality(**speciality_data)

    session.add(new_speciality)
    await session.commit()
    await session.refresh(new_speciality)

    return new_speciality

# =========================================================
# UPDATE SPECIALITY
# =========================================================

@apiRouter.put(
    "/specialities/{speciality_id}",
    response_model=HippoSpecialityRead,
    dependencies=[Depends(get_current_active_user)],
)
async def update_speciality(
    speciality_id: str,
    speciality: HippoSpecialityUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    Update an existing speciality.

    - Returns 404 if not found.
    - Updates provided fields.
    """

    result = await session.execute(
        select(HippoSpeciality).where(
            HippoSpeciality.id == speciality_id
        )
    )

    existing_speciality = result.scalar_one_or_none()

    if not existing_speciality:
        raise HTTPException(status_code=404, detail="Speciality not found")

    # Update all fields (consider using exclude_unset=True for partial updates)
    for key, value in speciality.dict().items():
        if value is not None:
            setattr(existing_speciality, key, value)

    await session.commit()
    await session.refresh(existing_speciality)

    return existing_speciality

# =========================================================
# DELETE SPECIALITY
# =========================================================

@apiRouter.delete(
    "/specialities/{speciality_id}",
    dependencies=[Depends(get_current_active_user)],
)
async def delete_speciality(
    speciality_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete a speciality.

    WARNING:
    If speciality is referenced in hippo_person or other tables,
    deletion should be prevented or replaced with soft delete.
    """

    result = await session.execute(
        select(HippoSpeciality).where(
            HippoSpeciality.id == speciality_id
        )
    )

    existing_speciality = result.scalar_one_or_none()

    if not existing_speciality:
        raise HTTPException(status_code=404, detail="Speciality not found")

    await session.delete(existing_speciality)
    await session.commit()

    return {"detail": "Speciality deleted successfully"}