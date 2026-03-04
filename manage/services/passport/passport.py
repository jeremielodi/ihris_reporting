# app/main.py

# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

# Unique ID generation
import uuid

# Image type detection (basic validation)
import imghdr

# OS utilities
import os

# Path handling
from pathlib import Path

# Utility to create dated upload directories
from manage.utils import createUploadDirs

# FastAPI utilities
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from starlette.staticfiles import StaticFiles

# Async DB session
from sqlalchemy.ext.asyncio import AsyncSession
from manage.database import SessionLocal, engine

# Authentication dependency
from endpoints.user_api import get_current_active_user

# Passport schemas
from manage.services.passport.schemas import HippoPassportCreate, HippoPassportRead

# ORM model
from manage.models import HippoPersonPassport

# SQLAlchemy query builder
from sqlalchemy.future import select


# Create router
apiRouter = APIRouter()


# ---------------------------------------------------------
# Dependency: Get Async Database Session
# ---------------------------------------------------------
async def get_session() -> AsyncSession:
    """
    Provides an async DB session.
    Ensures proper lifecycle handling (open/close).
    """
    async with SessionLocal() as session:
        yield session


# ---------------------------------------------------------
# UPLOAD DIRECTORY CONFIGURATION
# ---------------------------------------------------------

# Root upload directory from environment variable
# Example: /opt/uploads
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR"))

# Ensure directory exists
UPLOAD_DIR.mkdir(parents=True, mode=0o777, exist_ok=True)

# Allowed image file extensions
ALLOWED_TYPES = {"jpeg", "jpg", "png", "webp", "gif"}


def _detect_type(byte_head: bytes) -> str | None:
    """
    Detect image type from raw bytes.
    NOTE: imghdr is basic; for stricter validation use Pillow.
    """
    return imghdr.what(None, h=byte_head)


# =========================================================
# GET PASSPORT IMAGES FOR A PERSON
# =========================================================

@apiRouter.get("/passport/upload/{person_id}")
async def get_image(
    person_id: str,
    session: AsyncSession = Depends(get_session),
    response_model=list[HippoPassportRead],
):
    """
    Retrieve all passport images for a specific person.
    """

    result = await session.execute(
        select(HippoPersonPassport).where(
            HippoPersonPassport.person_id == person_id
        )
    )

    passports = result.scalars().all()
    return passports


# =========================================================
# UPLOAD PASSPORT IMAGE
# =========================================================

@apiRouter.post("/passport/upload/{person_id}")
async def upload_image(
    person_id: str,
    username: str = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
    file: UploadFile = File(...)
):
    """
    Upload a passport image for a person.

    Security measures:
    - Validate content-type starts with image/
    - Validate extension against allowed types
    - Stream file to disk (memory efficient)
    - Store file path in database
    """

    # -----------------------------------------------------
    # Validate Content-Type
    # -----------------------------------------------------
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    # Read first 1KB to inspect file header
    head = await file.read(1024)

    # Validate extension
    root, ext = os.path.splitext(file.filename)
    ext = ext.replace('.', '').lower()

    if ext not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported image type")

    # -----------------------------------------------------
    # Generate Safe Filename
    # -----------------------------------------------------

    # Create date-based upload directory (e.g. uploads/passports/2026/03/01)
    datePath, passportDir = createUploadDirs("passports")

    # Random filename prevents collision & path traversal
    filename = f"{uuid.uuid4().hex}.{ext}"

    # Absolute path on disk
    dest = passportDir / filename

    # Relative path saved in DB
    filename = f"{datePath}/{filename}"

    # -----------------------------------------------------
    # Stream File to Disk
    # -----------------------------------------------------
    # Write first chunk + stream rest in 1MB blocks
    with dest.open("wb") as f:
        f.write(head)

        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)

    # -----------------------------------------------------
    # Save Record in Database
    # -----------------------------------------------------

    # Public URL (assuming /uploads is statically served)
    url = f"/uploads/{filename}"

    # Create DB entry
    data = HippoPassportCreate(
        id=uuid.uuid4().hex,
        path=filename,
        person_id=person_id
    )

    new_photo = HippoPersonPassport(**data.dict())

    session.add(new_photo)
    await session.commit()
    await session.refresh(new_photo)

    return JSONResponse({
        "filename": filename,
        "url": url
    })