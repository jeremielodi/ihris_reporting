# manage/routes/norm_requirement.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from manage.database import SessionLocal, engine
from typing import List
from endpoints.user_api import get_current_active_user

from manage.services.norms.schema import (
    NormRequirementCreate,
    NormRequirementUpdate,
    NormRequirementRead
)
from manage.models import NormRequirement
from manage.services.norms.norm_requirement_repo import NormRequirementRepository


async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session



APIRouter = APIRouter()

@APIRouter.post("/norm-requirements", 
                response_model=NormRequirementRead, status_code=status.HTTP_201_CREATED,
                dependencies=[Depends(get_current_active_user)],)
async def create_norm(
    payload: NormRequirementCreate,
    db: AsyncSession = Depends(get_session),
    
):

    return await NormRequirementRepository.create(db, payload.organization_unit_type_id, payload.classification_id, payload.required)

@APIRouter.get(
    "/norm-requirements",
    response_model=List[NormRequirementRead]
)
async def list_all_norms(
    db: AsyncSession = Depends(get_session)
):
    return await NormRequirementRepository.list_all(db)

@APIRouter.get(
    "/norm-requirements/{id}",
    response_model=NormRequirementRead
)
async def list_norms_by_type(
    id: str,
    db: AsyncSession = Depends(get_session)
):
    return await NormRequirementRepository.find_by_id(db, id)



@APIRouter.get(
    "/norm-requirements/{organization_unit_type_id}/{classification_id}",
    response_model=NormRequirementRead
)
async def get_norm(
    organization_unit_type_id: str,
    classification_id: str,
    db: AsyncSession = Depends(get_session)
):
    obj = await NormRequirementRepository.get(
        db, organization_unit_type_id, classification_id
    )
    if not obj:
        raise HTTPException(status_code=404, detail="Norm requirement not found")
    return obj


@APIRouter.put(
    "/norm-requirements/{id}",
    response_model=NormRequirementRead,
    dependencies=[Depends(get_current_active_user)],
)
async def update_norm(
    id: str,
    payload: NormRequirementUpdate,
    db: AsyncSession = Depends(get_session)
):
 
    return await NormRequirementRepository.update(db,id, payload.organization_unit_type_id, payload.classification_id, payload.required)


@APIRouter.delete(
    "/norm-requirements/{organization_unit_type_id}/{classification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_active_user)],
)
async def delete_norm(
    organization_unit_type_id: str,
    classification_id: str,
    db: AsyncSession = Depends(get_session)
):
    await NormRequirementRepository.delete(
        db, organization_unit_type_id, classification_id
    )
