from manage.models import DocumentType as DocumentTypeModel
from manage.services.document_type.schemas import (
    DocumentTypeRead,
    DocumentTypeCreate,
    DocumentTypeUpdate,
)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from manage.database import SessionLocal
from endpoints.user_api import get_current_active_user
from manage.utils import make_id

apiRouter = APIRouter()


async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


# Get all document types
@apiRouter.get(
    "/document_types/",
    response_model=list[DocumentTypeRead],
    dependencies=[Depends(get_current_active_user)],
)
async def get_documenttypes(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(DocumentTypeModel).order_by(DocumentTypeModel.name))
    return result.scalars().all()


# Find a document type by id
@apiRouter.get(
    "/document_types/{documenttype_id}",
    response_model=DocumentTypeRead,
    dependencies=[Depends(get_current_active_user)],
)
async def get_documenttype(documenttype_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(DocumentTypeModel).where(DocumentTypeModel.id == documenttype_id)
    )
    document_type = result.scalar_one_or_none()
    if not document_type:
        raise HTTPException(status_code=404, detail="DocumentType not found")
    return document_type


# Create a document type
@apiRouter.post(
    "/document_types/",
    response_model=DocumentTypeRead,
    dependencies=[Depends(get_current_active_user)],
)
async def create_documenttype(
    doc_type: DocumentTypeCreate,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_active_user),
):
    data = doc_type.dict()  # pydantic v2 (use .dict() if v1)
    data["id"] = f"documenttype|{make_id(doc_type.name)}"   # ✅ use request value
    data["created_by"] = current_user_id

    new_doc_type = DocumentTypeModel(**data)
    session.add(new_doc_type)
    await session.commit()
    await session.refresh(new_doc_type)
    return new_doc_type


# Update an existing document type
@apiRouter.put(
    "/document_types/{documenttype_id}",
    response_model=DocumentTypeRead,
    dependencies=[Depends(get_current_active_user)],
)
async def update_documenttype(
    documenttype_id: str,
    payload: DocumentTypeUpdate,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_active_user),
):
    result = await session.execute(
        select(DocumentTypeModel).where(DocumentTypeModel.id == documenttype_id)
    )
    existing = result.scalar_one_or_none()
    if not existing:
        raise HTTPException(status_code=404, detail="DocumentType not found")

    updates = payload.dict(exclude_unset=True)  # only provided fields
    for key, value in updates.items():
        setattr(existing, key, value)

    setattr(existing, "last_modified_by", current_user_id)

    await session.commit()
    await session.refresh(existing)
    return existing


# Delete a document type
@apiRouter.delete(
    "/document_types/{documenttype_id}",
    dependencies=[Depends(get_current_active_user)],
)
async def delete_documenttype(documenttype_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(DocumentTypeModel).where(DocumentTypeModel.id == documenttype_id)
    )
    existing = result.scalar_one_or_none()
    if not existing:
        raise HTTPException(status_code=404, detail="DocumentType not found")

    await session.delete(existing)
    await session.commit()
    return {"detail": "DocumentType deleted successfully"}
