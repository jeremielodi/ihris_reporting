"""
Employee Status API Endpoints
------------------------------

This module exposes REST endpoints for managing and retrieving
HippoEmployeeStatus entities.

All routes are protected and require an authenticated active user.
"""

from manage.models import HippoEmployeeStatus
from manage.services.employee_status.schemas import HippoEmployeeStatusRead
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from manage.database import SessionLocal
from endpoints.user_api import get_current_active_user


# Initialize API Router for employee status endpoints
apiRouter = APIRouter()


async def get_session() -> AsyncSession:
    """
    Dependency function to provide an asynchronous database session.

    This function:
    - Creates a new async database session
    - Yields the session to the request lifecycle
    - Automatically closes the session after request completion

    Returns:
        AsyncSession: SQLAlchemy asynchronous session
    """
    async with SessionLocal() as session:
        yield session


# -------------------------------------------------------------------
# GET ALL EMPLOYEE STATUSES
# -------------------------------------------------------------------
@apiRouter.get(
    "/employee_status/",
    response_model=list[HippoEmployeeStatusRead],
    dependencies=[Depends(get_current_active_user)],
)
async def get_employeeStatus(session: AsyncSession = Depends(get_session)):
    """
    Retrieve all employee statuses from the database.

    Security:
        - Requires authenticated active user.

    Process:
        1. Execute a SELECT query on HippoEmployeeStatus table.
        2. Extract scalar results.
        3. Return list of employee status records.

    Args:
        session (AsyncSession): Injected database session.

    Returns:
        List[HippoEmployeeStatusRead]: List of employee status records.
    """
    result = await session.execute(select(HippoEmployeeStatus))
    employeeStatus = result.scalars().all()
    return employeeStatus


# -------------------------------------------------------------------
# GET EMPLOYEE STATUS BY ID
# -------------------------------------------------------------------
@apiRouter.get(
    "/employee_status/{statusId}",
    response_model=HippoEmployeeStatusRead,
    dependencies=[Depends(get_current_active_user)],
)
async def get_status(statusId: str, session: AsyncSession = Depends(get_session)):
    """
    Retrieve a single employee status by its unique identifier.

    Security:
        - Requires authenticated active user.

    Process:
        1. Execute SELECT query filtered by statusId.
        2. Fetch a single record (or None).
        3. If not found → raise 404 error.
        4. Return the employee status object.

    Args:
        statusId (str): Unique identifier of the employee status.
        session (AsyncSession): Injected database session.

    Raises:
        HTTPException:
            - 404 if the employee status does not exist.

    Returns:
        HippoEmployeeStatusRead: Employee status record.
    """
    result = await session.execute(
        select(HippoEmployeeStatus).where(HippoEmployeeStatus.id == statusId)
    )
    status = result.scalar_one_or_none()

    # If no record found, return HTTP 404
    if not status:
        raise HTTPException(status_code=404, detail="Employee status not found")

    return status