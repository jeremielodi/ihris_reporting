

from manage.models import HippoContactType
from manage.services.contact_type.schemas import HippoContactTypeRead, HippoContactTypeCreate, HippoContactTypeUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user


apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

# Get all contact_types
@apiRouter.get("/contact_types/", response_model=list[HippoContactTypeRead], dependencies=[Depends(get_current_active_user)],)
async def get_contact_types(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoContactType).order_by(HippoContactType.name))
    contact_types = result.scalars().all()
    return contact_types


# find a Contact_type by id
@apiRouter.get("/contact_types/{contact_type_id}", response_model=HippoContactTypeRead, dependencies=[Depends(get_current_active_user)],)
async def get_Contact_type(contact_type_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoContactType).where(HippoContactType.id == contact_type_id))
    Contact_type = result.scalar_one_or_none()
    if not Contact_type:
        raise HTTPException(status_code=404, detail="Contact_type not found")
    return Contact_type

@apiRouter.post("/contact_types/", response_model=HippoContactTypeRead, dependencies=[Depends(get_current_active_user)])
async def create_Contact_type(
    Contact_type:HippoContactTypeCreate,
    session: AsyncSession = Depends(get_session),
):
    Contact_type_data = Contact_type.dict()  # get dict from pydantic model
    Contact_type_data['id'] = f"contact_type|{Contact_type.name}"
    
    new_Contact_type = HippoContactType(**Contact_type_data)
    session.add(new_Contact_type)
    await session.commit()
    await session.refresh(new_Contact_type)
    return new_Contact_type

# update an existing Contact_type
@apiRouter.put("/contact_types/{contact_type_id}", response_model=HippoContactTypeRead)
async def update_Contact_type(contact_type_id: str, Contact_type:HippoContactTypeUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoContactType).where(HippoContactType.id == contact_type_id))
    existing_Contact_type = result.scalar_one_or_none()
    if not existing_Contact_type:
        raise HTTPException(status_code=404, detail="Contact_type not found")
    
    for key, value in Contact_type.dict().items():
        if value is not None:
            setattr(existing_Contact_type, key, value)
    
    await session.commit()
    await session.refresh(existing_Contact_type)
    return existing_Contact_type  

# delete a Contact_type
@apiRouter.delete("/contact_types/{contact_type_id}")
async def delete_Contact_type(contact_type_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoContactType).where(HippoContactType.id == contact_type_id))
    existing_Contact_type = result.scalar_one_or_none()
    if not existing_Contact_type:
        raise HTTPException(status_code=404, detail="Contact_type not found")
    
    await session.delete(existing_Contact_type)
    await session.commit()
    return {"detail": "Contact_type deleted successfully"}


