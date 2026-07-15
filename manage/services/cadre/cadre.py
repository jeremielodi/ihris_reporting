# Import ORM models
from manage.models import HippoCadre, HippoEntityMap

# Import Pydantic schemas for request/response validation
from manage.services.cadre.schemas import HippoCadreRead, HippoCadreCreate, HippoCadreUpdate

# Async database session
from sqlalchemy.ext.asyncio import AsyncSession

# FastAPI utilities
from fastapi import APIRouter, Depends, HTTPException, status

# SQLAlchemy query builder
from sqlalchemy.future import select

# Database session factory
from manage.database import SessionLocal, engine

# Authentication dependency
from endpoints.user_api import get_current_active_user

# PostgreSQL-specific insert (for bulk insert with conflict handling)
from sqlalchemy.dialects.postgresql import insert as pg_insert

# Service used to generate incremental entity numbers
from manage.services.entity_map import entity_map


# Create API router instance
apiRouter = APIRouter()


# ---------------------------------------------------------
# Dependency: Get async database session
# ---------------------------------------------------------
async def get_session() -> AsyncSession:
    """
    Provides an async database session to endpoints.
    Ensures proper session lifecycle management.
    """
    async with SessionLocal() as session:
        yield session


# ---------------------------------------------------------
# GET ALL CADRES
# ---------------------------------------------------------
@apiRouter.get(
    "/cadres/",
    response_model=list[HippoCadreRead],
    dependencies=[Depends(get_current_active_user)],
)
async def get_cadres(session: AsyncSession = Depends(get_session)):
    """
    Retrieve all cadres ordered alphabetically by name.
    Requires authenticated user.
    """
    result = await session.execute(
        select(HippoCadre).order_by(HippoCadre.name)
    )
    cadres = result.scalars().all()
    return cadres


# ---------------------------------------------------------
# GET CADRE BY ID
# ---------------------------------------------------------
@apiRouter.get(
    "/cadres/{cadre_id}",
    response_model=HippoCadreRead,
    dependencies=[Depends(get_current_active_user)],
)
async def get_Cadre(cadre_id: str, session: AsyncSession = Depends(get_session)):
    """
    Retrieve a single Cadre by its unique ID.
    Returns 404 if not found.
    """
    result = await session.execute(
        select(HippoCadre).where(HippoCadre.id == cadre_id)
    )
    Cadre = result.scalar_one_or_none()

    if not Cadre:
        raise HTTPException(status_code=404, detail="Cadre not found")

    return Cadre


# ---------------------------------------------------------
# CREATE SINGLE CADRE
# ---------------------------------------------------------
@apiRouter.post(
    "/cadres/",
    response_model=HippoCadreRead,
    dependencies=[Depends(get_current_active_user)]
)
async def create_Cadre(
    Cadre: HippoCadreCreate,
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new Cadre.
    The ID is generated using format: 'cadre|<Cadre.name>'.
    """
    # Convert Pydantic model to dictionary
    Cadre_data = Cadre.model_dump()

    # Generate custom ID
    Cadre_data['id'] = f"cadre|{Cadre.name}"

    # Create ORM object
    new_Cadre = HippoCadre(**Cadre_data)

    # Persist to database
    session.add(new_Cadre)
    await session.commit()
    await session.refresh(new_Cadre)

    return new_Cadre


# ---------------------------------------------------------
# BULK IMPORT CADRES
# ---------------------------------------------------------
@apiRouter.post(
    "/cadres/import",
    response_model=list[HippoCadreRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_user)]
)
async def bulk_create_classifications(
    cadres: list[HippoCadreCreate],
    session: AsyncSession = Depends(get_session),
):
    """
    Bulk insert Cadres.
    - Automatically generates incremental IDs using entity_map.
    - Uses PostgreSQL ON CONFLICT DO NOTHING to avoid duplicates.
    - Returns only successfully inserted records.
    """

    # Validate payload
    if not cadres:
        raise HTTPException(status_code=400, detail="Empty payload.")

    # Get next incremental number from entity_map service
    maxNumber = await entity_map.getMaxNumber("cadre", session)
    maxNumber = maxNumber + 1

    rows = []
    cadreId = None

    # Prepare rows for bulk insertion
    for item in cadres:
        data = item.model_dump()

        # Generate sequential ID (cadre|<number>)
        cadreId = f"cadre|{maxNumber}"
        data["id"] = cadreId

        rows.append(data)
        maxNumber += 1

    # PostgreSQL bulk insert with conflict handling
    stmt = (
        pg_insert(HippoCadre.__table__)
        .values(rows)
        .on_conflict_do_nothing(index_elements=["id"])  # ignore duplicates
        .returning(*HippoCadre.__table__.c)             # return inserted rows
    )

    result = await session.execute(stmt)
    inserted = result.mappings().all()  # rows actually inserted

    # Update entity_map with new max number
    new_entity_map = HippoEntityMap(
        id=cadreId,
        entity_type="cadre",
        max_number=maxNumber
    )
    session.add(new_entity_map)

    # Commit entire batch in one transaction
    await session.commit()

    # Return only inserted rows
    return [dict(row) for row in inserted]


# ---------------------------------------------------------
# UPDATE CADRE
# ---------------------------------------------------------
@apiRouter.put("/cadres/{cadre_id}", response_model=HippoCadreRead)
async def update_Cadre(
    cadre_id: str,
    Cadre: HippoCadreUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    Update an existing Cadre.
    Only non-null fields will be updated.
    Returns 404 if Cadre does not exist.
    """

    result = await session.execute(
        select(HippoCadre).where(HippoCadre.id == cadre_id)
    )
    existing_Cadre = result.scalar_one_or_none()

    if not existing_Cadre:
        raise HTTPException(status_code=404, detail="Cadre not found")

    # Update only provided fields
    for key, value in Cadre.model_dump().items():
        if value is not None:
            setattr(existing_Cadre, key, value)

    await session.commit()
    await session.refresh(existing_Cadre)

    return existing_Cadre


# ---------------------------------------------------------
# DELETE CADRE
# ---------------------------------------------------------
@apiRouter.delete("/cadres/{cadre_id}")
async def delete_Cadre(
    cadre_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete a Cadre by ID.
    Returns 404 if not found.
    """

    result = await session.execute(
        select(HippoCadre).where(HippoCadre.id == cadre_id)
    )
    existing_Cadre = result.scalar_one_or_none()

    if not existing_Cadre:
        raise HTTPException(status_code=404, detail="Cadre not found")

    await session.delete(existing_Cadre)
    await session.commit()

    return {"detail": "Cadre deleted successfully"}