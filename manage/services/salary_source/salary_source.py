

from manage.models import HippoSalarySource
from manage.services.salary_source.schemas import HippoSalarySourceRead, HippoSalarySourceCreate, HippoSalarySourceUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user


apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

# Get all sources
@apiRouter.get("/salary_sources/", response_model=list[HippoSalarySourceRead], dependencies=[Depends(get_current_active_user)],)
async def get_sources(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoSalarySource).order_by(HippoSalarySource.name))
    sources = result.scalars().all()
    return sources


# find a Cadre by id
@apiRouter.get("/salary_sources/{cadre_id}", response_model=HippoSalarySourceRead, dependencies=[Depends(get_current_active_user)],)
async def get_Cadre(cadre_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoSalarySource).where(HippoSalarySource.id == cadre_id))
    Cadre = result.scalar_one_or_none()
    if not Cadre:
        raise HTTPException(status_code=404, detail="Cadre not found")
    return Cadre

@apiRouter.post("/salary_sources/", response_model=HippoSalarySourceRead, dependencies=[Depends(get_current_active_user)])
async def create_Cadre(
    Cadre:HippoSalarySourceCreate,
    session: AsyncSession = Depends(get_session),
):
    Cadre_data = Cadre.dict()  # get dict from pydantic model
    Cadre_data['id'] = f"cadre|{Cadre.name}"
    
    new_Cadre = HippoSalarySource(**Cadre_data)
    session.add(new_Cadre)
    await session.commit()
    await session.refresh(new_Cadre)
    return new_Cadre

# update an existing Cadre
@apiRouter.put("/salary_sources/{cadre_id}", response_model=HippoSalarySourceRead)
async def update_Cadre(cadre_id: str, Cadre:HippoSalarySourceUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoSalarySource).where(HippoSalarySource.id == cadre_id))
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
@apiRouter.delete("/salary_sources/{cadre_id}")
async def delete_Cadre(cadre_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoSalarySource).where(HippoSalarySource.id == cadre_id))
    existing_Cadre = result.scalar_one_or_none()
    if not existing_Cadre:
        raise HTTPException(status_code=404, detail="Cadre not found")
    
    await session.delete(existing_Cadre)
    await session.commit()
    return {"detail": "Cadre deleted successfully"}
