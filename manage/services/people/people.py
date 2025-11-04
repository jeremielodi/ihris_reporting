

from manage.models import HippoUser, HippoPerson, HippoEntityMap, HippoAuditLog
from manage.services.people.schemas import HippoPersonCreate, HippoPersonUpdate, HippoPersonRead, PeopelQueryParameters
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user
from manage.services.entity_map import entity_map
from sqlalchemy import text
from manage.utils import generate_unit_id
import uuid
apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


async def lookUp(id:str, queryParameters: PeopelQueryParameters | None, db: AsyncSession):
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

    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)

    sql += " LIMIT 25"

    result = await db.execute(text(sql), params)
    return result.mappings().all()   # returns list of dict-like rows
    
# Get all people
@apiRouter.get("/people/",  response_model=list, dependencies=[Depends(get_current_active_user)],)
async def get_peoples( name: str = None, db: AsyncSession = Depends(get_session)):
    result = await lookUp(None, PeopelQueryParameters(name=name), db)
    return result


# find a person by id
@apiRouter.get("/people/{id}", response_model=HippoPersonRead, dependencies=[Depends(get_current_active_user)],)
async def get_person(id: str, session: AsyncSession = Depends(get_session)):
    result = await lookUp(id, None,session)
    if len(result) == 0:
        raise HTTPException(status_code=404, detail="person not found")
    return result[0]

@apiRouter.post("/people/", response_model=HippoPersonRead, dependencies=[Depends(get_current_active_user)])
async def create_person(
    person:HippoPersonCreate,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_active_user),
):
    ## getting current user
   
    maxNumber = await entity_map.getMaxNumber("person", session)
    maxNumber = maxNumber + 1
    person_data = person.dict()  # get dict from pydantic model
    persion_id = generate_unit_id(f"person|{maxNumber}", length=10)
    person_data['id'] = persion_id
    person_data['created_by'] = current_user_id
    new_person = HippoPerson(**person_data)
    session.add(new_person)

    new_entity_map = HippoEntityMap(id= person_data['id'], entity_type="person", max_number=maxNumber)
    session.add(new_entity_map)

    auditLog = HippoAuditLog(id= uuid.uuid4(), user_id=current_user_id, operation=f'add new agent {persion_id}')
    session.add(auditLog)
    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise

    await session.refresh(new_person)
    return new_person

@apiRouter.put("/people/{person_id}", response_model=HippoPersonRead)
async def update_person(person_id: str,
    person:HippoPersonUpdate, 
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_active_user),
):
  
    result = await session.execute(select(HippoPerson).where(HippoPerson.id == person_id))
    existing_person = result.scalar_one_or_none()
    if not existing_person:
        raise HTTPException(status_code=404, detail="person not found")
    
    for key, value in person.dict().items():
        if value is not None and key != 'created':
            setattr(existing_person, key, value)

    setattr(existing_person, "last_modified_by", current_user_id)

    auditLog = HippoAuditLog(id= uuid.uuid4(), user_id=current_user_id, operation=f'update new agent {person_id}')
    session.add(auditLog)

    await session.commit()
    await session.refresh(existing_person)
    return existing_person  
