"""
Organization Level API Endpoints
---------------------------------

This module exposes REST endpoints for retrieving organization levels.

Organization levels typically represent hierarchical levels such as:
- National
- Provincial
- District
- Facility

All endpoints are protected and require an authenticated active user.
"""

from manage.models import OrganizationLevel
from manage.services.organization_level.schemas import OrganizationUnitLevelRead
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user
from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException, status
import uuid

from manage.services.organization_level.schemas import (
    OrganizationUnitLevelRead,
    OrganizationUnitLevelCreate,
    OrganizationUnitLevelUpdate,
)

# Initialize API router for organization level endpoints
apiRouter = APIRouter()


async def get_session() -> AsyncSession:
    """
    Dependency that provides an asynchronous database session.

    This function:
    - Opens a new AsyncSession
    - Yields it to the request lifecycle
    - Automatically closes it after the request completes

    Returns:
        AsyncSession: Active database session
    """
    async with SessionLocal() as session:
        yield session




apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


# -------------------------------------------------------------------
# CREATE ORGANIZATION LEVEL
# -------------------------------------------------------------------
@apiRouter.post(
    "/organization_levels/",
    response_model=OrganizationUnitLevelRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_user)],
)
async def create_organization_level(
    payload: OrganizationUnitLevelCreate,
    db: AsyncSession = Depends(get_session),
):
    """
    Create a new organization level.

    - If payload.id is not provided, generates one.
    - Returns the created record.
    """

    data = payload.model_dump()

    # Generate an ID if missing
    if not data.get("id"):
        data["id"] = f"org_level|{uuid.uuid4().hex[:10]}"

    # Optional uniqueness check (choose what you want to enforce)
    # Example: prevent duplicate level number
    result = await db.execute(select(OrganizationLevel).where(OrganizationLevel.level == data["level"]))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Organization level with this level already exists")

    new_level = OrganizationLevel(**data)
    db.add(new_level)
    await db.commit()
    await db.refresh(new_level)

    return new_level


# -------------------------------------------------------------------
# UPDATE ORGANIZATION LEVEL
# -------------------------------------------------------------------
@apiRouter.put(
    "/organization_levels/{id}",
    response_model=OrganizationUnitLevelRead,
    dependencies=[Depends(get_current_active_user)],
)
async def update_organization_level(
    id: str,
    payload: OrganizationUnitLevelUpdate,
    db: AsyncSession = Depends(get_session),
):
    """
    Update an organization level by ID (partial update).
    Returns 404 if not found.
    """

    result = await db.execute(select(OrganizationLevel).where(OrganizationLevel.id == id))
    existing = result.scalar_one_or_none()

    if not existing:
        raise HTTPException(status_code=404, detail="Organization level not found")

    updates = payload.model_dump(exclude_unset=True)
    for k, v in updates.items():
        if v is not None:
            setattr(existing, k, v)

    await db.commit()
    await db.refresh(existing)
    return existing


# -------------------------------------------------------------------
# DELETE ORGANIZATION LEVEL
# -------------------------------------------------------------------
@apiRouter.delete(
    "/organization_levels/{id}",
    dependencies=[Depends(get_current_active_user)],
)
async def delete_organization_level(
    id: str,
    db: AsyncSession = Depends(get_session),
):
    """
    Delete an organization level by ID.
    Returns 404 if not found.
    """

    result = await db.execute(select(OrganizationLevel).where(OrganizationLevel.id == id))
    existing = result.scalar_one_or_none()

    if not existing:
        raise HTTPException(status_code=404, detail="Organization level not found")

    await db.delete(existing)
    await db.commit()

    return {"detail": "Organization level deleted successfully"}

# -------------------------------------------------------------------
# GET ALL ORGANIZATION LEVELS
# -------------------------------------------------------------------
@apiRouter.get(
    "/organization_levels",
    response_model=list[OrganizationUnitLevelRead],
    dependencies=[Depends(get_current_active_user)],
)
async def get_OrganisationLevels(db: AsyncSession = Depends(get_session)):
    """
    Retrieve all organization levels from the database.

    Security:
        - Requires authenticated active user.

    Process:
        1. Execute raw SQL query to fetch all records
           from organization_level table.
        2. Convert results into dictionary mappings.
        3. Return the list of organization levels.

    Args:
        db (AsyncSession): Injected database session.

    Returns:
        List[OrganizationUnitLevelRead]: List of organization levels.
    """
    result = await db.execute(text("""
        SELECT *
        FROM organization_level                                      
    """))
    rows = result.mappings().all()
    return rows


# -------------------------------------------------------------------
# GET ORGANIZATION LEVEL BY ID
# -------------------------------------------------------------------
@apiRouter.get(
    "/organization_levels/{id}",
    response_model=OrganizationUnitLevelRead,
    dependencies=[Depends(get_current_active_user)],
)
async def get_OrganisationLevel(id: str, db: AsyncSession = Depends(get_session)):
    """
    Retrieve a specific organization level by its unique ID.

    Security:
        - Requires authenticated active user.

    Process:
        1. Execute raw SQL query filtered by ID.
        2. Convert result into dictionary mappings.
        3. If no record found → return HTTP 404.
        4. Otherwise return the first matching record.

    Args:
        id (str): Unique identifier of the organization level.
        db (AsyncSession): Injected database session.

    Raises:
        HTTPException:
            - 404 if the organization level does not exist.

    Returns:
        OrganizationUnitLevelRead: Organization level record.
    """
    result = await db.execute(
    text("""
        SELECT *
        FROM organization_level
        WHERE id = :id
    """),
    {"id": id})
    rows = result.mappings().all()

    # If no matching record is found, return HTTP 404
    if len(rows) == 0:
        raise HTTPException(status_code=404, detail="Organization level not found")

    return rows[0]