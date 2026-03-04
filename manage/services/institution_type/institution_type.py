"""
Institution Type API Endpoints
------------------------------

This module exposes CRUD (Create, Read, Update, Delete)
operations for HippoInstitutionType entities.

Institution types typically represent categories of health
institutions (e.g., Public Hospital, Private Clinic, NGO Facility, etc.).

All read and write operations require an authenticated active user.
"""

from manage.models import HippoInstitutionType
from manage.services.institution_type.schemas import (
    HippoInstitutionTypeRead,
    HippoInstitutionTypeCreate,
    HippoInstitutionTypeUpdate
)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user


# Initialize API Router for institution type endpoints
apiRouter = APIRouter()


async def get_session() -> AsyncSession:
    """
    Dependency that provides an asynchronous database session.

    - Opens a new AsyncSession.
    - Yields it during the request lifecycle.
    - Automatically closes it after completion.

    Returns:
        AsyncSession: Active database session.
    """
    async with SessionLocal() as session:
        yield session


# -------------------------------------------------------------------
# GET ALL INSTITUTION TYPES
# -------------------------------------------------------------------
@apiRouter.get(
    "/institution_types/",
    response_model=list[HippoInstitutionTypeRead],
    dependencies=[Depends(get_current_active_user)],
)
async def get_institution_types(session: AsyncSession = Depends(get_session)):
    """
    Retrieve all institution types ordered alphabetically by name.

    Security:
        - Requires authenticated active user.

    Process:
        1. Execute SELECT query ordered by name.
        2. Extract scalar ORM objects.
        3. Return list of institution types.

    Args:
        session (AsyncSession): Injected database session.

    Returns:
        List[HippoInstitutionTypeRead]
    """
    result = await session.execute(
        select(HippoInstitutionType).order_by(HippoInstitutionType.name)
    )
    institution_types = result.scalars().all()
    return institution_types


# -------------------------------------------------------------------
# GET INSTITUTION TYPE BY ID
# -------------------------------------------------------------------
@apiRouter.get(
    "/institution_types/{institution_type_id}",
    response_model=HippoInstitutionTypeRead,
    dependencies=[Depends(get_current_active_user)],
)
async def get_Institution_type(
    institution_type_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieve a specific institution type by its unique ID.

    Security:
        - Requires authenticated active user.

    Args:
        institution_type_id (str): Unique identifier.
        session (AsyncSession): Injected database session.

    Raises:
        HTTPException:
            - 404 if institution type not found.

    Returns:
        HippoInstitutionTypeRead
    """
    result = await session.execute(
        select(HippoInstitutionType)
        .where(HippoInstitutionType.id == institution_type_id)
    )
    Institution_type = result.scalar_one_or_none()

    if not Institution_type:
        raise HTTPException(status_code=404, detail="Institution_type not found")

    return Institution_type


# -------------------------------------------------------------------
# CREATE NEW INSTITUTION TYPE
# -------------------------------------------------------------------
@apiRouter.post(
    "/institution_types/",
    response_model=HippoInstitutionTypeRead,
    dependencies=[Depends(get_current_active_user)]
)
async def create_Institution_type(
    Institution_type: HippoInstitutionTypeCreate,
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new institution type.

    Security:
        - Requires authenticated active user.

    Process:
        1. Convert Pydantic model to dictionary.
        2. Generate a custom ID using naming convention:
           "institution_type|<name>".
        3. Create ORM instance.
        4. Add to session.
        5. Commit transaction.
        6. Refresh and return created object.

    Args:
        Institution_type (HippoInstitutionTypeCreate): Input data.
        session (AsyncSession): Injected database session.

    Returns:
        HippoInstitutionTypeRead
    """
    Institution_type_data = Institution_type.dict()

    # Generate deterministic ID based on naming convention
    Institution_type_data['id'] = f"institution_type|{Institution_type.name}"

    new_Institution_type = HippoInstitutionType(**Institution_type_data)

    session.add(new_Institution_type)
    await session.commit()
    await session.refresh(new_Institution_type)

    return new_Institution_type


# -------------------------------------------------------------------
# UPDATE EXISTING INSTITUTION TYPE
# -------------------------------------------------------------------
@apiRouter.put(
    "/institution_types/{institution_type_id}",
    response_model=HippoInstitutionTypeRead
)
async def update_Institution_type(
    institution_type_id: str,
    Institution_type: HippoInstitutionTypeUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    Update an existing institution type.

    Process:
        1. Retrieve existing record by ID.
        2. If not found → return 404.
        3. Update only non-null fields.
        4. Commit changes.
        5. Refresh and return updated record.

    Args:
        institution_type_id (str): Unique identifier.
        Institution_type (HippoInstitutionTypeUpdate): Update payload.
        session (AsyncSession): Injected database session.

    Raises:
        HTTPException:
            - 404 if institution type not found.

    Returns:
        HippoInstitutionTypeRead
    """
    result = await session.execute(
        select(HippoInstitutionType)
        .where(HippoInstitutionType.id == institution_type_id)
    )
    existing_Institution_type = result.scalar_one_or_none()

    if not existing_Institution_type:
        raise HTTPException(status_code=404, detail="Institution_type not found")

    # Update only fields provided in request
    for key, value in Institution_type.dict().items():
        if value is not None:
            setattr(existing_Institution_type, key, value)

    await session.commit()
    await session.refresh(existing_Institution_type)

    return existing_Institution_type


# -------------------------------------------------------------------
# DELETE INSTITUTION TYPE
# -------------------------------------------------------------------
@apiRouter.delete("/institution_types/{institution_type_id}")
async def delete_Institution_type(
    institution_type_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete an institution type by ID.

    Process:
        1. Retrieve record by ID.
        2. If not found → return 404.
        3. Delete record.
        4. Commit transaction.

    Args:
        institution_type_id (str): Unique identifier.
        session (AsyncSession): Injected database session.

    Raises:
        HTTPException:
            - 404 if institution type not found.

    Returns:
        dict: Success confirmation message.
    """
    result = await session.execute(
        select(HippoInstitutionType)
        .where(HippoInstitutionType.id == institution_type_id)
    )
    existing_Institution_type = result.scalar_one_or_none()

    if not existing_Institution_type:
        raise HTTPException(status_code=404, detail="Institution_type not found")

    await session.delete(existing_Institution_type)
    await session.commit()

    return {"detail": "Institution_type deleted successfully"}