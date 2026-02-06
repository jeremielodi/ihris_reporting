# app/main.py
import uuid
import imghdr
import os
import lzma
from sqlalchemy import and_
from fastapi.responses import StreamingResponse
from io import BytesIO
from pathlib import Path
from manage.utils import createUploadDirs
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user
from manage.services.document.schemas import DocumentCreate, DocumentRead
from manage.models import HippoPersonDocument, DocumentType, HippoAuditLog
from sqlalchemy.future import select

apiRouter = APIRouter()


async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


# Serve uploaded files (http://localhost:8000/uploads/<filename>)
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR") or "./uploads")
UPLOAD_DIR.mkdir(parents=True, mode=0o777, exist_ok=True)

ALLOWED_TYPES = {"pdf"}


def _detect_type(byte_head: bytes) -> str | None:
    # imghdr is simple; for stricter validation use Pillow
    return imghdr.what(None, h=byte_head)


@apiRouter.get(
    "/documents/upload/{person_id}",
    response_model=list[DocumentRead],
    dependencies=[Depends(get_current_active_user)],
)
async def get_documents(
    person_id: str,
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(
            HippoPersonDocument,
            DocumentType.name.label("document_type_name"),
        )
        .join(
            DocumentType,
            DocumentType.id == HippoPersonDocument.type_id,
            isouter=True,  # LEFT JOIN
        )
        .where(
            
            HippoPersonDocument.person_id == person_id,
          
        )
    )

    result = await session.execute(stmt)

    documents = []
    for doc, document_type_name in result.all():
        documents.append(
            {
                **doc.__dict__,
                "document_type_name": document_type_name,
            }
        )

    return documents


@apiRouter.get(
    "/documents/{document_id}/pdf",
    dependencies=[Depends(get_current_active_user)],
)
async def get_document_pdf(
    document_id: str,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(HippoPersonDocument).where(HippoPersonDocument.id == document_id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    xz_path = UPLOAD_DIR / doc.path
    if not xz_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    try:
        with lzma.open(xz_path, "rb") as f:
            pdf_bytes = f.read()
    except lzma.LZMAError:
        raise HTTPException(status_code=400, detail="Invalid xz file")

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            # IMPORTANT: inline + binary
            "Content-Disposition": f'inline; filename="{document_id}.pdf"',
            "Content-Length": str(len(pdf_bytes)),
            "Cache-Control": "no-store",
        },
    )


@apiRouter.post("/documents/upload/{person_id}", dependencies=[Depends(get_current_active_user)])
async def upload_image(
    person_id: str,
    type_id: str = Form(..., alias="type_id"),
    description: str = Form(..., alias="description"),
    current_user_id: str = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
    file: UploadFile = File(...),
):
    if not file.content_type.startswith("application/pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    _, ext = os.path.splitext(file.filename)
    ext = ext.replace(".", "").lower()
    if ext not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported PDF type")

    # create dirs
    datePath, passportDir = createUploadDirs("documents")

    base_id = uuid.uuid4().hex
    pdf_filename = f"{base_id}.pdf"
    pdf_dest = passportDir / pdf_filename

    # write PDF to temp file (streaming)
    head = await file.read(1024)
    with pdf_dest.open("wb") as f:
        f.write(head)
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)

    # compress to .xz (LZMA)
    xz_filename = f"{base_id}.pdf.xz"
    xz_dest = passportDir / xz_filename

    try:
        with pdf_dest.open("rb") as f_in, lzma.open(xz_dest, "wb") as f_out:
            while True:
                chunk = f_in.read(1024 * 1024)
                if not chunk:
                    break
                f_out.write(chunk)
    finally:
        # remove raw PDF after compressing
        if pdf_dest.exists():
            pdf_dest.unlink()

    # store .xz path in DB
    stored_path = f"{datePath}/{xz_filename}"
    url = f"/uploads/{stored_path}"

    data = DocumentCreate(
        id=uuid.uuid4().hex,
        path=stored_path,  # <-- now points to .pdf.xz
        person_id=person_id,
        description=description,
        type_id=type_id,
    )

    new_document = HippoPersonDocument(**data.dict())
    new_document.created_by = current_user_id

    session.add(new_document)
    await session.commit()


    auditLog = HippoAuditLog(id= uuid.uuid4(), user_id=current_user_id, operation=f'create document id:{new_document.id}, path: {new_document.path}')
    session.add(auditLog)

    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(
                status_code=500,
                detail=f"Failed to upload file in disk  {str(e)}",
            )
    await session.refresh(new_document)

    return JSONResponse({"filename": stored_path, "url": url, "document_id": new_document.id})

@apiRouter.delete(
    "/documents/{document_id}",
    dependencies=[Depends(get_current_active_user)],
)
async def delete_document(
    document_id: str,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_active_user),
):
    # find document
    result = await session.execute(
        select(HippoPersonDocument).where(HippoPersonDocument.id == document_id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # delete file on disk
    file_path = UPLOAD_DIR / doc.path
    if file_path.exists():
        try:
            file_path.unlink()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete file from disk: {str(e)}",
            )

    # delete DB record
    await session.delete(doc)

    auditLog = HippoAuditLog(id= uuid.uuid4(), user_id=current_user_id, operation=f'Delete document id:{doc.id}, path: {doc.path}')
    session.add(auditLog)

    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(
                status_code=500,
                detail=f"Failed to delete file from disk: {str(e)}",
            )

    return {
        "detail": "Document deleted successfully",
        "document_id": document_id,
    }