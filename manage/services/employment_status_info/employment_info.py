

from manage.models import HippoEmploymentStatusInfo, HippoPerson, HippoEntityMap
from manage.services.employment_status_info.schemas import HippoEmploymentStatusInfoCreate, HippoEmploymentStatusInfoUpdate, HippoEmploymentStatusInfoRead
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user
from manage.services.entity_map import entity_map
from sqlalchemy import text
from manage.utils import generate_unit_id

apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session



@apiRouter.post("/employment_status_infos/", response_model=HippoEmploymentStatusInfoRead, dependencies=[Depends(get_current_active_user)])
async def create_employement_infos(
    employment_infos:HippoEmploymentStatusInfoCreate,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_active_user),
):
    ## getting current user
    entityType='employment_infos'
    maxNumber = await entity_map.getMaxNumber(entityType, session)
    maxNumber = maxNumber + 1
    employment_data = employment_infos.dict()  # get dict from pydantic model
    employment_data['id'] = generate_unit_id(f"{entityType}|{maxNumber}", length=10)
    employment_data['created_by'] = current_user_id
    new_employment_info = HippoEmploymentStatusInfo(**employment_data)
    session.add(new_employment_info)

    new_entity_map = HippoEntityMap(id=  employment_data['id'], entity_type=entityType, max_number=maxNumber)
    session.add(new_entity_map)

    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise

    await session.refresh(new_employment_info)
    return new_employment_info


@apiRouter.put("/employment_status_infos/{id}", response_model=HippoEmploymentStatusInfoRead)
async def update_person(id: str,
    statusInfo:HippoEmploymentStatusInfoUpdate, 
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_active_user),
):
   
    result = await session.execute(select(HippoEmploymentStatusInfo).where(HippoEmploymentStatusInfo.id == id))
    existing_employmentInfo = result.scalar_one_or_none()
    if not existing_employmentInfo:
        raise HTTPException(status_code=404, detail="employment status infos not found")
    
    for key, value in statusInfo.dict().items():
        if value is not None and key != 'created':
            setattr(existing_employmentInfo, key, value)

    setattr(existing_employmentInfo, 'last_modified_by', current_user_id)

    await session.commit()
    await session.refresh(existing_employmentInfo)
    return existing_employmentInfo  



# find a maritalStatus by id
@apiRouter.get("/employment_status_infos/{id}", response_model=HippoEmploymentStatusInfoRead, dependencies=[Depends(get_current_active_user)],)
async def get_maritalStatus(id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoEmploymentStatusInfo).where(HippoEmploymentStatusInfo.id == id))
    maritalStatus = result.scalar_one_or_none()
    if not maritalStatus:
        raise HTTPException(status_code=404, detail="Employment_status_infos status not found")
    return maritalStatus


@apiRouter.get("/employment_status_infos/person/{person_id}", response_model=list[HippoEmploymentStatusInfoRead], dependencies=[Depends(get_current_active_user)])
async def get_employement_infos(
    person_id:str,
    db: AsyncSession = Depends(get_session),
    username: str = Depends(get_current_active_user),
):
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
            select *
            from hippo_employment_status_info
            WHERE person_id='{person_id}'
            ORDER BY created ASC
        ) as   empSt
        LEFT JOIN public.hippo_cadre cadre on cadre.id = empSt.cadre
        LEFT JOIN public.hippo_salary_grade grade on grade.id = empSt.grade
        LEFT JOIN public.hippo_classification clasf on clasf.id = empSt.classification
        LEFT JOIN public.hippo_employee_status estatus on estatus.id = empSt.employee_status
        LEFT JOIN public.hippo_salary_source ss ON ss.id = empSt.salary_source
        LEFT JOIN public.hippo_job_type jt ON jt.id = empSt.job_type

    """

    result = await db.execute(text(sql))
    rows = result.mappings().all()   # returns list of dict-like rows
    return rows