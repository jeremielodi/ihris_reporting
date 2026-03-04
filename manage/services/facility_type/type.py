# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

# ORM model
from manage.models import HippoFacilityType

# Pydantic schemas (validation + serialization)
from manage.services.facility_type.schemas import (
    HippoFacilityTypeRead,
    HippoFacilityTypeCreate,
    HippoFacilityTypeUpdate
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
# GET ALL FACILITY TYPES
# =========================================================

@apiRouter.get(
    "/facility_types/",
    response_model=list[HippoFacilityTypeRead],
    dependencies=[Depends(get_current_active_user)],
)
async def get_facility_types(session: AsyncSession = Depends(get_session)):
    """
    Retrieve all facility types ordered alphabetically by name.

    Example:
    - Hospital
    - Health Center
    - Health Post
    - Referral Facility
    """

    result = await session.execute(
        select(HippoFacilityType).order_by(HippoFacilityType.name)
    )

    facility_types = result.scalars().all()
    return facility_types


# =========================================================
# GET FACILITY TYPE BY ID
# =========================================================

@apiRouter.get(
    "/facility_types/{facility_type_id}",
    response_model=HippoFacilityTypeRead,
    dependencies=[Depends(get_current_active_user)],
)
async def get_facility_type(
    facility_type_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieve a specific facility type by ID.

    Returns:
    - 404 if the facility type does not exist.
    """

    result = await session.execute(
        select(HippoFacilityType).where(
            HippoFacilityType.id == facility_type_id
        )
    )

    facility_type = result.scalar_one_or_none()

    if not facility_type:
        raise HTTPException(status_code=404, detail="Facility type not found")

    return facility_type


# =========================================================
# CREATE FACILITY TYPE
# =========================================================

@apiRouter.post(
    "/facility_types/",
    response_model=HippoFacilityTypeRead,
    dependencies=[Depends(get_current_active_user)]
)
async def create_facility_type(
    facility_type: HippoFacilityTypeCreate,
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new facility type.

    ID format:
        facility_type|<name>

    NOTE:
    Consider validating uniqueness of name before insert.
    """

    facility_type_data = facility_type.dict()

    # Generate ID based on name
    facility_type_data['id'] = f"facility_type|{facility_type.name}"

    new_facility_type = HippoFacilityType(**facility_type_data)

    session.add(new_facility_type)
    await session.commit()
    await session.refresh(new_facility_type)

    return new_facility_type


# =========================================================
# UPDATE FACILITY TYPE
# =========================================================

@apiRouter.put(
    "/facility_types/{facility_type_id}",
    response_model=HippoFacilityTypeRead
)
async def update_facility_type(
    facility_type_id: str,
    facility_type: HippoFacilityTypeUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    Update an existing facility type.

    - Only non-null fields are updated.
    - Returns 404 if not found.
    """

    result = await session.execute(
        select(HippoFacilityType).where(
            HippoFacilityType.id == facility_type_id
        )
    )

    existing_facility_type = result.scalar_one_or_none()

    if not existing_facility_type:
        raise HTTPException(status_code=404, detail="Facility type not found")

    for key, value in facility_type.dict().items():
        if value is not None:
            setattr(existing_facility_type, key, value)

    await session.commit()
    await session.refresh(existing_facility_type)

    return existing_facility_type


# =========================================================
# DELETE FACILITY TYPE
# =========================================================

@apiRouter.delete("/facility_types/{facility_type_id}")
async def delete_facility_type(
    facility_type_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete a facility type.

    WARNING:
    If this type is referenced in organization units,
    deletion should be prevented or replaced by soft delete.
    """

    result = await session.execute(
        select(HippoFacilityType).where(
            HippoFacilityType.id == facility_type_id
        )
    )

    existing_facility_type = result.scalar_one_or_none()

    if not existing_facility_type:
        raise HTTPException(status_code=404, detail="Facility type not found")

    await session.delete(existing_facility_type)
    await session.commit()

    return {"detail": "Facility type deleted successfully"}