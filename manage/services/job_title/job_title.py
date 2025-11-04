

from manage.models import HippoJobTitle
from manage.services.job_title.schemas import HippoJobTitleRead, HippoJobTitleCreate, HippoJobTitleUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user


apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

# Get all job_titles
@apiRouter.get("/job_titles/", response_model=list[HippoJobTitleRead], dependencies=[Depends(get_current_active_user)],)
async def get_job_titles(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoJobTitle).order_by(HippoJobTitle.name))
    job_titles = result.scalars().all()
    return job_titles


# find a Job_title by id
@apiRouter.get("/job_titles/{job_title_id}", response_model=HippoJobTitleRead, dependencies=[Depends(get_current_active_user)],)
async def get_Job_title(job_title_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoJobTitle).where(HippoJobTitle.id == job_title_id))
    Job_title = result.scalar_one_or_none()
    if not Job_title:
        raise HTTPException(status_code=404, detail="Job_title not found")
    return Job_title

@apiRouter.post("/job_titles/", response_model=HippoJobTitleRead, dependencies=[Depends(get_current_active_user)])
async def create_Job_title(
    Job_title:HippoJobTitleCreate,
    session: AsyncSession = Depends(get_session),
):
    Job_title_data = Job_title.dict()  # get dict from pydantic model
    Job_title_data['id'] = f"job_title|{Job_title.name}"
    
    new_Job_title = HippoJobTitle(**Job_title_data)
    session.add(new_Job_title)
    await session.commit()
    await session.refresh(new_Job_title)
    return new_Job_title

# update an existing Job_title
@apiRouter.put("/job_titles/{job_title_id}", response_model=HippoJobTitleRead)
async def update_Job_title(job_title_id: str, Job_title:HippoJobTitleUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoJobTitle).where(HippoJobTitle.id == job_title_id))
    existing_Job_title = result.scalar_one_or_none()
    if not existing_Job_title:
        raise HTTPException(status_code=404, detail="Job_title not found")
    
    for key, value in Job_title.dict().items():
        if value is not None:
            setattr(existing_Job_title, key, value)
    
    await session.commit()
    await session.refresh(existing_Job_title)
    return existing_Job_title  

# delete a Job_title
@apiRouter.delete("/job_titles/{job_title_id}")
async def delete_Job_title(job_title_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoJobTitle).where(HippoJobTitle.id == job_title_id))
    existing_Job_title = result.scalar_one_or_none()
    if not existing_Job_title:
        raise HTTPException(status_code=404, detail="Job_title not found")
    
    await session.delete(existing_Job_title)
    await session.commit()
    return {"detail": "Job_title deleted successfully"}


