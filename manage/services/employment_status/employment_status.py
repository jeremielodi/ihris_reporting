"""
Employment Status API Endpoints
-------------------------------

This module provides CRUD operations for HippoEmploymentStatus.

EmploymentStatus represents standardized employment states
(e.g., Active, Suspended, Retired, Terminated, On Leave, etc.).

These statuses are typically referenced in:
- EmploymentStatusInfo history
- Reporting modules
- Workforce analytics

All endpoints require authenticated active users.
"""

from manage.models import HippoEmploymentStatus
from manage.services.employment_status.schemas import (
    HippoEmploymentStatusRead,
    HippoEmploymentStatusCreate,
    HippoEmploymentStatusUpdate
)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user


# Initialize API router
apiRouter = APIRouter()


async def get_session() -> AsyncSession:
    """
    Provides an asynchronous database session.

    - Opens AsyncSession
    - Yields session during request lifecycle
    - Automatically closes after completion
    """
    async with SessionLocal() as session:
        yield session


# -------------------------------------------------------------------
# GET ALL EMPLOYMENT STATUS RECORDS
# -------------------------------------------------------------------
@apiRouter.get(
    "/employment_status/",
    response_model=list[HippoEmploymentStatusRead],
    dependencies=[Depends(get_current_active_user)],
)
async def get_employment_status(session: AsyncSession = Depends(get_session)):
    """
    Retrieve all employment status records.

    Results are ordered alphabetically by name
    for consistent UI display.

    Returns:
        List[HippoEmploymentStatusRead]
    """
    result = await session.execute(
        select(HippoEmploymentStatus)
        .order_by(HippoEmploymentStatus.name)
    )
    employment_status = result.scalars().all()
    return employment_status


# -------------------------------------------------------------------
# GET EMPLOYMENT STATUS BY ID
# -------------------------------------------------------------------
@apiRouter.get(
    "/employment_status/{employment_status_id}",
    response_model=HippoEmploymentStatusRead,
    dependencies=[Depends(get_current_active_user)],
)
async def get_Employment_status(
    employment_status_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieve a specific employment status by ID.

    Args:
        employment_status_id (str): Unique identifier.

    Raises:
        HTTPException(404): If record does not exist.

    Returns:
        HippoEmploymentStatusRead
    """
    result = await session.execute(
        select(HippoEmploymentStatus)
        .where(HippoEmploymentStatus.id == employment_status_id)
    )
    Employment_status = result.scalar_one_or_none()

    if not Employment_status:
        raise HTTPException(
            status_code=404,
            detail="Employment_status not found"
        )

    return Employment_status


# -------------------------------------------------------------------
# CREATE NEW EMPLOYMENT STATUS
# -------------------------------------------------------------------
@apiRouter.post(
    "/employment_status/",
    response_model=HippoEmploymentStatusRead,
    dependencies=[Depends(get_current_active_user)]
)
async def create_Employment_status(
    Employment_status: HippoEmploymentStatusCreate,
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new employment status record.

    Process:
        1. Convert Pydantic model to dictionary.
        2. Generate deterministic ID using naming convention:
           "employment_status|<name>".
        3. Insert record into database.
        4. Commit and refresh instance.

    Returns:
        HippoEmploymentStatusRead
    """

    Employment_status_data = Employment_status.dict()

    # Generate ID based on name
    Employment_status_data['id'] = (
        f"employment_status|{Employment_status.name}"
    )

    new_Employment_status = HippoEmploymentStatus(**Employment_status_data)

    session.add(new_Employment_status)
    await session.commit()
    await session.refresh(new_Employment_status)

    return new_Employment_status


# -------------------------------------------------------------------
# UPDATE EMPLOYMENT STATUS
# -------------------------------------------------------------------
@apiRouter.put(
    "/employment_status/{employment_status_id}",
    response_model=HippoEmploymentStatusRead
)
async def update_Employment_status(
    employment_status_id: str,
    Employment_status: HippoEmploymentStatusUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    Update an existing employment status record.

    - Updates only provided (non-null) fields.
    - Keeps existing values for omitted fields.

    Raises:
        HTTPException(404): If record not found.

    Returns:
        HippoEmploymentStatusRead
    """

    result = await session.execute(
        select(HippoEmploymentStatus)
        .where(HippoEmploymentStatus.id == employment_status_id)
    )
    existing_Employment_status = result.scalar_one_or_none()

    if not existing_Employment_status:
        raise HTTPException(
            status_code=404,
            detail="Employment_status not found"
        )

    # Apply partial update
    for key, value in Employment_status.dict().items():
        if value is not None:
            setattr(existing_Employment_status, key, value)

    await session.commit()
    await session.refresh(existing_Employment_status)

    return existing_Employment_status


# -------------------------------------------------------------------
# DELETE EMPLOYMENT STATUS
# -------------------------------------------------------------------
@apiRouter.delete("/employment_status/{employment_status_id}")
async def delete_Employment_status(
    employment_status_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete an employment status record.

    Raises:
        HTTPException(404): If record not found.

    Returns:
        dict: Confirmation message.
    """

    result = await session.execute(
        select(HippoEmploymentStatus)
        .where(HippoEmploymentStatus.id == employment_status_id)
    )
    existing_Employment_status = result.scalar_one_or_none()

    if not existing_Employment_status:
        raise HTTPException(
            status_code=404,
            detail="Employment_status not found"
        )

    await session.delete(existing_Employment_status)
    await session.commit()

    return {"detail": "Employment_status deleted successfully"}