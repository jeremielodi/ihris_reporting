# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

# ORM models
from datetime import date, datetime

# Importer delete de SQLAlchemy (pas de requests)
from sqlalchemy import delete

from manage.models import HippoSpecialityPerson, HippoSpeciality, HippoPerson, HippoEntityMap, HippoAuditLog

# Pydantic schemas for People
from manage.services.people.schemas import (
    HippoPersonCreate,
    HippoPersonUpdate,
    HippoPersonRead,
    PeopelQueryParameters
)
from manage.services.speciality.schemas import HippoSpecialityRead

# Async database session support
from sqlalchemy.ext.asyncio import AsyncSession

# FastAPI utilities
from fastapi import APIRouter, Depends, HTTPException

# SQLAlchemy ORM query builder
from sqlalchemy.future import select
from fastapi import Depends

# Database session factory
from manage.database import SessionLocal, engine

# Authentication dependency
from endpoints.user_api import get_current_active_user

# Service used to generate incremental numbers
from manage.services.entity_map import entity_map

# Raw SQL execution helper
from sqlalchemy import text

# Utility to generate consistent IDs
from manage.utils import generate_unit_id

# UUID for audit log identifiers
import uuid

# Create router instance
apiRouter = APIRouter()


# ---------------------------------------------------------
# Dependency: Get Async DB Session
# ---------------------------------------------------------
async def get_session() -> AsyncSession:
    """
    Provides an async database session for API endpoints.
    Ensures proper session lifecycle management.
    """
    async with SessionLocal() as session:
        yield session


# ---------------------------------------------------------
# INTERNAL QUERY HELPER: lookup people with joins + filters
# ---------------------------------------------------------
async def lookUp(id: str, queryParameters = PeopelQueryParameters, db: AsyncSession = Depends(get_session)):
    """
    Generic people lookup query used by multiple endpoints.
    """
    sql = """
        SELECT
            p.id,
            p.firstname,
            p.middlename,
            p.lastname,
            p.address,
            p.birthdate,
            p.recruitment_date,
            p.birthplace,
            p.residence,
            p.dependents,
            p.recruitment_doc_ref,
            p.email,
            p.created_by,
            p.i2ce_hidden,
            p.last_modified,
            p.created,
            gender.id as gender_id,
            gender.name as gender,
            hc.id as nationality_id,
            hc.name as nationality,
            mst.id as marital_status_id,
            mst.name as marital_status,
            dgr.name as degree,
            dgr.id as degree_id
        FROM (
            SELECT  id,
                firstname,
                middlename,
                lastname,
                address,
                birthdate,
                recruitment_date,
                birthplace,
                residence,
                dependents,
                nationality,
                gender,
                marital_status,
                recruitment_doc_ref,
                email,
                created_by,
                i2ce_hidden,
                last_modified,
                created,
                degree
            FROM hippo_person
            ORDER BY created ASC
        ) as p
        LEFT JOIN hippo_country hc ON hc.id = p.nationality
        LEFT JOIN hippo_gender gender ON gender.id = p.gender
        LEFT JOIN hippo_marital_status mst ON mst.id = p.marital_status
        LEFT JOIN hippo_degree dgr ON dgr.id = p.degree
    """

    params = {}
    where_clauses = []

    if id is not None:
        where_clauses.append("p.id = :person_id")
        params["person_id"] = id

    if queryParameters is not None:
        if queryParameters.name is not None:
            where_clauses.append("p.firstname ILIKE :name OR p.lastname ILIKE :name")
            params["name"] = f"%{queryParameters.name}%"

        if queryParameters.firstname is not None:
            where_clauses.append("p.firstname ILIKE :firstname")
            params["firstname"] = queryParameters.firstname

        if queryParameters.middlename is not None:
            where_clauses.append("p.middlename ILIKE :middlename")
            params["middlename"] = queryParameters.middlename

        if queryParameters.lastname is not None:
            where_clauses.append("p.lastname ILIKE :lastname")
            params["lastname"] = queryParameters.lastname

        if queryParameters.matricule is not None:
            where_clauses.append(
                "p.id IN (SELECT person_id FROM hippo_person_identification WHERE number ILIKE :matricule)"
            )
            params["matricule"] = f"%{queryParameters.matricule}%"

        if queryParameters.birthdate is not None:
            where_clauses.append("p.birthdate = :birthdate")
            params["birthdate"] = queryParameters.birthdate

    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)

    sql += " LIMIT 25 "

    result = await db.execute(text(sql), params)
    return result.mappings().all()


# ---------------------------------------------------------
# GET PEOPLE LIST
# ---------------------------------------------------------
@apiRouter.get(
    "/people/",
    response_model=list,
    dependencies=[Depends(get_current_active_user)],
)
async def get_peoples(
    name: str = None,
    matricule: str = None,
    lastname: str = None,
    firstname: str = None,
    middlename: str = None,
    birthdate: str = None,
    db: AsyncSession = Depends(get_session)
):
    """
    Search and return people list (limited to 25).
    """
    result = await lookUp(None, PeopelQueryParameters(name=name, firstname=firstname, middlename=middlename, lastname=lastname, birthdate=birthdate, matricule=matricule), db)
    return [dict(row) for row in result]


# ---------------------------------------------------------
# GET PERSON DETAILS BY ID
# ---------------------------------------------------------
@apiRouter.get(
    "/people/{id}",
    response_model=HippoPersonRead,
    dependencies=[Depends(get_current_active_user)],
)
async def get_person(id: str, session: AsyncSession = Depends(get_session)):
    """
    Retrieve a single person by ID with their specialities.
    """
    # Get person details
    result = await lookUp(id, None, session)
    if len(result) == 0:
        raise HTTPException(status_code=404, detail="Person not found")
    
    person_data = dict(result[0])
    
    # Load specialities for this person
    specialities_result = await session.execute(
        select(HippoSpeciality)
        .join(HippoSpecialityPerson, HippoSpeciality.id == HippoSpecialityPerson.speciality_id)
        .where(HippoSpecialityPerson.person_id == id)
        .order_by(HippoSpeciality.name)
    )
    specialities = specialities_result.scalars().all()
    
    # Add specialities to person data
    person_data['specialities'] = specialities
    
    return person_data



# ---------------------------------------------------------
# GET PERSON'S SPECIALITIES
# ---------------------------------------------------------
@apiRouter.get(
    "/people/{person_id}/specialities",
    response_model=list[HippoSpecialityRead],
    dependencies=[Depends(get_current_active_user)],
)
async def get_person_specialities(
    person_id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Retrieve all specialities for a specific person.
    
    Returns:
    - 404 if person not found
    - List of specialities associated with the person
    """
    # Check if person exists
    result = await session.execute(
        select(HippoPerson).where(HippoPerson.id == person_id)
    )
    person = result.scalar_one_or_none()
    
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    # Get specialities for this person
    specialities_result = await session.execute(
        select(HippoSpeciality)
        .join(HippoSpecialityPerson, HippoSpeciality.id == HippoSpecialityPerson.speciality_id)
        .where(HippoSpecialityPerson.person_id == person_id)
        .order_by(HippoSpeciality.name)
    )
    specialities = specialities_result.scalars().all()
    
    return specialities

# ---------------------------------------------------------
# CREATE PERSON
# ---------------------------------------------------------
@apiRouter.post(
    "/people/",
    response_model=HippoPersonRead,
    dependencies=[Depends(get_current_active_user)]
)
async def create_person(
    person: HippoPersonCreate,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_active_user),
):
    """
    Create a new person record with specialities.
    """
    # Get next sequential number for person IDs
    maxNumber = await entity_map.getMaxNumber("person", session)
    maxNumber = maxNumber + 1

    # Convert request payload to dict
    person_data = person.model_dump(exclude={'specialities'})  # Exclude specialities from person data

    # Generate ID
    person_id = generate_unit_id(f"person|{maxNumber}", length=10)

    # Fill required audit fields
    person_data['id'] = person_id
    person_data['created_by'] = current_user_id

    # Create ORM instance
    new_person = HippoPerson(**person_data)
    session.add(new_person)

    # ---------------------------------------------------------
    # ADD SPECIALITIES TO PERSON
    # ---------------------------------------------------------
    if person.specialities is not None and len(person.specialities) > 0:
        speciality_ids = person.specialities
        
        # Validate that all specialities exist
        if speciality_ids:
            speciality_result = await session.execute(
                select(HippoSpeciality).where(
                    HippoSpeciality.id.in_(speciality_ids)
                )
            )
            existing_specialities = speciality_result.scalars().all()
            existing_speciality_ids = {s.id for s in existing_specialities}
            
            # Check if any speciality doesn't exist
            invalid_ids = set(speciality_ids) - existing_speciality_ids
            if invalid_ids:
                await session.rollback()
                raise HTTPException(
                    status_code=400,
                    detail=f"Specialities not found: {', '.join(invalid_ids)}"
                )
        
        # Add specialities to person
        for speciality_id in speciality_ids:
            speciality_person = HippoSpecialityPerson(
                id=f"speciality_person|{person_id}|{speciality_id}",
                person_id=person_id,
                speciality_id=speciality_id,
                parent='|',
                created=datetime.now(),
                last_modified=datetime.now()
            )
            session.add(speciality_person)

    # Update entity map
    new_entity_map = HippoEntityMap(
        id=person_id,
        entity_type="person",
        max_number=maxNumber
    )
    session.add(new_entity_map)

    # Audit trail
    auditLog = HippoAuditLog(
        id=str(uuid.uuid4()),
        user_id=current_user_id,
        operation=f'add new person {person_id}'
    )
    session.add(auditLog)

    # Commit
    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating person: {str(e)}")

    # Refresh to get DB-generated fields
    await session.refresh(new_person)
    
    # Load person with specialities for response
    person_with_specialities = await get_person_with_specialities(session, person_id)
    
    return person_with_specialities


# ---------------------------------------------------------
# UPDATE PERSON
# ---------------------------------------------------------
@apiRouter.put("/people/{person_id}", response_model=HippoPersonRead)
async def update_person(
    person_id: str,
    person: HippoPersonUpdate,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_active_user),
):
    """
    Update an existing person with specialities.
    """
    # Fetch existing person record
    result = await session.execute(
        select(HippoPerson).where(HippoPerson.id == person_id)
    )
    existing_person = result.scalar_one_or_none()

    if not existing_person:
        raise HTTPException(status_code=404, detail="Person not found")

    # Apply incoming updates (exclude specialities)
    update_data = person.model_dump(exclude_unset=True, exclude={'specialities'})
    
    # S'assurer que last_modified est toujours mis à jour
    update_data['last_modified'] = datetime.now()
    
    for key, value in update_data.items():
        if key != 'created' and key != 'id':
            setattr(existing_person, key, value)

    # Track who performed the modification
    setattr(existing_person, "last_modified_by", current_user_id)

    # ---------------------------------------------------------
    # UPDATE SPECIALITIES (Many-to-Many Relationship)
    # ---------------------------------------------------------
    if person.specialities is not None:
        speciality_ids = person.specialities
        
        # Validate that all specialities exist
        if speciality_ids and len(speciality_ids) > 0:
            speciality_result = await session.execute(
                select(HippoSpeciality).where(
                    HippoSpeciality.id.in_(speciality_ids)
                )
            )
            existing_specialities = speciality_result.scalars().all()
            existing_speciality_ids = {s.id for s in existing_specialities}
            
            # Check if any speciality doesn't exist
            invalid_ids = set(speciality_ids) - existing_speciality_ids
            if invalid_ids:
                raise HTTPException(
                    status_code=400,
                    detail=f"Specialities not found: {', '.join(invalid_ids)}"
                )
        
        # Delete all existing specialities for this person
        await session.execute(
            delete(HippoSpecialityPerson).where(
                HippoSpecialityPerson.person_id == person_id
            )
        )

        # Add new specialities
        for speciality_id in speciality_ids:
            speciality_person = HippoSpecialityPerson(
                id=f"speciality_person|{person_id}|{speciality_id}",
                person_id=person_id,
                speciality_id=speciality_id,
                parent='|',
                created=datetime.now(),
                last_modified=datetime.now()
            )
            session.add(speciality_person)

    # Audit trail
    auditLog = HippoAuditLog(
        id=str(uuid.uuid4()),
        user_id=current_user_id,
        operation=f'update person {person_id}'
    )
    session.add(auditLog)

    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating person: {str(e)}")

    await session.refresh(existing_person)
    
    # Load person with specialities for response
    person_with_specialities = await get_person_with_specialities(session, person_id)
    
    return person_with_specialities

# ---------------------------------------------------------
# HELPER: Get person with specialities
# ---------------------------------------------------------
async def get_person_with_specialities(
    session: AsyncSession,
    person_id: str
) -> dict:
    """
    Get a person with their specialities loaded.
    """
    # Get person details
    result = await lookUp(person_id, None, session)
    if len(result) == 0:
        return None
    
    person_data = dict(result[0])
    
    # Load specialities for this person
    specialities_result = await session.execute(
        select(HippoSpeciality)
        .join(HippoSpecialityPerson, HippoSpeciality.id == HippoSpecialityPerson.speciality_id)
        .where(HippoSpecialityPerson.person_id == person_id)
        .order_by(HippoSpeciality.name)
    )
    specialities = specialities_result.scalars().all()
    
    person_data['specialities'] = specialities
    
    return person_data