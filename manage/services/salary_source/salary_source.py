# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

# ORM model
from manage.models import HippoSalarySource

# Pydantic schemas (validation & serialization)
from manage.services.salary_source.schemas import (
    HippoSalarySourceRead,
    HippoSalarySourceCreate,
    HippoSalarySourceUpdate
)

# Async DB session
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
    Ensures proper session lifecycle management.
    """
    async with SessionLocal() as session:
        yield session


# ---------------------------------------------------------
# GET ALL SALARY SOURCES
# ---------------------------------------------------------
@apiRouter.get(
    "/salary_sources/",
    response_model=list[HippoSalarySourceRead],
    dependencies=[Depends(get_current_active_user)],
)
async def get_salary_sources(session: AsyncSession = Depends(get_session)):
    """
    Retrieve all salary sources ordered alphabetically by name.
    Requires authenticated user.
    """
    result = await session.execute(
        select(HippoSalarySource).order_by(HippoSalarySource.name)
    )
    sources = result.scalars().all()
    return sources


# ---------------------------------------------------------
# GET SALARY SOURCE BY ID
# ---------------------------------------------------------
@apiRouter.get(
    "/salary_sources/{salary_source_id}",
    response_model=HippoSalarySourceRead,
    dependencies=[Depends(get_current_active_user)],
)
async def get_salary_source(
    salary_source_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieve a single Salary Source by ID.
    Returns 404 if not found.
    """
    result = await session.execute(
        select(HippoSalarySource).where(
            HippoSalarySource.id == salary_source_id
        )
    )

    salary_source = result.scalar_one_or_none()

    if not salary_source:
        raise HTTPException(status_code=404, detail="Salary source not found")

    return salary_source


# ---------------------------------------------------------
# CREATE SALARY SOURCE
# ---------------------------------------------------------
@apiRouter.post(
    "/salary_sources/",
    response_model=HippoSalarySourceRead,
    dependencies=[Depends(get_current_active_user)]
)
async def create_salary_source(
    salary_source: HippoSalarySourceCreate,
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new Salary Source.

    ID format: salary_source|<name>
    """

    # Convert Pydantic model to dictionary
    salary_source_data = salary_source.model_dump()

    # Generate ID (correct prefix)
    salary_source_data['id'] = f"salary_source|{salary_source.name}"

    # Create ORM instance
    new_salary_source = HippoSalarySource(**salary_source_data)

    session.add(new_salary_source)
    await session.commit()
    await session.refresh(new_salary_source)

    return new_salary_source


# ---------------------------------------------------------
# UPDATE SALARY SOURCE
# ---------------------------------------------------------
@apiRouter.put(
    "/salary_sources/{salary_source_id}",
    response_model=HippoSalarySourceRead
)
async def update_salary_source(
    salary_source_id: str,
    salary_source: HippoSalarySourceUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    Update an existing Salary Source.

    - Only non-null fields are updated.
    - Returns 404 if not found.
    """

    result = await session.execute(
        select(HippoSalarySource).where(
            HippoSalarySource.id == salary_source_id
        )
    )

    existing_salary_source = result.scalar_one_or_none()

    if not existing_salary_source:
        raise HTTPException(status_code=404, detail="Salary source not found")

    # Apply partial update
    for key, value in salary_source.model_dump().items():
        if value is not None:
            setattr(existing_salary_source, key, value)

    await session.commit()
    await session.refresh(existing_salary_source)

    return existing_salary_source


# ---------------------------------------------------------
# DELETE SALARY SOURCE
# ---------------------------------------------------------
@apiRouter.delete("/salary_sources/{salary_source_id}")
async def delete_salary_source(
    salary_source_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete a Salary Source by ID.
    Returns 404 if not found.
    """

    result = await session.execute(
        select(HippoSalarySource).where(
            HippoSalarySource.id == salary_source_id
        )
    )

    existing_salary_source = result.scalar_one_or_none()

    if not existing_salary_source:
        raise HTTPException(status_code=404, detail="Salary source not found")

    await session.delete(existing_salary_source)
    await session.commit()

    return {"detail": "Salary source deleted successfully"}