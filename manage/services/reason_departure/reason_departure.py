"""
Reason Departure API Endpoints
------------------------------

This module provides CRUD operations for HippoReasonDeparture.

ReasonDeparture represents standardized reasons why an employee
leaves an organization (e.g., Retirement, Resignation, Dismissal,
End of Contract, Transfer, etc.).

All endpoints require an authenticated active user.
"""

from manage.models import HippoReasonDeparture
from manage.services.reason_departure.schemas import (
    HippoReasonDepartureRead,
    HippoReasonDepartureCreate,
    HippoReasonDepartureUpdate
)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user


# Initialize API router for reason departure endpoints
apiRouter = APIRouter()


async def get_session() -> AsyncSession:
    """
    Dependency that provides an asynchronous database session.

    - Opens a new AsyncSession.
    - Yields it during the request lifecycle.
    - Automatically closes it after request completion.
    """
    async with SessionLocal() as session:
        yield session


# -------------------------------------------------------------------
# GET ALL REASON DEPARTURES
# -------------------------------------------------------------------
@apiRouter.get(
    "/reason_departures/",
    response_model=list[HippoReasonDepartureRead],
    dependencies=[Depends(get_current_active_user)],
)
async def get_reason_departures(session: AsyncSession = Depends(get_session)):
    """
    Retrieve all reason_departure records ordered alphabetically by name.

    Security:
        - Requires authenticated active user.

    Process:
        1. Execute SELECT query ordered by name.
        2. Extract ORM scalar objects.
        3. Return list of reason departures.

    Returns:
        List[HippoReasonDepartureRead]
    """
    result = await session.execute(
        select(HippoReasonDeparture).order_by(HippoReasonDeparture.name)
    )
    reason_departures = result.scalars().all()
    return reason_departures


# -------------------------------------------------------------------
# GET REASON DEPARTURE BY ID
# -------------------------------------------------------------------
@apiRouter.get(
    "/reason_departures/{reason_departure_id}",
    response_model=HippoReasonDepartureRead,
    dependencies=[Depends(get_current_active_user)],
)
async def get_Reason_departure(
    reason_departure_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieve a specific reason_departure by its unique ID.

    Args:
        reason_departure_id (str): Unique identifier.
        session (AsyncSession): Injected database session.

    Raises:
        HTTPException(404): If reason_departure does not exist.

    Returns:
        HippoReasonDepartureRead
    """
    result = await session.execute(
        select(HippoReasonDeparture)
        .where(HippoReasonDeparture.id == reason_departure_id)
    )
    Reason_departure = result.scalar_one_or_none()

    if not Reason_departure:
        raise HTTPException(status_code=404, detail="Reason_departure not found")

    return Reason_departure


# -------------------------------------------------------------------
# CREATE NEW REASON DEPARTURE
# -------------------------------------------------------------------
@apiRouter.post(
    "/reason_departures/",
    response_model=HippoReasonDepartureRead,
    dependencies=[Depends(get_current_active_user)]
)
async def create_Reason_departure(
    Reason_departure: HippoReasonDepartureCreate,
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new reason_departure record.

    Process:
        1. Convert Pydantic model to dictionary.
        2. Generate deterministic ID:
           "reason_departure|<name>".
        3. Create ORM instance.
        4. Insert into database.
        5. Commit and refresh.

    Args:
        Reason_departure (HippoReasonDepartureCreate): Input payload.
        session (AsyncSession): Injected database session.

    Returns:
        HippoReasonDepartureRead
    """
    Reason_departure_data = Reason_departure.model_dump()

    # Generate ID based on naming convention
    Reason_departure_data['id'] = f"reason_departure|{Reason_departure.name}"

    new_Reason_departure = HippoReasonDeparture(**Reason_departure_data)

    session.add(new_Reason_departure)
    await session.commit()
    await session.refresh(new_Reason_departure)

    return new_Reason_departure


# -------------------------------------------------------------------
# UPDATE EXISTING REASON DEPARTURE
# -------------------------------------------------------------------
@apiRouter.put(
    "/reason_departures/{reason_departure_id}",
    response_model=HippoReasonDepartureRead
)
async def update_Reason_departure(
    reason_departure_id: str,
    Reason_departure: HippoReasonDepartureUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    Update an existing reason_departure record.

    Process:
        1. Retrieve existing record by ID.
        2. If not found → return 404.
        3. Update only non-null fields.
        4. Commit changes.
        5. Refresh and return updated object.

    Args:
        reason_departure_id (str): Unique identifier.
        Reason_departure (HippoReasonDepartureUpdate): Update payload.
        session (AsyncSession): Injected database session.

    Raises:
        HTTPException(404): If record does not exist.

    Returns:
        HippoReasonDepartureRead
    """
    result = await session.execute(
        select(HippoReasonDeparture)
        .where(HippoReasonDeparture.id == reason_departure_id)
    )
    existing_Reason_departure = result.scalar_one_or_none()

    if not existing_Reason_departure:
        raise HTTPException(status_code=404, detail="Reason_departure not found")

    # Apply partial update (only provided fields)
    for key, value in Reason_departure.model_dump().items():
        if value is not None:
            setattr(existing_Reason_departure, key, value)

    await session.commit()
    await session.refresh(existing_Reason_departure)

    return existing_Reason_departure


# -------------------------------------------------------------------
# DELETE REASON DEPARTURE
# -------------------------------------------------------------------
@apiRouter.delete("/reason_departures/{reason_departure_id}")
async def delete_Reason_departure(
    reason_departure_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete a reason_departure record by ID.

    Process:
        1. Retrieve record by ID.
        2. If not found → return 404.
        3. Delete record.
        4. Commit transaction.

    Args:
        reason_departure_id (str): Unique identifier.
        session (AsyncSession): Injected database session.

    Raises:
        HTTPException(404): If record not found.

    Returns:
        dict: Success confirmation message.
    """
    result = await session.execute(
        select(HippoReasonDeparture)
        .where(HippoReasonDeparture.id == reason_departure_id)
    )
    existing_Reason_departure = result.scalar_one_or_none()

    if not existing_Reason_departure:
        raise HTTPException(status_code=404, detail="Reason_departure not found")

    await session.delete(existing_Reason_departure)
    await session.commit()

    return {"detail": "Reason_departure deleted successfully"}