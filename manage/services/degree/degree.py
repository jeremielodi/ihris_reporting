from manage.models import Base, HippoDegree
from manage.services.degree.schemas import HippoDegreeRead, HippoDegreeCreate, HippoDegreeUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user
apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

# Get all degrees
@apiRouter.get("/degrees/", response_model=list[HippoDegreeRead], 
                    dependencies=[Depends(get_current_active_user)],)
async def get_degrees(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoDegree).order_by(HippoDegree.name))
    degrees = result.scalars().all()
    return degrees


# find a degree by id
@apiRouter.get("/degrees/{degree_id}", response_model=HippoDegreeRead,  dependencies=[Depends(get_current_active_user)],)
async def get_degree(degree_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoDegree).where(HippoDegree.id == degree_id).order_by(HippoDegree.name))
    degree = result.scalar_one_or_none()
    if not degree:
        raise HTTPException(status_code=404, detail="Degree not found")
    return degree

# create a new degree
@apiRouter.post("/degrees/", response_model=HippoDegreeRead,  dependencies=[Depends(get_current_active_user)],)
async def create_degree(degree: HippoDegreeCreate, session: AsyncSession = Depends(get_session)):
    degree_data = degree.dict()
    degree_data['id'] = f"degree|{degree.name}"
    new_degree = HippoDegree(**degree_data)
    session.add(new_degree)
    await session.commit()
    await session.refresh(new_degree)
    return new_degree

# update an existing degree
@apiRouter.put("/degrees/{degree_id}", response_model=HippoDegreeRead,  dependencies=[Depends(get_current_active_user)],)
async def update_degree(degree_id: str, degree: HippoDegreeUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoDegree).where(HippoDegree.id == degree_id))
    existing_degree = result.scalar_one_or_none()
    if not existing_degree:
        raise HTTPException(status_code=404, detail="Degree not found")
    
    for key, value in degree.dict().items():
        setattr(existing_degree, key, value)
    
    await session.commit()
    await session.refresh(existing_degree)
    return existing_degree  

# delete a degree
@apiRouter.delete("/degrees/{degree_id}",  dependencies=[Depends(get_current_active_user)],)
async def delete_degree(degree_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoDegree).where(HippoDegree.id == degree_id))
    existing_degree = result.scalar_one_or_none()
    if not existing_degree:
        raise HTTPException(status_code=404, detail="Degree not found")
    
    await session.delete(existing_degree)
    await session.commit()
    return {"detail": "Degree deleted successfully"}