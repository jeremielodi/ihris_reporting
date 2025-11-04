from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from manage.database import SessionLocal, engine
from models.models import Cadre, Classification, County, District, Facility, HealthArea, Job
from models.training import dashboard_data, scheduled_training_course
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/training",
)

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


@router.get('/dashboard')
def dashboard(pr_id: str = "0", tr_id: str = "0", zs_id: str = "0", fosa_id: str = "0",  db: Session = Depends(get_session)):
    return True
    #return dashboard_data(db=db)  

@router.get('/trainingcours')
def training_course(db: Session = Depends(get_session)):
    return True
    # return scheduled_training_course(db=db)