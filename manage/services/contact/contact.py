import uuid
from manage.models import HippoContact
from manage.services.contact.schemas import HippoContactRead, HippoContactCreate, HippoContactUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user
import  models.usercrud as user_crud

apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

# Get all contacts
@apiRouter.get("/contacts/", response_model=list[HippoContactRead], dependencies=[Depends(get_current_active_user)],)
async def get_contacts(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoContact))
    contacts = result.scalars().all()
    return contacts

@apiRouter.get("/contacts/person/{persion_id}", response_model=list[HippoContactRead], dependencies=[Depends(get_current_active_user)],)
async def get_personContacts(persion_id:str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoContact).where(HippoContact.person_id == persion_id))
    contacts = result.scalars().all()
    return contacts

# find a Contact by id
@apiRouter.get("/contacts/{contact_id}", response_model=HippoContactRead, dependencies=[Depends(get_current_active_user)],)
async def get_Contact(contact_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoContact).where(HippoContact.id == contact_id))
    Contact = result.scalar_one_or_none()
    if not Contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return Contact

@apiRouter.post("/contacts/", response_model=HippoContactRead, dependencies=[Depends(get_current_active_user)])
async def create_Contact(
    Contact:HippoContactCreate,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_active_user),
):
    
    Contact_data = Contact.dict()  # get dict from pydantic model
    Contact_data['id'] = uuid.uuid4()
    Contact_data['created_by'] = current_user_id
    new_Contact = HippoContact(**Contact_data)
    session.add(new_Contact)
    await session.commit()
    await session.refresh(new_Contact)
    return new_Contact

# update an existing Contact
@apiRouter.put("/contacts/{contact_id}", response_model=HippoContactRead)
async def update_Contact(
    contact_id: str, 
    Contact:HippoContactUpdate, 
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_active_user),
    ):
    result = await session.execute(select(HippoContact).where(HippoContact.id == contact_id))
    existing_Contact = result.scalar_one_or_none()
    if not existing_Contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    for key, value in Contact.dict().items():
        if value is not None and key != 'created':
            setattr(existing_Contact, key, value)
       ## getting current user
    
    setattr(existing_Contact, "last_modified_by", current_user_id)

    await session.commit()
    await session.refresh(existing_Contact)
    return existing_Contact  

# delete a Contact
@apiRouter.delete("/contacts/{contact_id}")
async def delete_Contact(contact_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoContact).where(HippoContact.id == contact_id))
    existing_Contact = result.scalar_one_or_none()
    if not existing_Contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    await session.delete(existing_Contact)
    await session.commit()
    return {"detail": "Contact deleted successfully"}


