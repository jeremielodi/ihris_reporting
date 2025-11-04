

from manage.models import HippoIdentificationType
from manage.services.identification_type.schemas import HippoIdentificationTypeRead, HippoIdentificationTypeCreate, HippoIdentificationTypeUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user


apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

# Get all identification_types
@apiRouter.get("/identification_types/", response_model=list[HippoIdentificationTypeRead], dependencies=[Depends(get_current_active_user)],)
async def get_identification_types(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoIdentificationType).order_by(HippoIdentificationType.name))
    identification_types = result.scalars().all()
    return identification_types


# find a Identification_type by id
@apiRouter.get("/identification_types/{identification_type_id}", response_model=HippoIdentificationTypeRead, dependencies=[Depends(get_current_active_user)],)
async def get_Identification_type(identification_type_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoIdentificationType).where(HippoIdentificationType.id == identification_type_id))
    Identification_type = result.scalar_one_or_none()
    if not Identification_type:
        raise HTTPException(status_code=404, detail="Identification_type not found")
    return Identification_type

@apiRouter.post("/identification_types/", response_model=HippoIdentificationTypeRead, dependencies=[Depends(get_current_active_user)])
async def create_Identification_type(
    Identification_type:HippoIdentificationTypeCreate,
    session: AsyncSession = Depends(get_session),
):
    Identification_type_data = Identification_type.dict()  # get dict from pydantic model
    Identification_type_data['id'] = f"identification_type|{Identification_type.name}"
    
    new_Identification_type = HippoIdentificationType(**Identification_type_data)
    session.add(new_Identification_type)
    await session.commit()
    await session.refresh(new_Identification_type)
    return new_Identification_type

# update an existing Identification_type
@apiRouter.put("/identification_types/{identification_type_id}", response_model=HippoIdentificationTypeRead)
async def update_Identification_type(identification_type_id: str, Identification_type:HippoIdentificationTypeUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoIdentificationType).where(HippoIdentificationType.id == identification_type_id))
    existing_Identification_type = result.scalar_one_or_none()
    if not existing_Identification_type:
        raise HTTPException(status_code=404, detail="Identification_type not found")
    
    for key, value in Identification_type.dict().items():
        if value is not None:
            setattr(existing_Identification_type, key, value)
    
    await session.commit()
    await session.refresh(existing_Identification_type)
    return existing_Identification_type  

# delete a Identification_type
@apiRouter.delete("/identification_types/{identification_type_id}")
async def delete_Identification_type(identification_type_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoIdentificationType).where(HippoIdentificationType.id == identification_type_id))
    existing_Identification_type = result.scalar_one_or_none()
    if not existing_Identification_type:
        raise HTTPException(status_code=404, detail="Identification_type not found")
    
    await session.delete(existing_Identification_type)
    await session.commit()
    return {"detail": "Identification_type deleted successfully"}


