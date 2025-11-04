from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from manage.database import SessionLocal
from models.models import Cadre, Classification, County, District, Facility, HealthArea, Job
from manage.models import HippoJob
router = APIRouter(
    
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get('/cadres')
async def cadre(db: Session = Depends(get_db)):
    stmt = select(Cadre).where(Cadre.i2ce_hidden == 0).order_by(Cadre.name.asc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get('/jobs')
async def job(db: Session = Depends(get_db)):
    stmt = select(HippoJob).where(HippoJob.i2ce_hidden == 0).order_by(HippoJob.title.asc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get('/classifications')
async def classification(db: Session = Depends(get_db)):
    stmt = select(Classification).where(Classification.i2ce_hidden == 0).order_by(Classification.name.asc())
    result = await db.execute(stmt)
    return result.scalars().all()
