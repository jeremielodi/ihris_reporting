# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

# ORM models
from datetime import date, datetime
import json
import os
from pathlib import Path

# Importer delete de SQLAlchemy (pas de requests)
from sqlalchemy import delete

from manage.models import (
    HippoSpecialityPerson,
    HippoSpeciality,
    HippoPerson,
    HippoEntityMap,
    HippoAuditLog,
    HippoContact,
    HippoEmploymentStatusInfo,
    HippoPersonIdentification,
    HippoPersonTimesheet,
    HippoPersonDocument,
    HippoPersonPassport,
)

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
from manage.services.role.role import require_action

# hippo_actions.id for "CAN_DELETE_DUPLICATE_PERSON" (see db/config.sql /
# client/src/service/constants.ts) - gates viewing and deleting duplicates.
CAN_DELETE_DUPLICATE_PERSON = 7

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

# Where uploaded documents/photos live on disk (same resolution as
# document.py/passport.py) so deleting a person can also clean up their files.
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR") or "./uploads")


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
# FIND DUPLICATE PEOPLE
# ---------------------------------------------------------
# NOTE: must stay registered before GET /people/{id} below, otherwise
# "duplicates" would be swallowed as that route's {id} path param.
@apiRouter.get(
    "/people/duplicates",
    dependencies=[Depends(get_current_active_user), Depends(require_action(CAN_DELETE_DUPLICATE_PERSON))],
)
async def get_duplicate_people(db: AsyncSession = Depends(get_session)):
    """
    Group people who share the same lastname, firstname, middlename and
    birthdate - the same match used to warn about a possible duplicate at
    creation time (see create.vue's searchExisting()). Only groups with
    more than one member are returned.

    Counts of related records are included so a reviewer can tell at a
    glance which record in a group has the most data tied to it before
    deciding which one to keep.
    """
    result = await db.execute(text("""
        SELECT
            p.id, p.lastname, p.firstname, p.middlename, p.birthdate, p.created,
            (SELECT COUNT(*) FROM hippo_person_identification i WHERE i.person_id = p.id) AS identification_count,
            (SELECT COUNT(*) FROM hippo_employment_status_info e WHERE e.person_id = p.id) AS employment_count,
            (SELECT COUNT(*) FROM hippo_person_document d WHERE d.person_id = p.id) AS document_count
        FROM hippo_person p
        WHERE p.lastname IS NOT NULL AND p.birthdate IS NOT NULL
        ORDER BY p.lastname, p.firstname, p.created
    """))
    rows = [dict(row) for row in result.mappings().all()]

    # Grouped in Python (not SQL) because comparing NULL middlenames with a
    # row-value IN-subquery never matches (NULL = NULL is NULL, not true in
    # SQL), which would silently hide the very common case of two duplicate
    # records that both have no middlename.
    groups = {}
    for row in rows:
        key = (
            (row['lastname'] or '').strip().lower(),
            (row['firstname'] or '').strip().lower(),
            (row['middlename'] or '').strip().lower(),
            str(row['birthdate']),
        )
        groups.setdefault(key, []).append(row)

    return [members for members in groups.values() if len(members) > 1]


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
# DELETE PERSON (used from the duplicate-cleanup screen)
# ---------------------------------------------------------
def _row_to_jsonable_dict(obj) -> dict:
    """ORM instance -> plain dict, with dates/datetimes as ISO strings."""
    result = {}
    for column in obj.__table__.columns:
        value = getattr(obj, column.name)
        if isinstance(value, (datetime, date)):
            value = value.isoformat()
        result[column.name] = value
    return result


@apiRouter.delete(
    "/people/{person_id}",
    dependencies=[Depends(get_current_active_user), Depends(require_action(CAN_DELETE_DUPLICATE_PERSON))],
)
async def delete_person(
    person_id: str,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_active_user),
):
    """
    Permanently delete a person and every record tied to them
    (identifications, contacts, specialities, employment history,
    timesheets, documents, passport photo), after writing a full
    snapshot of all of it to the audit log.

    This is irreversible beyond what's captured in that audit entry -
    there is no soft-delete/undo. Intended to be triggered only from the
    duplicate-cleanup review screen, not exposed as a general-purpose
    "delete a person" action.
    """
    result = await session.execute(select(HippoPerson).where(HippoPerson.id == person_id))
    person = result.scalar_one_or_none()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    identifications = (await session.execute(
        select(HippoPersonIdentification).where(HippoPersonIdentification.person_id == person_id)
    )).scalars().all()
    contacts = (await session.execute(
        select(HippoContact).where(HippoContact.person_id == person_id)
    )).scalars().all()
    speciality_links = (await session.execute(
        select(HippoSpecialityPerson).where(HippoSpecialityPerson.person_id == person_id)
    )).scalars().all()
    employment_infos = (await session.execute(
        select(HippoEmploymentStatusInfo).where(HippoEmploymentStatusInfo.person_id == person_id)
    )).scalars().all()
    timesheets = (await session.execute(
        select(HippoPersonTimesheet).where(HippoPersonTimesheet.person_id == person_id)
    )).scalars().all()
    documents = (await session.execute(
        select(HippoPersonDocument).where(HippoPersonDocument.person_id == person_id)
    )).scalars().all()
    photos = (await session.execute(
        select(HippoPersonPassport).where(HippoPersonPassport.person_id == person_id)
    )).scalars().all()

    snapshot = {
        "person": _row_to_jsonable_dict(person),
        "identifications": [_row_to_jsonable_dict(x) for x in identifications],
        "contacts": [_row_to_jsonable_dict(x) for x in contacts],
        "specialities": [_row_to_jsonable_dict(x) for x in speciality_links],
        "employment_status_info": [_row_to_jsonable_dict(x) for x in employment_infos],
        "timesheets": [_row_to_jsonable_dict(x) for x in timesheets],
        "documents": [_row_to_jsonable_dict(x) for x in documents],
        "photos": [_row_to_jsonable_dict(x) for x in photos],
    }

    audit_log = HippoAuditLog(
        id=uuid.uuid4(),
        user_id=current_user_id,
        operation=json.dumps({"action": "delete_person", "person_id": person_id, "snapshot": snapshot}, default=str),
    )
    session.add(audit_log)

    # Best-effort cleanup of uploaded files - the audit snapshot above is
    # the record of truth, so a failure here shouldn't block the deletion.
    for row in (*documents, *photos):
        try:
            (UPLOAD_DIR / row.path).unlink(missing_ok=True)
        except Exception:
            pass

    await session.execute(delete(HippoPersonIdentification).where(HippoPersonIdentification.person_id == person_id))
    await session.execute(delete(HippoContact).where(HippoContact.person_id == person_id))
    await session.execute(delete(HippoSpecialityPerson).where(HippoSpecialityPerson.person_id == person_id))
    await session.execute(delete(HippoEmploymentStatusInfo).where(HippoEmploymentStatusInfo.person_id == person_id))
    await session.execute(delete(HippoPersonTimesheet).where(HippoPersonTimesheet.person_id == person_id))
    await session.execute(delete(HippoPersonDocument).where(HippoPersonDocument.person_id == person_id))
    await session.execute(delete(HippoPersonPassport).where(HippoPersonPassport.person_id == person_id))
    await session.execute(delete(HippoPerson).where(HippoPerson.id == person_id))

    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting person: {str(e)}")

    return {"detail": "Person and related records deleted", "person_id": person_id}


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