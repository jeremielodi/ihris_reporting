# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

# ORM model
from manage.models import HippoJobTitle

# Pydantic schemas (validation + serialization)
from manage.services.job_title.schemas import (
    HippoJobTitleRead,
    HippoJobTitleCreate,
    HippoJobTitleUpdate
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
    Ensures proper open/close lifecycle management.
    """
    async with SessionLocal() as session:
        yield session


# =========================================================
# GET ALL JOB TITLES
# =========================================================

@apiRouter.get(
    "/job_titles/",
    response_model=list[HippoJobTitleRead],
    dependencies=[Depends(get_current_active_user)],
)
async def get_job_titles(session: AsyncSession = Depends(get_session)):
    """
    Retrieve all job titles ordered alphabetically by name.

    Example:
    - Nurse
    - Doctor
    - Pharmacist
    - Laboratory Technician
    """
    result = await session.execute(
        select(HippoJobTitle).order_by(HippoJobTitle.name)
    )

    job_titles = result.scalars().all()
    return job_titles


# =========================================================
# GET JOB TITLE BY ID
# =========================================================

@apiRouter.get(
    "/job_titles/{job_title_id}",
    response_model=HippoJobTitleRead,
    dependencies=[Depends(get_current_active_user)],
)
async def get_job_title(
    job_title_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieve a specific job title by ID.
    Returns 404 if not found.
    """

    result = await session.execute(
        select(HippoJobTitle).where(
            HippoJobTitle.id == job_title_id
        )
    )

    job_title = result.scalar_one_or_none()

    if not job_title:
        raise HTTPException(status_code=404, detail="Job title not found")

    return job_title


# =========================================================
# CREATE JOB TITLE
# =========================================================

@apiRouter.post(
    "/job_titles/",
    response_model=HippoJobTitleRead,
    dependencies=[Depends(get_current_active_user)]
)
async def create_job_title(
    job_title: HippoJobTitleCreate,
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new job title.

    ID format:
        job_title|<name>

    NOTE:
    If names are not unique, you should add a uniqueness check
    before insertion.
    """

    # Convert Pydantic model to dictionary
    job_title_data = job_title.dict()

    # Generate ID using name
    job_title_data['id'] = f"job_title|{job_title.name}"

    # Create ORM instance
    new_job_title = HippoJobTitle(**job_title_data)

    session.add(new_job_title)
    await session.commit()
    await session.refresh(new_job_title)

    return new_job_title


# =========================================================
# UPDATE JOB TITLE
# =========================================================

@apiRouter.put(
    "/job_titles/{job_title_id}",
    response_model=HippoJobTitleRead
)
async def update_job_title(
    job_title_id: str,
    job_title: HippoJobTitleUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    Update an existing job title.

    - Only non-null fields are updated.
    - Returns 404 if not found.
    """

    result = await session.execute(
        select(HippoJobTitle).where(
            HippoJobTitle.id == job_title_id
        )
    )

    existing_job_title = result.scalar_one_or_none()

    if not existing_job_title:
        raise HTTPException(status_code=404, detail="Job title not found")

    # Apply partial update
    for key, value in job_title.dict().items():
        if value is not None:
            setattr(existing_job_title, key, value)

    await session.commit()
    await session.refresh(existing_job_title)

    return existing_job_title


# =========================================================
# DELETE JOB TITLE
# =========================================================

@apiRouter.delete("/job_titles/{job_title_id}")
async def delete_job_title(
    job_title_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete a job title by ID.

    WARNING:
    If job titles are referenced in employment records,
    consider preventing deletion or implementing soft delete.
    """

    result = await session.execute(
        select(HippoJobTitle).where(
            HippoJobTitle.id == job_title_id
        )
    )

    existing_job_title = result.scalar_one_or_none()

    if not existing_job_title:
        raise HTTPException(status_code=404, detail="Job title not found")

    await session.delete(existing_job_title)
    await session.commit()

    return {"detail": "Job title deleted successfully"}