# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

# ORM models (User, Person, EntityMap for incremental numbering, and AuditLog)
from datetime import date

from manage.models import HippoUser, HippoPerson, HippoEntityMap, HippoAuditLog

# Pydantic schemas for People (create/update/read + query params)
from manage.services.people.schemas import (
    HippoPersonCreate,
    HippoPersonUpdate,
    HippoPersonRead,
    PeopelQueryParameters
)

# Async database session support
from sqlalchemy.ext.asyncio import AsyncSession

# FastAPI utilities
from fastapi import APIRouter, Depends, HTTPException

# SQLAlchemy ORM query builder (used for update)
from sqlalchemy.future import select
from fastapi import Depends
# Database session factory
from manage.database import SessionLocal, engine

# Authentication dependency (protect endpoints)
from endpoints.user_api import get_current_active_user

# Service used to generate incremental numbers for entities (person, cadre, etc.)
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

    What it does:
    - Selects base person fields from hippo_person
    - Joins reference tables for display labels:
      nationality (hippo_country), gender, marital status, degree
    - Supports filters:
      - by person id
      - by name (firstname or lastname)
      - by birthdate (exact match)
      - by matricule (via hippo_person_identification)
    - Limits results to 25 to avoid heavy responses.
    """

    # Base SQL query: select person fields + joined labels/ids
    sql = """
        SELECT 
            p.id,
            p.firstname, 
            p.middlename, 
            p.lastname,
            p.birthdate,
            p.recruitment_date,
            p.birthplace,
            p.residence,
            p.dependents,
            gender.id as gender_id,
            gender.name as gender,
            hc.id as nationality_id,
            hc.name as nationality,
            mst.id as marital_status_id,
            mst.name as marital_status,
            dgr.name as degree,
            dgr.id as degree_id
        FROM (
            -- Subquery to define ordering before joins (stable pagination-ish behavior)
            SELECT  id, 
                firstname, 
                middlename, 
                lastname,
                birthdate,
                recruitment_date,
                birthplace,
                residence,
                dependents,
                nationality,
                gender,
                marital_status,
                degree
            FROM hippo_person 
            ORDER BY created ASC
        ) as p
        -- LEFT JOINs allow nullable references (person can exist without these attributes)
        LEFT JOIN hippo_country hc ON hc.id = p.nationality
        LEFT JOIN hippo_gender gender ON gender.id = p.gender
        LEFT JOIN hippo_marital_status mst ON mst.id = p.marital_status
        LEFT JOIN hippo_degree dgr ON dgr.id = p.degree
    """

    # Parameters dict for safe query binding
    params = {}

    # WHERE clause builder (appends conditions dynamically)
    where_clauses = []

    # Filter by ID if provided
    if id is not None:
        where_clauses.append("p.id = :person_id")
        params["person_id"] = id

   
    # Filter by name/matricule if queryParameters provided
    if queryParameters is not None:
        if queryParameters.name is not None:
            # NOTE: This condition should ideally be grouped with parentheses.
            # Current version: "A OR B" can interact badly with other AND clauses.
            where_clauses.append("p.firstname ILIKE :name OR p.lastname ILIKE :name")
            params["name"] = f"%{queryParameters.name}%"

        if queryParameters.firstname is not None:
                    # NOTE: This condition should ideally be grouped with parentheses.
                    # Current version: "A OR B" can interact badly with other AND clauses.
            where_clauses.append("p.firstname ILIKE :firstname")
            params["firstname"] = queryParameters.firstname

        if queryParameters.middlename is not None:
                    # NOTE: This condition should ideally be grouped with parentheses.
                    # Current version: "A OR B" can interact badly with other AND clauses.
            where_clauses.append("p.middlename ILIKE :middlename")
            params["middlename"] = queryParameters.middlename

        if queryParameters.lastname is not None:
                    # NOTE: This condition should ideally be grouped with parentheses.
                    # Current version: "A OR B" can interact badly with other AND clauses.
            where_clauses.append("p.lastname ILIKE :lastname")
            params["lastname"] = queryParameters.lastname

        if queryParameters.lastname is not None:
                    # NOTE: This condition should ideally be grouped with parentheses.
                    # Current version: "A OR B" can interact badly with other AND clauses.
            where_clauses.append("p.lastname ILIKE :lastname")
            params["lastname"] = queryParameters.lastname

        if queryParameters.matricule is not None:
            # Filter by identification number (matricule) through identification table
            where_clauses.append(
                "p.id IN (SELECT person_id FROM hippo_person_identification WHERE number ILIKE :matricule)"
            )
            params["matricule"] = f"%{queryParameters.matricule}%"

        if queryParameters.birthdate is not None:
            where_clauses.append("p.birthdate = :birthdate")
            params["birthdate"] = queryParameters.birthdate  # Convert date to string for SQL

    print(params)
    # Append WHERE clause if any filters exist
    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)

    # Hard limit to prevent huge responses
    sql += " LIMIT 25 "

    # Execute query safely with bound parameters
    result = await db.execute(text(sql), params)

    # Return list of dict-like rows (good for JSON responses)
    return result.mappings().all()


# ---------------------------------------------------------
# GET PEOPLE LIST (search by name/matricule)
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

    Query params:
    - name: searches firstname or lastname using ILIKE
    - matricule: searches in hippo_person_identification.number using ILIKE
    """
    result = await lookUp(None, PeopelQueryParameters(name=name, firstname=firstname, middlename=middlename, lastname=lastname, birthdate=birthdate, matricule=matricule), db)
    return result


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
    Retrieve a single person by ID.
    Uses the lookup query to include joined labels.
    Returns 404 if not found.
    """
    result = await lookUp(id, None, session)
    if len(result) == 0:
        raise HTTPException(status_code=404, detail="person not found")
    return result[0]


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
    Create a new person record.

    Steps:
    - Get next incremental number from entity_map (for "person")
    - Generate a new person ID using generate_unit_id
    - Set created_by for auditing
    - Insert person in hippo_person
    - Insert/update entity_map (tracks max_number for this entity type)
    - Write audit log entry
    - Commit transaction (rollback on failure)
    """

    # Get next sequential number for person IDs
    maxNumber = await entity_map.getMaxNumber("person", session)
    maxNumber = maxNumber + 1

    # Convert request payload to dict
    person_data = person.dict()

    # Generate ID (example: person|<sequence>xxxxx) with fixed length
    # NOTE: variable name is "persion_id" (typo), but kept as-is
    persion_id = generate_unit_id(f"person|{maxNumber}", length=10)

    # Fill required audit fields
    person_data['id'] = persion_id
    person_data['created_by'] = current_user_id

    # Create ORM instance
    new_person = HippoPerson(**person_data)
    session.add(new_person)

    # Update entity map to store latest max number used
    new_entity_map = HippoEntityMap(
        id=person_data['id'],
        entity_type="person",
        max_number=maxNumber
    )
    session.add(new_entity_map)

    # Audit trail: record creation action
    auditLog = HippoAuditLog(
        id=uuid.uuid4(),
        user_id=current_user_id,
        operation=f'add new agent {persion_id}'
    )
    session.add(auditLog)

    # Commit with rollback protection
    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise

    # Refresh to get DB-generated fields (if any)
    await session.refresh(new_person)
    print(new_person)
    return new_person


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
    Update an existing person.

    - Loads person via ORM query.
    - Applies only non-null fields (excluding 'created').
    - Sets last_modified_by for auditing.
    - Writes an audit log entry.
    - Commits changes and returns updated record.
    """

    # Fetch existing person record
    result = await session.execute(
        select(HippoPerson).where(HippoPerson.id == person_id)
    )
    existing_person = result.scalar_one_or_none()

    if not existing_person:
        raise HTTPException(status_code=404, detail="person not found")

    # Apply incoming updates (partial update behavior)
    for key, value in person.dict().items():
        if value is not None and key != 'created':
            setattr(existing_person, key, value)

    # Track who performed the modification
    setattr(existing_person, "last_modified_by", current_user_id)

    # Audit trail: record update action
    auditLog = HippoAuditLog(
        id=uuid.uuid4(),
        user_id=current_user_id,
        operation=f'update agent {person_id}'
    )
    session.add(auditLog)

    await session.commit()
    await session.refresh(existing_person)
    return existing_person