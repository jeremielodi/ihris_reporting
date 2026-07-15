# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

# Used to generate unique identifiers for contacts
import uuid

# ORM model
from manage.models import HippoContact

# Pydantic schemas (validation & serialization)
from manage.services.contact.schemas import (
    HippoContactRead,
    HippoContactCreate,
    HippoContactUpdate
)

# Async DB session
from sqlalchemy.ext.asyncio import AsyncSession

# FastAPI utilities
from fastapi import APIRouter, Depends, HTTPException

# SQLAlchemy query builder
from sqlalchemy.future import select

# Database session factory
from manage.database import SessionLocal, engine

# Authentication dependency
from endpoints.user_api import get_current_active_user

# (Currently unused import — consider removing if not needed)
import models.usercrud as user_crud


# Create API router
apiRouter = APIRouter()


# ---------------------------------------------------------
# Dependency: Get Async Database Session
# ---------------------------------------------------------
async def get_session() -> AsyncSession:
    """
    Provides an async database session to endpoints.
    Ensures proper session lifecycle handling.
    """
    async with SessionLocal() as session:
        yield session


# ---------------------------------------------------------
# GET ALL CONTACTS
# ---------------------------------------------------------
@apiRouter.get(
    "/contacts/",
    response_model=list[HippoContactRead],
    dependencies=[Depends(get_current_active_user)],
)
async def get_contacts(session: AsyncSession = Depends(get_session)):
    """
    Retrieve all contacts.
    Requires authenticated user.
    """
    result = await session.execute(select(HippoContact))
    contacts = result.scalars().all()
    return contacts


# ---------------------------------------------------------
# GET CONTACTS BY PERSON ID
# ---------------------------------------------------------
@apiRouter.get(
    "/contacts/person/{persion_id}",
    response_model=list[HippoContactRead],
    dependencies=[Depends(get_current_active_user)],
)
async def get_personContacts(
    persion_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieve all contacts linked to a specific person.
    """
    result = await session.execute(
        select(HippoContact).where(
            HippoContact.person_id == persion_id
        )
    )
    contacts = result.scalars().all()
    return contacts


# ---------------------------------------------------------
# GET CONTACT BY ID
# ---------------------------------------------------------
@apiRouter.get(
    "/contacts/{contact_id}",
    response_model=HippoContactRead,
    dependencies=[Depends(get_current_active_user)],
)
async def get_Contact(
    contact_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieve a single Contact by ID.
    Returns 404 if not found.
    """
    result = await session.execute(
        select(HippoContact).where(
            HippoContact.id == contact_id
        )
    )

    Contact = result.scalar_one_or_none()

    if not Contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    return Contact


# ---------------------------------------------------------
# CREATE CONTACT
# ---------------------------------------------------------
@apiRouter.post(
    "/contacts/",
    response_model=HippoContactRead,
    dependencies=[Depends(get_current_active_user)]
)
async def create_Contact(
    Contact: HippoContactCreate,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_active_user),
):
    """
    Create a new Contact.

    - Generates a UUID as primary key.
    - Stores the user who created the record.
    """

    # Convert Pydantic model to dictionary
    Contact_data = Contact.model_dump()

    # Generate unique ID
    Contact_data['id'] = uuid.uuid4()

    # Track audit information
    Contact_data['created_by'] = current_user_id

    # Create ORM instance
    new_Contact = HippoContact(**Contact_data)

    # Persist to database
    session.add(new_Contact)
    await session.commit()
    await session.refresh(new_Contact)

    return new_Contact


# ---------------------------------------------------------
# UPDATE CONTACT
# ---------------------------------------------------------
@apiRouter.put(
    "/contacts/{contact_id}",
    response_model=HippoContactRead
)
async def update_Contact(
    contact_id: str,
    Contact: HippoContactUpdate,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_active_user),
):
    """
    Update an existing Contact.

    - Only non-null fields are updated.
    - 'created' field is protected.
    - Tracks the user who modified the record.
    """

    result = await session.execute(
        select(HippoContact).where(
            HippoContact.id == contact_id
        )
    )

    existing_Contact = result.scalar_one_or_none()

    if not existing_Contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    # Update provided fields dynamically
    for key, value in Contact.model_dump().items():
        if value is not None and key != 'created':
            setattr(existing_Contact, key, value)

    # Audit: track last modification user
    setattr(existing_Contact, "last_modified_by", current_user_id)

    await session.commit()
    await session.refresh(existing_Contact)

    return existing_Contact


# ---------------------------------------------------------
# DELETE CONTACT
# ---------------------------------------------------------
@apiRouter.delete("/contacts/{contact_id}")
async def delete_Contact(
    contact_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete a Contact by ID.
    Returns 404 if not found.
    """

    result = await session.execute(
        select(HippoContact).where(
            HippoContact.id == contact_id
        )
    )

    existing_Contact = result.scalar_one_or_none()

    if not existing_Contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    await session.delete(existing_Contact)
    await session.commit()

    return {"detail": "Contact deleted successfully"}