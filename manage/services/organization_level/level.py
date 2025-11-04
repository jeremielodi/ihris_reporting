from manage.models import OrganizationLevel
from manage.services.organization_level.schemas import OrganizationUnitLevelRead
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user
from sqlalchemy import text

apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


@apiRouter.get("/organization_levels", response_model=list[OrganizationUnitLevelRead], dependencies=[Depends(get_current_active_user)],)
async def get_OrganisationLevels(db: AsyncSession = Depends(get_session)):
    result = await db.execute(text("""
        SELECT *
        FROM organization_level                                      
    """))
    rows = result.mappings().all()
    return rows


# Get all healthareas
@apiRouter.get("/organization_levels/{id}", response_model=OrganizationUnitLevelRead, dependencies=[Depends(get_current_active_user)],)
async def get_OrganisationLevel(id:str,db: AsyncSession = Depends(get_session)):
    result = await db.execute(text(f"""
        SELECT *
        FROM organization_level 
        WHERE id='{id}'                                     
    """))
    rows = result.mappings().all()
    if len(rows) == 0:
        raise HTTPException(status_code=404, detail="Organization level not found")
    return rows[0]
