# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

# ORM model (aliased for clarity)
from manage.models import DocumentType as DocumentTypeModel

# Pydantic schemas (validation + serialization)
from manage.services.document_type.schemas import (
    DocumentTypeRead,
    DocumentTypeCreate,
    DocumentTypeUpdate,
)

# Async database session
from sqlalchemy.ext.asyncio import AsyncSession

# FastAPI utilities
from fastapi import APIRouter, Depends, HTTPException

# SQLAlchemy query builder
from sqlalchemy import select

# Database session factory
from manage.database import SessionLocal

# Authentication dependency
from endpoints.user_api import get_current_active_user

# Utility function to generate clean IDs
from manage.utils import make_id


# Create API router
apiRouter = APIRouter()


# ---------------------------------------------------------
# Dependency: Get Async Database Session
# ---------------------------------------------------------
async def get_session() -> AsyncSession:
    """
    Provides an async database session.
    Ensures proper lifecycle handling (open/close).
    """
    async with SessionLocal() as session:
        yield session


# =========================================================
# GET ALL DOCUMENT TYPES
# =========================================================

@apiRouter.get(
    "/document_types/",
    response_model=list[DocumentTypeRead],
    dependencies=[Depends(get_current_active_user)],
)
async def get_documenttypes(session: AsyncSession = Depends(get_session)):
    """
    Retrieve all document types ordered alphabetically by name.

    Example:
    - Employment Contract
    - ID Card
    - Diploma
    - Medical Certificate
    """

    result = await session.execute(
        select(DocumentTypeModel).order_by(DocumentTypeModel.name)
    )

    return result.scalars().all()


# =========================================================
# GET DOCUMENT TYPE BY ID
# =========================================================

@apiRouter.get(
    "/document_types/{documenttype_id}",
    response_model=DocumentTypeRead,
    dependencies=[Depends(get_current_active_user)],
)
async def get_documenttype(
    documenttype_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieve a specific document type by ID.

    Returns:
    - 404 if not found.
    """

    result = await session.execute(
        select(DocumentTypeModel).where(
            DocumentTypeModel.id == documenttype_id
        )
    )

    document_type = result.scalar_one_or_none()

    if not document_type:
        raise HTTPException(status_code=404, detail="DocumentType not found")

    return document_type


# =========================================================
# CREATE DOCUMENT TYPE
# =========================================================

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
    """
    Create a new document type.

    - ID is generated using:
        documenttype|<normalized_name>
    - created_by is stored for audit tracking.
    """

    data = doc_type.dict()

    # Generate consistent ID using utility
    data["id"] = f"documenttype|{make_id(doc_type.name)}"

    # Audit field
    data["created_by"] = current_user_id

    new_doc_type = DocumentTypeModel(**data)

    session.add(new_doc_type)
    await session.commit()
    await session.refresh(new_doc_type)

    return new_doc_type


# =========================================================
# UPDATE DOCUMENT TYPE
# =========================================================

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
    """
    Update an existing document type.

    - Only provided fields are updated (partial update).
    - Updates audit field (last_modified_by).
    """

    result = await session.execute(
        select(DocumentTypeModel).where(
            DocumentTypeModel.id == documenttype_id
        )
    )

    existing = result.scalar_one_or_none()

    if not existing:
        raise HTTPException(status_code=404, detail="DocumentType not found")

    # Update only provided fields
    updates = payload.dict(exclude_unset=True)

    for key, value in updates.items():
        setattr(existing, key, value)

    # Audit tracking
    setattr(existing, "last_modified_by", current_user_id)

    await session.commit()
    await session.refresh(existing)

    return existing


# =========================================================
# DELETE DOCUMENT TYPE
# =========================================================

@apiRouter.delete(
    "/document_types/{documenttype_id}",
    dependencies=[Depends(get_current_active_user)],
)
async def delete_documenttype(
    documenttype_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete a document type.

    WARNING:
    If this type is referenced in employee documents,
    deletion should be prevented or replaced with soft delete.
    """

    result = await session.execute(
        select(DocumentTypeModel).where(
            DocumentTypeModel.id == documenttype_id
        )
    )

    existing = result.scalar_one_or_none()

    if not existing:
        raise HTTPException(status_code=404, detail="DocumentType not found")

    await session.delete(existing)
    await session.commit()

    return {"detail": "DocumentType deleted successfully"}