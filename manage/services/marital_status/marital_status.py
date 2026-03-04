# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

# ORM model
from manage.models import HippoMaritalStatus

# Pydantic schema (response serialization only — read-only module)
from manage.services.marital_status.schemas import (
    HippoMaritalStatusRead,
    HippoMaritalStatusCreate,
    HippoMaritalStatusUpdate
)
from sqlalchemy.ext.asyncio import AsyncSession

# FastAPI utilities
from fastapi import APIRouter,status, Depends, HTTPException

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
# GET ALL MARITAL STATUSES
# =========================================================

@apiRouter.get(
    "/marital_status/",
    response_model=list[HippoMaritalStatusRead]
)
async def get_marital_status_list(session: AsyncSession = Depends(get_session)):
    """
    Retrieve all marital statuses.

    Example values:
    - Single
    - Married
    - Divorced
    - Widowed

    NOTE:
    This endpoint is currently public (no authentication dependency).
    If this is reference data, that may be acceptable.
    """

    result = await session.execute(
        select(HippoMaritalStatus)
    )

    marital_statuses = result.scalars().all()
    return marital_statuses


# =========================================================
# GET MARITAL STATUS BY ID
# =========================================================

@apiRouter.get(
    "/marital_status/{marital_status_id}",
    response_model=HippoMaritalStatusRead,
    dependencies=[Depends(get_current_active_user)],
)
async def get_marital_status(
    marital_status_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieve a specific marital status by ID.

    - Requires authentication.
    - Returns 404 if not found.
    """

    result = await session.execute(
        select(HippoMaritalStatus).where(
            HippoMaritalStatus.id == marital_status_id
        )
    )

    marital_status = result.scalar_one_or_none()

    if not marital_status:
        raise HTTPException(status_code=404, detail="Marital status not found")

    return marital_status



# =========================================================
# CREATE MARITAL STATUS
# =========================================================
@apiRouter.post(
    "/marital_status/",
    response_model=HippoMaritalStatusRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_user)],
)
async def create_marital_status(
    marital_status: HippoMaritalStatusCreate,
    session: AsyncSession = Depends(get_session)
):
    """
    Create a new marital status.

    ID format:
        marital_status|<name>
    """
    data = marital_status.dict()

    # Generate ID based on name (same pattern as your other reference tables)
    data["id"] = f"marital_status|{marital_status.name}"

    new_item = HippoMaritalStatus(**data)
    session.add(new_item)
    await session.commit()
    await session.refresh(new_item)
    return new_item


# =========================================================
# UPDATE MARITAL STATUS
# =========================================================
@apiRouter.put(
    "/marital_status/{marital_status_id}",
    response_model=HippoMaritalStatusRead,
    dependencies=[Depends(get_current_active_user)],
)
async def update_marital_status(
    marital_status_id: str,
    marital_status: HippoMaritalStatusUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    Update an existing marital status.

    - Updates only non-null fields
    - Protects 'created'
    - Returns 404 if not found
    """
    result = await session.execute(
        select(HippoMaritalStatus).where(HippoMaritalStatus.id == marital_status_id)
    )
    existing = result.scalar_one_or_none()

    if not existing:
        raise HTTPException(status_code=404, detail="Marital status not found")

    for key, value in marital_status.dict().items():
        if value is not None and key != "created":
            setattr(existing, key, value)

    await session.commit()
    await session.refresh(existing)
    return existing


# =========================================================
# DELETE MARITAL STATUS
# =========================================================
@apiRouter.delete(
    "/marital_status/{marital_status_id}",
    dependencies=[Depends(get_current_active_user)],
)
async def delete_marital_status(
    marital_status_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete a marital status by ID.
    Returns 404 if not found.
    """
    result = await session.execute(
        select(HippoMaritalStatus).where(HippoMaritalStatus.id == marital_status_id)
    )
    existing = result.scalar_one_or_none()

    if not existing:
        raise HTTPException(status_code=404, detail="Marital status not found")

    await session.delete(existing)
    await session.commit()
    return {"detail": "Marital status deleted successfully"}