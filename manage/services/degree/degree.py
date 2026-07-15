# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

# Base model (if needed for metadata) and ORM model
from manage.models import Base, HippoDegree

# Pydantic schemas (validation + serialization)
from manage.services.degree.schemas import (
    HippoDegreeRead,
    HippoDegreeCreate,
    HippoDegreeUpdate
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
# GET ALL DEGREES
# =========================================================

@apiRouter.get(
    "/degrees/",
    response_model=list[HippoDegreeRead],
    dependencies=[Depends(get_current_active_user)],
)
async def get_degrees(session: AsyncSession = Depends(get_session)):
    """
    Retrieve all degrees ordered alphabetically by name.

    Example:
    - Bachelor
    - Master
    - PhD
    - Diploma
    """

    result = await session.execute(
        select(HippoDegree).order_by(HippoDegree.name)
    )

    degrees = result.scalars().all()
    return degrees


# =========================================================
# GET DEGREE BY ID
# =========================================================

@apiRouter.get(
    "/degrees/{degree_id}",
    response_model=HippoDegreeRead,
    dependencies=[Depends(get_current_active_user)],
)
async def get_degree(degree_id: str, session: AsyncSession = Depends(get_session)):
    """
    Retrieve a specific degree by ID.

    Returns:
    - 404 if the degree does not exist.
    """

    result = await session.execute(
        select(HippoDegree).where(
            HippoDegree.id == degree_id
        )
    )

    degree = result.scalar_one_or_none()

    if not degree:
        raise HTTPException(status_code=404, detail="Degree not found")

    return degree


# =========================================================
# CREATE DEGREE
# =========================================================

@apiRouter.post(
    "/degrees/",
    response_model=HippoDegreeRead,
    dependencies=[Depends(get_current_active_user)],
)
async def create_degree(
    degree: HippoDegreeCreate,
    session: AsyncSession = Depends(get_session)
):
    """
    Create a new degree.

    ID format:
        degree|<name>

    NOTE:
    Consider validating uniqueness of name before insertion.
    """

    degree_data = degree.model_dump()
    # Generate ID based on degree name
    degree_data['id'] = f"degree|{degree.name}"

    new_degree = HippoDegree(**degree_data)

    session.add(new_degree)
    await session.commit()
    await session.refresh(new_degree)

    return new_degree


# =========================================================
# UPDATE DEGREE
# =========================================================

@apiRouter.put(
    "/degrees/{degree_id}",
    response_model=HippoDegreeRead,
    dependencies=[Depends(get_current_active_user)],
)
async def update_degree(
    degree_id: str,
    degree: HippoDegreeUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    Update an existing degree.

    - Returns 404 if not found.
    - Updates provided fields.
    """

    result = await session.execute(
        select(HippoDegree).where(
            HippoDegree.id == degree_id
        )
    )

    existing_degree = result.scalar_one_or_none()

    if not existing_degree:
        raise HTTPException(status_code=404, detail="Degree not found")

    # Update all fields (consider using exclude_unset=True for partial updates)
    for key, value in degree.model_dump().items():
        if value is not None:
            setattr(existing_degree, key, value)

    await session.commit()
    await session.refresh(existing_degree)

    return existing_degree


# =========================================================
# DELETE DEGREE
# =========================================================

@apiRouter.delete(
    "/degrees/{degree_id}",
    dependencies=[Depends(get_current_active_user)],
)
async def delete_degree(
    degree_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete a degree.

    WARNING:
    If degree is referenced in hippo_person or other tables,
    deletion should be prevented or replaced with soft delete.
    """

    result = await session.execute(
        select(HippoDegree).where(
            HippoDegree.id == degree_id
        )
    )

    existing_degree = result.scalar_one_or_none()

    if not existing_degree:
        raise HTTPException(status_code=404, detail="Degree not found")

    await session.delete(existing_degree)
    await session.commit()

    return {"detail": "Degree deleted successfully"}