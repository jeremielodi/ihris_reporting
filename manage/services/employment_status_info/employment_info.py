"""
Employment Status Info API
---------------------------

This module manages employment status history records
for employees (HippoEmploymentStatusInfo).

It supports:
- Creating employment status records
- Updating records
- Fetching single record by ID
- Fetching all employment records for a given person

Includes:
- EntityMap-based incremental ID generation
- Audit fields (created_by, last_modified_by)
- Joined reporting query for enriched employment history

All endpoints require authenticated active users.
"""

from manage.models import HippoEmploymentStatusInfo, HippoPerson, HippoEntityMap
from manage.services.employment_status_info.schemas import (
    HippoEmploymentStatusInfoCreate,
    HippoEmploymentStatusInfoUpdate,
    HippoEmploymentStatusInfoRead
)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user
from manage.services.entity_map import entity_map
from sqlalchemy import text
from manage.utils import generate_unit_id


# Initialize router
apiRouter = APIRouter()


async def get_session() -> AsyncSession:
    """
    Provides an asynchronous database session.

    - Opens AsyncSession
    - Yields it during request lifecycle
    - Automatically closes it afterward
    """
    async with SessionLocal() as session:
        yield session


# -------------------------------------------------------------------
# CREATE EMPLOYMENT STATUS INFO
# -------------------------------------------------------------------
@apiRouter.post(
    "/employment_status_infos/",
    response_model=HippoEmploymentStatusInfoRead,
    dependencies=[Depends(get_current_active_user)]
)
async def create_employement_infos(
    employment_infos: HippoEmploymentStatusInfoCreate,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_active_user),
):
    """
    Create a new employment status record for a person.

    Process:
        1. Retrieve max_number from entity_map.
        2. Increment to generate new sequential number.
        3. Generate unique ID using generate_unit_id().
        4. Set created_by audit field.
        5. Insert employment record.
        6. Insert corresponding entity_map record.
        7. Commit transaction.

    Returns:
        HippoEmploymentStatusInfoRead
    """

    entityType = 'employment_infos'

    # Retrieve current max_number for this entity type
    maxNumber = await entity_map.getMaxNumber(entityType, session)
    maxNumber = maxNumber + 1

    # Convert Pydantic model to dict
    employment_data = employment_infos.dict()

    # Generate secure, formatted unique ID
    employment_data['id'] = generate_unit_id(
        f"{entityType}|{maxNumber}",
        length=10
    )

    # Set audit field
    employment_data['created_by'] = current_user_id

    new_employment_info = HippoEmploymentStatusInfo(**employment_data)
    session.add(new_employment_info)

    # Update entity_map for incremental tracking
    new_entity_map = HippoEntityMap(
        id=employment_data['id'],
        entity_type=entityType,
        max_number=maxNumber
    )
    session.add(new_entity_map)

    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise

    await session.refresh(new_employment_info)
    return new_employment_info


# -------------------------------------------------------------------
# UPDATE EMPLOYMENT STATUS INFO
# -------------------------------------------------------------------
@apiRouter.put(
    "/employment_status_infos/{id}",
    response_model=HippoEmploymentStatusInfoRead
)
async def update_person(
    id: str,
    statusInfo: HippoEmploymentStatusInfoUpdate,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_active_user),
):
    """
    Update an existing employment status record.

    - Updates only provided (non-null) fields.
    - Prevents modification of 'created' field.
    - Updates last_modified_by audit field.

    Raises:
        HTTPException(404) if record not found.
    """

    result = await session.execute(
        select(HippoEmploymentStatusInfo)
        .where(HippoEmploymentStatusInfo.id == id)
    )
    existing_employmentInfo = result.scalar_one_or_none()

    if not existing_employmentInfo:
        raise HTTPException(
            status_code=404,
            detail="employment status infos not found"
        )

    # Apply partial update (exclude 'created' field)
    for key, value in statusInfo.dict().items():
        if value is not None and key != 'created':
            setattr(existing_employmentInfo, key, value)

    # Update audit field
    setattr(existing_employmentInfo, 'last_modified_by', current_user_id)

    await session.commit()
    await session.refresh(existing_employmentInfo)

    return existing_employmentInfo


# -------------------------------------------------------------------
# GET EMPLOYMENT STATUS INFO BY ID
# -------------------------------------------------------------------
@apiRouter.get(
    "/employment_status_infos/{id}",
    response_model=HippoEmploymentStatusInfoRead,
    dependencies=[Depends(get_current_active_user)],
)
async def get_maritalStatus(
    id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieve a single employment status record by ID.

    Raises:
        HTTPException(404) if not found.
    """

    result = await session.execute(
        select(HippoEmploymentStatusInfo)
        .where(HippoEmploymentStatusInfo.id == id)
    )
    maritalStatus = result.scalar_one_or_none()

    if not maritalStatus:
        raise HTTPException(
            status_code=404,
            detail="Employment_status_infos status not found"
        )

    return maritalStatus


# -------------------------------------------------------------------
# GET EMPLOYMENT HISTORY BY PERSON
# -------------------------------------------------------------------
@apiRouter.get(
    "/employment_status_infos/person/{person_id}",
    response_model=list[HippoEmploymentStatusInfoRead],
    dependencies=[Depends(get_current_active_user)]
)
async def get_employement_infos(
    person_id: str,
    db: AsyncSession = Depends(get_session),
    username: str = Depends(get_current_active_user),
):
    
    """
    Retrieve full employment history for a given person.

    This query:
        - Fetches employment status records.
        - Enriches results with related lookup tables:
            - Cadre
            - Classification
            - Salary Grade
            - Employee Status
            - Salary Source
            - Job Type
        - Orders results chronologically (created ASC).

    Returns:
        List[dict] with enriched employment data.
    """

    sql = f"""
        SELECT 
            empSt.*,
            cadre.name as cadre_name, 
            clasf.name as classification_name,
            grade.name as grade_name,
            estatus.name as employee_status_name,
            ss.name as salary_source_name,
            jt.name as job_type_name
        FROM (
            SELECT *
            FROM hippo_employment_status_info
            WHERE person_id=:person_id
            ORDER BY created ASC
        ) AS empSt
        LEFT JOIN public.hippo_cadre cadre 
            ON cadre.id = empSt.cadre
        LEFT JOIN public.hippo_salary_grade grade 
            ON grade.id = empSt.grade
        LEFT JOIN public.hippo_classification clasf 
            ON clasf.id = empSt.classification
        LEFT JOIN public.hippo_employee_status estatus 
            ON estatus.id = empSt.employee_status
        LEFT JOIN public.hippo_salary_source ss 
            ON ss.id = empSt.salary_source
        LEFT JOIN public.hippo_job_type jt 
            ON jt.id = empSt.job_type
    """

    result = await db.execute(text(sql), {"person_id": person_id})
    rows = result.mappings().all()

    return rows