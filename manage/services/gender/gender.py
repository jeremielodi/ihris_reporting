# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

# ORM model
from manage.models import HippoGender

# Pydantic schema (read-only reference data)
from manage.services.gender.schemas import HippoGenderRead

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
    Ensures proper lifecycle management (open/close).
    """
    async with SessionLocal() as session:
        yield session


# =========================================================
# GET ALL GENDERS
# =========================================================

@apiRouter.get(
    "/genders/",
    response_model=list[HippoGenderRead]
)
async def get_genders(session: AsyncSession = Depends(get_session)):
    """
    Retrieve all gender reference values.

    Example:
    - Male
    - Female
    - Other

    NOTE:
    This endpoint is currently public (no authentication required).
    If this is sensitive in your system, add authentication dependency.
    """

    result = await session.execute(
        select(HippoGender)
    )

    genders = result.scalars().all()
    return genders


# =========================================================
# GET GENDER BY ID
# =========================================================

@apiRouter.get(
    "/genders/{gender_id}",
    response_model=HippoGenderRead,
    dependencies=[Depends(get_current_active_user)],
)
async def get_gender(
    gender_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieve a specific gender by ID.

    - Requires authentication.
    - Returns 404 if not found.
    """

    result = await session.execute(
        select(HippoGender).where(
            HippoGender.id == gender_id
        )
    )

    gender = result.scalar_one_or_none()

    if not gender:
        raise HTTPException(status_code=404, detail="Gender not found")

    return gender