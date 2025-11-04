

from manage.models import HippoInstitutionType
from manage.services.institution_type.schemas import HippoInstitutionTypeRead, HippoInstitutionTypeCreate, HippoInstitutionTypeUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user


apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

# Get all institution_types
@apiRouter.get("/institution_types/", response_model=list[HippoInstitutionTypeRead], dependencies=[Depends(get_current_active_user)],)
async def get_institution_types(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoInstitutionType).order_by(HippoInstitutionType.name))
    institution_types = result.scalars().all()
    return institution_types


# find a Institution_type by id
@apiRouter.get("/institution_types/{institution_type_id}", response_model=HippoInstitutionTypeRead, dependencies=[Depends(get_current_active_user)],)
async def get_Institution_type(institution_type_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoInstitutionType).where(HippoInstitutionType.id == institution_type_id))
    Institution_type = result.scalar_one_or_none()
    if not Institution_type:
        raise HTTPException(status_code=404, detail="Institution_type not found")
    return Institution_type

@apiRouter.post("/institution_types/", response_model=HippoInstitutionTypeRead, dependencies=[Depends(get_current_active_user)])
async def create_Institution_type(
    Institution_type:HippoInstitutionTypeCreate,
    session: AsyncSession = Depends(get_session),
):
    Institution_type_data = Institution_type.dict()  # get dict from pydantic model
    Institution_type_data['id'] = f"institution_type|{Institution_type.name}"
    
    new_Institution_type = HippoInstitutionType(**Institution_type_data)
    session.add(new_Institution_type)
    await session.commit()
    await session.refresh(new_Institution_type)
    return new_Institution_type

# update an existing Institution_type
@apiRouter.put("/institution_types/{institution_type_id}", response_model=HippoInstitutionTypeRead)
async def update_Institution_type(institution_type_id: str, Institution_type:HippoInstitutionTypeUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoInstitutionType).where(HippoInstitutionType.id == institution_type_id))
    existing_Institution_type = result.scalar_one_or_none()
    if not existing_Institution_type:
        raise HTTPException(status_code=404, detail="Institution_type not found")
    
    for key, value in Institution_type.dict().items():
        if value is not None:
            setattr(existing_Institution_type, key, value)
    
    await session.commit()
    await session.refresh(existing_Institution_type)
    return existing_Institution_type  

# delete a Institution_type
@apiRouter.delete("/institution_types/{institution_type_id}")
async def delete_Institution_type(institution_type_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoInstitutionType).where(HippoInstitutionType.id == institution_type_id))
    existing_Institution_type = result.scalar_one_or_none()
    if not existing_Institution_type:
        raise HTTPException(status_code=404, detail="Institution_type not found")
    
    await session.delete(existing_Institution_type)
    await session.commit()
    return {"detail": "Institution_type deleted successfully"}


