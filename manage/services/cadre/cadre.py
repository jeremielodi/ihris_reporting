

from manage.models import HippoCadre, HippoEntityMap
from manage.services.cadre.schemas import HippoCadreRead, HippoCadreCreate, HippoCadreUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user
from sqlalchemy.dialects.postgresql import insert as pg_insert
from manage.services.entity_map import entity_map


apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

# Get all cadres
@apiRouter.get("/cadres/", response_model=list[HippoCadreRead], dependencies=[Depends(get_current_active_user)],)
async def get_cadres(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoCadre).order_by(HippoCadre.name))
    cadres = result.scalars().all()
    return cadres


# find a Cadre by id
@apiRouter.get("/cadres/{cadre_id}", response_model=HippoCadreRead, dependencies=[Depends(get_current_active_user)],)
async def get_Cadre(cadre_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoCadre).where(HippoCadre.id == cadre_id))
    Cadre = result.scalar_one_or_none()
    if not Cadre:
        raise HTTPException(status_code=404, detail="Cadre not found")
    return Cadre

@apiRouter.post("/cadres/", response_model=HippoCadreRead, dependencies=[Depends(get_current_active_user)])
async def create_Cadre(
    Cadre:HippoCadreCreate,
    session: AsyncSession = Depends(get_session),
):
    Cadre_data = Cadre.dict()  # get dict from pydantic model
    Cadre_data['id'] = f"cadre|{Cadre.name}"
    
    new_Cadre = HippoCadre(**Cadre_data)
    session.add(new_Cadre)
    await session.commit()
    await session.refresh(new_Cadre)
    return new_Cadre



# --- new BULK endpoint ---
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
    if not cadres:
        raise HTTPException(status_code=400, detail="Empty payload.")

    # Normalize payload -> list of dicts
    maxNumber = await entity_map.getMaxNumber("cadre", session)
    maxNumber = maxNumber + 1

    rows = []
    cadreId = None
    for item in cadres:
        try:
            data = item.model_dump()
        except AttributeError:
            data = item.dict()

        # generate id the same way as single-create
        cadreId = f"cadre|{maxNumber}"
        data["id"] = cadreId
        rows.append(data)
        maxNumber += 1

    # Postgres bulk insert with ON CONFLICT DO NOTHING + RETURNING
    # Choose the unique/PK column for conflict target (id here).
    stmt = (
        pg_insert(HippoCadre.__table__)
        .values(rows)
        .on_conflict_do_nothing(index_elements=["id"])
        .returning(*HippoCadre.__table__.c)  # return inserted rows
    )

    result = await session.execute(stmt)
    inserted = result.mappings().all()  # list[Mapping]

    new_entity_map = HippoEntityMap(id=  cadreId, entity_type="cadre", max_number=maxNumber)
    session.add(new_entity_map)

    # Commit once for the whole batch
    await session.commit()

    # If some were duplicates, they won’t be returned by RETURNING (do-nothing).
    # We still return what was actually inserted.
    # Convert MappingRow -> dict for Pydantic response_model
    return [dict(row) for row in inserted]

# update an existing Cadre
@apiRouter.put("/cadres/{cadre_id}", response_model=HippoCadreRead)
async def update_Cadre(cadre_id: str, Cadre:HippoCadreUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoCadre).where(HippoCadre.id == cadre_id))
    existing_Cadre = result.scalar_one_or_none()
    if not existing_Cadre:
        raise HTTPException(status_code=404, detail="Cadre not found")
    
    for key, value in Cadre.dict().items():
        if value is not None:
            setattr(existing_Cadre, key, value)
    
    await session.commit()
    await session.refresh(existing_Cadre)
    return existing_Cadre  

# delete a Cadre
@apiRouter.delete("/cadres/{cadre_id}")
async def delete_Cadre(cadre_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoCadre).where(HippoCadre.id == cadre_id))
    existing_Cadre = result.scalar_one_or_none()
    if not existing_Cadre:
        raise HTTPException(status_code=404, detail="Cadre not found")
    
    await session.delete(existing_Cadre)
    await session.commit()
    return {"detail": "Cadre deleted successfully"}
