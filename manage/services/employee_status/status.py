"""
Employee Status API Endpoints
------------------------------

This module exposes REST endpoints for managing and retrieving
HippoEmployeeStatus entities.

All routes are protected and require an authenticated active user.
"""

from manage.models import HippoEmployeeStatus
from manage.services.employee_status.schemas import (
    HippoEmployeeStatusCreate,
    HippoEmployeeStatusUpdate,
    HippoEmployeeStatusRead
)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.future import select
from manage.database import SessionLocal
from endpoints.user_api import get_current_active_user
from datetime import datetime


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
async def get_employee_statuses(session: AsyncSession = Depends(get_session)):
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
    employee_statuses = result.scalars().all()
    return employee_statuses


# -------------------------------------------------------------------
# GET EMPLOYEE STATUS BY ID
# -------------------------------------------------------------------
@apiRouter.get(
    "/employee_status/{status_id}",
    response_model=HippoEmployeeStatusRead,
    dependencies=[Depends(get_current_active_user)],
)
async def get_employee_status(status_id: str, session: AsyncSession = Depends(get_session)):
    """
    Retrieve a single employee status by its unique identifier.

    Security:
        - Requires authenticated active user.

    Process:
        1. Execute SELECT query filtered by status_id.
        2. Fetch a single record (or None).
        3. If not found → raise 404 error.
        4. Return the employee status object.

    Args:
        status_id (str): Unique identifier of the employee status.
        session (AsyncSession): Injected database session.

    Raises:
        HTTPException:
            - 404 if the employee status does not exist.

    Returns:
        HippoEmployeeStatusRead: Employee status record.
    """
    result = await session.execute(
        select(HippoEmployeeStatus).where(HippoEmployeeStatus.id == status_id)
    )
    status = result.scalar_one_or_none()

    if not status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee status not found"
        )

    return status


# -------------------------------------------------------------------
# CREATE EMPLOYEE STATUS
# -------------------------------------------------------------------
@apiRouter.post(
    "/employee_status/",
    response_model=HippoEmployeeStatusRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_user)],
)
async def create_employee_status(
    employee_status_data: HippoEmployeeStatusCreate,
    session: AsyncSession = Depends(get_session)
):
    """
    Create a new employee status.

    Security:
        - Requires authenticated active user.

    Process:
        1. Check if an employee status with the same ID already exists.
        2. If exists → raise 400 error.
        3. Create new employee status object with provided data.
        4. Add to session and commit to database.
        5. Refresh to get updated timestamps.
        6. Return the created employee status.

    Args:
        employee_status_data (HippoEmployeeStatusCreate): Employee status data to create.
        session (AsyncSession): Injected database session.

    Raises:
        HTTPException:
            - 400 if an employee status with the same ID already exists.
            - 422 if validation fails.

    Returns:
        HippoEmployeeStatusRead: Created employee status record.
    """
    # Check if employee status with this ID already exists
    existing = await session.execute(
        select(HippoEmployeeStatus).where(
            HippoEmployeeStatus.id == employee_status_data.id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Employee status with ID '{employee_status_data.id}' already exists"
        )

    # Create new employee status
    new_status = HippoEmployeeStatus(
        id=employee_status_data.id,
        parent=employee_status_data.parent or '|',
        remap=employee_status_data.remap,
        i2ce_hidden=employee_status_data.i2ce_hidden or 0,
        name=employee_status_data.name,
        translate_key=employee_status_data.translate_key,
        created=datetime.now(),
        last_modified=datetime.now()
    )

    session.add(new_status)
    await session.commit()
    await session.refresh(new_status)

    return new_status


# -------------------------------------------------------------------
# UPDATE EMPLOYEE STATUS
# -------------------------------------------------------------------
@apiRouter.put(
    "/employee_status/{status_id}",
    response_model=HippoEmployeeStatusRead,
    dependencies=[Depends(get_current_active_user)],
)
async def update_employee_status(
    status_id: str,
    employee_status_data: HippoEmployeeStatusUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    Update an existing employee status.

    Security:
        - Requires authenticated active user.

    Process:
        1. Find the employee status by ID.
        2. If not found → raise 404 error.
        3. Update only provided fields.
        4. Always update last_modified timestamp.
        5. Commit changes.
        6. Refresh to get updated data.
        7. Return the updated employee status.

    Args:
        status_id (str): ID of the employee status to update.
        employee_status_data (HippoEmployeeStatusUpdate): Data to update.
        session (AsyncSession): Injected database session.

    Raises:
        HTTPException:
            - 404 if the employee status does not exist.

    Returns:
        HippoEmployeeStatusRead: Updated employee status record.
    """
    # Find existing employee status
    result = await session.execute(
        select(HippoEmployeeStatus).where(HippoEmployeeStatus.id == status_id)
    )
    status = result.scalar_one_or_none()

    if not status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee status with ID '{status_id}' not found"
        )

    # Update only provided fields
    update_data = employee_status_data.dict(exclude_unset=True)
    
    # Remove id and timestamps from update data if present
    update_data.pop('id', None)
    update_data.pop('created', None)
    update_data.pop('last_modified', None)
    
    # Apply updates
    for key, value in update_data.items():
        setattr(status, key, value)
    
    # Always update last_modified timestamp
    status.last_modified = datetime.now()

    await session.commit()
    await session.refresh(status)

    return status


# -------------------------------------------------------------------
# DELETE EMPLOYEE STATUS
# -------------------------------------------------------------------
@apiRouter.delete(
    "/employee_status/{status_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_active_user)],
)
async def delete_employee_status(
    status_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete an employee status by its ID.

    Security:
        - Requires authenticated active user.

    Process:
        1. Find the employee status by ID.
        2. If not found → raise 404 error.
        3. Delete the record from the database.
        4. Commit the transaction.

    Args:
        status_id (str): ID of the employee status to delete.
        session (AsyncSession): Injected database session.

    Raises:
        HTTPException:
            - 404 if the employee status does not exist.

    Returns:
        None (204 No Content on success)
    """
    # Find existing employee status
    result = await session.execute(
        select(HippoEmployeeStatus).where(HippoEmployeeStatus.id == status_id)
    )
    status = result.scalar_one_or_none()

    if not status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee status with ID '{status_id}' not found"
        )

    await session.delete(status)
    await session.commit()

    return None  # 204 No Content