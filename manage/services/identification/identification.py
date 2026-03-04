# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

# ORM model
from manage.models import HippoPersonIdentification

# Pydantic schemas (validation + serialization)
from manage.services.identification.schemas import (
    HippoPersonIdentificationRead,
    HippoPersonIdentificationCreate,
    HippoPersonIdentificationUpdate
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

# Raw SQL execution
from sqlalchemy import text


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
# GET ALL IDENTIFICATIONS
# =========================================================

@apiRouter.get(
    "/identifications/",
    response_model=list[HippoPersonIdentificationRead],
    dependencies=[Depends(get_current_active_user)],
)
async def get_all_identifications(session: AsyncSession = Depends(get_session)):
    """
    Retrieve all person identifications.

    NOTE:
    This returns all records (consider pagination in production).
    """
    result = await session.execute(select(HippoPersonIdentification))
    identifications = result.scalars().all()
    return identifications


# =========================================================
# GET IDENTIFICATIONS BY PERSON ID
# =========================================================

@apiRouter.get(
    "/identifications/person/{person_id}",
    response_model=list,
    dependencies=[Depends(get_current_active_user)],
)
async def get_person_identifications(
    person_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieve all identifications for a specific person.

    Includes:
    - Identification type name
    - Country name

    ⚠️ Current query uses f-string interpolation (SQL injection risk).
    In production, replace with parameterized query.
    """

    result = await session.execute(text(f"""
        SELECT i.*,
               it.name AS type_name,
               c.name AS country_name
        FROM hippo_person_identification AS i
        JOIN hippo_identification_type it ON it.id = i.type_id
        LEFT JOIN hippo_country c ON c.id = i.country
        WHERE i.person_id = :person_id
    """), {"person_id": person_id})

    identifications = result.mappings().all()
    return identifications


# =========================================================
# GET IDENTIFICATION BY ID
# =========================================================

@apiRouter.get(
    "/identifications/{identification_id}",
    response_model=HippoPersonIdentificationRead,
    dependencies=[Depends(get_current_active_user)],
)
async def get_identification(
    identification_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieve a specific identification record by ID.
    Returns 404 if not found.
    """

    result = await session.execute(
        select(HippoPersonIdentification).where(
            HippoPersonIdentification.id == identification_id
        )
    )

    identification = result.scalar_one_or_none()

    if not identification:
        raise HTTPException(status_code=404, detail="Identification not found")

    return identification


# =========================================================
# CREATE IDENTIFICATION
# =========================================================

@apiRouter.post(
    "/identifications/",
    response_model=HippoPersonIdentificationRead,
    dependencies=[Depends(get_current_active_user)]
)
async def create_identification(
    identification: HippoPersonIdentificationCreate,
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new identification record for a person.

    ID format:
        identification|<person_id>|<number>

    ⚠️ Ensure number uniqueness per person in production.
    """

    identification_data = identification.dict()

    # Generate composite ID
    identification_data['id'] = (
        f"identification|{identification.person_id}|{identification.number}"
    )

    new_identification = HippoPersonIdentification(**identification_data)

    session.add(new_identification)
    await session.commit()
    await session.refresh(new_identification)

    print(new_identification)
    return new_identification


# =========================================================
# UPDATE IDENTIFICATION
# =========================================================

@apiRouter.put(
    "/identifications/{identification_id}",
    response_model=HippoPersonIdentificationRead
)
async def update_identification(
    identification_id: str,
    identification: HippoPersonIdentificationUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    Update an existing identification.

    - Only non-null fields are updated.
    - 'created' field is protected.
    """

    result = await session.execute(
        select(HippoPersonIdentification).where(
            HippoPersonIdentification.id == identification_id
        )
    )

    existing_identification = result.scalar_one_or_none()

    if not existing_identification:
        raise HTTPException(status_code=404, detail="Identification not found")

    for key, value in identification.dict().items():
        if value is not None and key != 'created':
            setattr(existing_identification, key, value)

    await session.commit()
    await session.refresh(existing_identification)

    return existing_identification


# =========================================================
# DELETE IDENTIFICATION
# =========================================================

@apiRouter.delete("/identifications/{identification_id}")
async def delete_identification(
    identification_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete an identification record.

    ⚠️ Consider soft-delete in production HR systems.
    """

    result = await session.execute(
        select(HippoPersonIdentification).where(
            HippoPersonIdentification.id == identification_id
        )
    )

    existing_identification = result.scalar_one_or_none()

    if not existing_identification:
        raise HTTPException(status_code=404, detail="Identification not found")

    await session.delete(existing_identification)
    await session.commit()

    return {"detail": "Identification deleted successfully"}