

from manage.models import HippoPersonIdentification
from manage.services.identification.schemas import HippoPersonIdentificationRead, HippoPersonIdentificationCreate, HippoPersonIdentificationUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user
from sqlalchemy import text

apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

# Get all identifications
@apiRouter.get("/identifications/", response_model=list[HippoPersonIdentificationRead], dependencies=[Depends(get_current_active_user)],)
async def get_identifications(persion_id:str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoPersonIdentification))
    identifications = result.scalars().all()
    return identifications


# Get all identifications
@apiRouter.get("/identifications/person/{persion_id}", response_model=list[HippoPersonIdentificationRead], dependencies=[Depends(get_current_active_user)],)
async def get_identifications(persion_id:str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(text(
        f"""
            SELECT i.* ,
                it.name as type_name,
                c.name as country_name
            FROM hippo_person_identification as  i 
            JOIN hippo_identification_type it ON it.id = i.type_id
            LEFT JOIN hippo_country c ON c.id = i.country
            WHERE i.person_id='{persion_id}'
            
        """
    ))
    identifications = result.mappings().all()
    return identifications


# find a Identification by id
@apiRouter.get("/identifications/{identification_id}", response_model=HippoPersonIdentificationRead, dependencies=[Depends(get_current_active_user)],)
async def get_Identification(identification_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoPersonIdentification).where(HippoPersonIdentification.id == identification_id))
    Identification = result.scalar_one_or_none()
    if not Identification:
        raise HTTPException(status_code=404, detail="Identification not found")
    return Identification

@apiRouter.post("/identifications/", response_model=HippoPersonIdentificationRead, dependencies=[Depends(get_current_active_user)])
async def create_Identification(
    Identification:HippoPersonIdentificationCreate,
    session: AsyncSession = Depends(get_session),
):
    Identification_data = Identification.dict()  # get dict from pydantic model
    Identification_data['id'] = f"identification|{Identification.person_id}|{Identification.number}"
    
    new_Identification = HippoPersonIdentification(**Identification_data)
    session.add(new_Identification)
    await session.commit()
    await session.refresh(new_Identification)
    return new_Identification

# update an existing Identification
@apiRouter.put("/identifications/{identification_id}", response_model=HippoPersonIdentificationRead)
async def update_Identification(identification_id: str, Identification:HippoPersonIdentificationUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoPersonIdentification).where(HippoPersonIdentification.id == identification_id))
    existing_Identification = result.scalar_one_or_none()
    if not existing_Identification:
        raise HTTPException(status_code=404, detail="Identification not found")
    
    for key, value in Identification.dict().items():
        if (value is not None) and (key !='created'):
            setattr(existing_Identification, key, value)
    
    await session.commit()
    await session.refresh(existing_Identification)
    return existing_Identification  

# delete a Identification
@apiRouter.delete("/identifications/{identification_id}")
async def delete_Identification(identification_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoPersonIdentification).where(HippoPersonIdentification.id == identification_id))
    existing_Identification = result.scalar_one_or_none()
    if not existing_Identification:
        raise HTTPException(status_code=404, detail="Identification not found")
    
    await session.delete(existing_Identification)
    await session.commit()
    return {"detail": "Identification deleted successfully"}


