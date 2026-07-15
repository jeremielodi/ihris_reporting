# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

# ORM model
from manage.models import HippoContactType

# Pydantic schemas (validation + serialization)
from manage.services.contact_type.schemas import (
    HippoContactTypeRead,
    HippoContactTypeCreate,
    HippoContactTypeUpdate
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
# GET ALL CONTACT TYPES
# =========================================================

@apiRouter.get(
    "/contact_types/",
    response_model=list[HippoContactTypeRead],
    dependencies=[Depends(get_current_active_user)],
)
async def get_contact_types(session: AsyncSession = Depends(get_session)):
    """
    Retrieve all contact types ordered alphabetically by name.

    Example:
    - Email
    - Phone
    - Emergency Contact
    - Fax
    """

    result = await session.execute(
        select(HippoContactType).order_by(HippoContactType.name)
    )

    contact_types = result.scalars().all()
    return contact_types


# =========================================================
# GET CONTACT TYPE BY ID
# =========================================================

@apiRouter.get(
    "/contact_types/{contact_type_id}",
    response_model=HippoContactTypeRead,
    dependencies=[Depends(get_current_active_user)],
)
async def get_contact_type(
    contact_type_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieve a specific contact type by ID.

    Returns:
    - 404 if not found.
    """

    result = await session.execute(
        select(HippoContactType).where(
            HippoContactType.id == contact_type_id
        )
    )

    contact_type = result.scalar_one_or_none()

    if not contact_type:
        raise HTTPException(status_code=404, detail="Contact type not found")

    return contact_type


# =========================================================
# CREATE CONTACT TYPE
# =========================================================

@apiRouter.post(
    "/contact_types/",
    response_model=HippoContactTypeRead,
    dependencies=[Depends(get_current_active_user)]
)
async def create_contact_type(
    contact_type: HippoContactTypeCreate,
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new contact type.

    ID format:
        contact_type|<name>

    NOTE:
    Consider adding uniqueness validation on name before insert.
    """

    contact_type_data = contact_type.model_dump()

    # Generate ID based on name
    contact_type_data['id'] = f"contact_type|{contact_type.name}"

    new_contact_type = HippoContactType(**contact_type_data)

    session.add(new_contact_type)
    await session.commit()
    await session.refresh(new_contact_type)

    return new_contact_type


# =========================================================
# UPDATE CONTACT TYPE
# =========================================================

@apiRouter.put(
    "/contact_types/{contact_type_id}",
    response_model=HippoContactTypeRead
)
async def update_contact_type(
    contact_type_id: str,
    contact_type: HippoContactTypeUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    Update an existing contact type.

    - Only non-null fields are updated.
    - Returns 404 if not found.
    """

    result = await session.execute(
        select(HippoContactType).where(
            HippoContactType.id == contact_type_id
        )
    )

    existing_contact_type = result.scalar_one_or_none()

    if not existing_contact_type:
        raise HTTPException(status_code=404, detail="Contact type not found")

    for key, value in contact_type.model_dump().items():
        if value is not None:
            setattr(existing_contact_type, key, value)

    await session.commit()
    await session.refresh(existing_contact_type)

    return existing_contact_type


# =========================================================
# DELETE CONTACT TYPE
# =========================================================

@apiRouter.delete("/contact_types/{contact_type_id}")
async def delete_contact_type(
    contact_type_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete a contact type.

    WARNING:
    If this type is referenced in hippo_contact records,
    deletion should be prevented or replaced with soft delete.
    """

    result = await session.execute(
        select(HippoContactType).where(
            HippoContactType.id == contact_type_id
        )
    )

    existing_contact_type = result.scalar_one_or_none()

    if not existing_contact_type:
        raise HTTPException(status_code=404, detail="Contact type not found")

    await session.delete(existing_contact_type)
    await session.commit()

    return {"detail": "Contact type deleted successfully"}