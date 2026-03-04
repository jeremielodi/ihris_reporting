# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

# ORM model
from manage.models import OrganizationUnitType

# Pydantic schemas (validation & serialization)
from manage.services.organization_unit_type.schemas import (
    OrganizationUnitTypeRead,
    OrganizationUnitTypeCreate,
    OrganizationUnitTypeUpdate
)

# Async DB session
from sqlalchemy.ext.asyncio import AsyncSession

# FastAPI utilities
from fastapi import APIRouter, Depends, HTTPException

# SQLAlchemy ORM query builder
from sqlalchemy.future import select

# Database session factory
from manage.database import SessionLocal

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
    Ensures proper open/close lifecycle handling.
    """
    async with SessionLocal() as session:
        yield session


# =========================================================
# GET ALL ORGANIZATION UNIT TYPES
# =========================================================

@apiRouter.get(
    "/organization_unit_types/",
    response_model=list[OrganizationUnitTypeRead],
    dependencies=[Depends(get_current_active_user)]
)
async def get_organization_unit_types(session: AsyncSession = Depends(get_session)):
    """
    Retrieve all organization unit types.

    Example:
    - HOSPITAL
    - HEALTH_CENTER
    - DISTRICT
    - PROVINCE
    """
    result = await session.execute(
        select(OrganizationUnitType)
    )
    org_unit_types = result.scalars().all()
    return org_unit_types


# =========================================================
# GET ORGANIZATION UNIT TYPE BY ID
# =========================================================

@apiRouter.get(
    "/organization_unit_types/{org_unit_type_id}",
    response_model=OrganizationUnitTypeRead,
    dependencies=[Depends(get_current_active_user)]
)
async def get_organization_unit_type(
    org_unit_type_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieve a single organization unit type by ID.
    Returns 404 if not found.
    """
    result = await session.execute(
        select(OrganizationUnitType).where(
            OrganizationUnitType.id == org_unit_type_id
        )
    )

    org_unit_type = result.scalar_one_or_none()

    if not org_unit_type:
        raise HTTPException(status_code=404, detail="Organization unit type not found")

    return org_unit_type


# =========================================================
# CREATE ORGANIZATION UNIT TYPE
# =========================================================

@apiRouter.post(
    "/organization_unit_types/",
    response_model=OrganizationUnitTypeRead,
    dependencies=[Depends(get_current_active_user)]
)
async def create_organization_unit_type(
    org_unit_type: OrganizationUnitTypeCreate,
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new organization unit type.

    - Ensures uniqueness by name.
    - Generates ID using prefix format.
    """

    # Check if name already exists
    result = await session.execute(
        select(OrganizationUnitType).where(
            OrganizationUnitType.name == org_unit_type.name
        )
    )
    existing_type = result.scalar_one_or_none()

    if existing_type:
        raise HTTPException(
            status_code=400,
            detail="Organization unit type with this name already exists"
        )

    # Convert request payload to dictionary
    org_unit_type_data = org_unit_type.dict()

    # Generate ID (⚠️ currently uses org_unit_type.id from payload — ensure it's intended)
    org_unit_type_data['id'] = f"org_unit_type|{org_unit_type.id}"

    # Create ORM instance
    new_org_unit_type = OrganizationUnitType(**org_unit_type_data)

    session.add(new_org_unit_type)
    await session.commit()
    await session.refresh(new_org_unit_type)

    return new_org_unit_type


# =========================================================
# UPDATE ORGANIZATION UNIT TYPE
# =========================================================

@apiRouter.put(
    "/organization_unit_types/{org_unit_type_id}",
    response_model=OrganizationUnitTypeRead,
    dependencies=[Depends(get_current_active_user)]
)
async def update_organization_unit_type(
    org_unit_type_id: str,
    org_unit_type: OrganizationUnitTypeUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    Update an existing organization unit type.

    - Checks if record exists.
    - Ensures name uniqueness if being modified.
    - Applies partial update using exclude_unset=True.
    """

    result = await session.execute(
        select(OrganizationUnitType).where(
            OrganizationUnitType.id == org_unit_type_id
        )
    )

    existing_org_unit_type = result.scalar_one_or_none()

    if not existing_org_unit_type:
        raise HTTPException(status_code=404, detail="Organization unit type not found")

    # If updating name, ensure uniqueness
    if org_unit_type.name and org_unit_type.name != existing_org_unit_type.name:
        name_result = await session.execute(
            select(OrganizationUnitType).where(
                OrganizationUnitType.name == org_unit_type.name
            )
        )
        duplicate_type = name_result.scalar_one_or_none()

        if duplicate_type:
            raise HTTPException(
                status_code=400,
                detail="Organization unit type with this name already exists"
            )

    # Apply partial update (only provided fields)
    for key, value in org_unit_type.dict(exclude_unset=True).items():
        if value is not None:
            setattr(existing_org_unit_type, key, value)

    await session.commit()
    await session.refresh(existing_org_unit_type)

    return existing_org_unit_type


# =========================================================
# DELETE ORGANIZATION UNIT TYPE
# =========================================================

@apiRouter.delete(
    "/organization_unit_types/{org_unit_type_id}",
    dependencies=[Depends(get_current_active_user)]
)
async def delete_organization_unit_type(
    org_unit_type_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete an organization unit type by ID.

    Returns 404 if not found.
    """

    result = await session.execute(
        select(OrganizationUnitType).where(
            OrganizationUnitType.id == org_unit_type_id
        )
    )

    existing_org_unit_type = result.scalar_one_or_none()

    if not existing_org_unit_type:
        raise HTTPException(status_code=404, detail="Organization unit type not found")

    await session.delete(existing_org_unit_type)
    await session.commit()

    return {"detail": "Organization unit type deleted successfully"}