# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

# OS utilities (file handling)
import os

# UUID generation (used for safe filename creation)
import uuid

# ORM model
from manage.models import HippoSetting

# Pydantic schemas (response + update validation)
from manage.services.settings.schemas import (
    HippoSettingRead,
    HippoSettingCreate,
    HippoSettingUpdate
)

# Async DB session
from sqlalchemy.ext.asyncio import AsyncSession

# FastAPI utilities
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException

# SQLAlchemy query builder
from sqlalchemy.future import select

# Database session factory
from manage.database import SessionLocal, engine

# Authentication dependency
from endpoints.user_api import get_current_active_user

# Utility to create upload directory structure
from manage.utils import createUploadDirs

# JSON response helper
from fastapi.responses import JSONResponse


# Create API router
apiRouter = APIRouter()

# Routes that must stay reachable without a Bearer token (e.g. the login
# page fetches the app's branding via GET /settings/{id} before the user
# is authenticated). Mounted directly on the app in main.py, outside the
# router-level auth dependency applied to the rest of /manage.
public_router = APIRouter()


# ---------------------------------------------------------
# Dependency: Get Async DB Session
# ---------------------------------------------------------
async def get_session() -> AsyncSession:
    """
    Provides an async database session.
    Ensures proper open/close lifecycle management.
    """
    async with SessionLocal() as session:
        yield session


# ---------------------------------------------------------
# GET ALL SETTINGS
# ---------------------------------------------------------
@apiRouter.get(
    "/settings/",
    response_model=list[HippoSettingRead],
    dependencies=[Depends(get_current_active_user)],
)
async def get_settings(session: AsyncSession = Depends(get_session)):
    """
    Retrieve all application settings.
    Requires authenticated user.
    """
    result = await session.execute(select(HippoSetting))
    settings = result.scalars().all()
    return settings


# ---------------------------------------------------------
# GET SETTING BY ID
# ---------------------------------------------------------
@public_router.get("/settings/{setting_id}", response_model=HippoSettingRead)
async def get_Setting(setting_id: int, session: AsyncSession = Depends(get_session)):
    """
    Retrieve a single setting by its ID.
    Returns 404 if not found.
    """
    result = await session.execute(
        select(HippoSetting).where(HippoSetting.id == setting_id)
    )

    Setting = result.scalar_one_or_none()

    if not Setting:
        raise HTTPException(status_code=404, detail="Setting not found")

    return Setting


# ---------------------------------------------------------
# UPDATE SETTING
# ---------------------------------------------------------
@apiRouter.put("/settings/{setting_id}", response_model=HippoSettingRead)
async def update_Setting(
    setting_id: int,
    Setting: HippoSettingUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    Update an existing setting.

    - Only non-null fields are updated.
    - 'id' and 'created' fields are protected.
    """

    result = await session.execute(
        select(HippoSetting).where(HippoSetting.id == setting_id)
    )
    existing_Setting = result.scalar_one_or_none()

    if not existing_Setting:
        raise HTTPException(status_code=404, detail="Setting not found")

    # Apply partial update (ignore id & created fields)
    for key, value in Setting.model_dump().items():
        if value is not None and key not in ('id', 'created'):
            setattr(existing_Setting, key, value)

    await session.commit()
    await session.refresh(existing_Setting)

    return existing_Setting


# ---------------------------------------------------------
# UPLOAD LOGO IMAGE
# ---------------------------------------------------------
@apiRouter.post("/settings/logo/upload/{appId}")
async def upload_image(
    appId: int,
    username: str = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
    file: UploadFile = File(...)
):
    """
    Upload a logo image for a specific application setting.

    Security Measures:
    - Validates content-type starts with 'image/'
    - Validates file extension against allowed types
    - Generates safe random filename using UUID
    - Streams file to disk (avoids loading entire file in memory)
    """

    # -----------------------------------------------------
    # Validate Content-Type
    # -----------------------------------------------------
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    # Read first 1KB for initial validation
    head = await file.read(1024)

    # Allowed extensions
    ALLOWED_TYPES = {"jpeg", "jpg", "png", "webp", "gif"}

    # Extract extension
    root, ext = os.path.splitext(file.filename)
    ext = ext.replace('.', '').lower()

    if ext not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported image type")

    # -----------------------------------------------------
    # Generate Safe Filename
    # -----------------------------------------------------
    datePath, passportDir = createUploadDirs("logo")

    # Randomized filename prevents collisions & path traversal
    filename = f"{uuid.uuid4().hex}.{ext}"

    # Absolute file destination path
    dest = passportDir / filename

    # Relative filename stored in DB
    filename = f"{datePath}/{filename}"

    # -----------------------------------------------------
    # Stream File to Disk (Memory Efficient)
    # -----------------------------------------------------
    with dest.open("wb") as f:
        # Write first chunk
        f.write(head)

        # Stream remaining file in 1MB chunks
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)

    # -----------------------------------------------------
    # Update Setting Record
    # -----------------------------------------------------
    result = await session.execute(
        select(HippoSetting).where(HippoSetting.id == appId)
    )
    existing_Setting = result.scalar_one_or_none()

    if not existing_Setting:
        raise HTTPException(status_code=404, detail="Setting not found")

    # Save relative file path in DB
    setattr(existing_Setting, 'logo', filename)

    await session.commit()
    await session.refresh(existing_Setting)

    # Public URL (assuming /uploads is served statically)
    url = f"/uploads/{filename}"

    return JSONResponse({
        "filename": filename,
        "url": url
    })

@apiRouter.post(
    "/settings/",
    response_model=HippoSettingRead,
    dependencies=[Depends(get_current_active_user)]
)
async def create_Setting(
    Setting: HippoSettingCreate,
    session: AsyncSession = Depends(get_session)
):
    """
    Create a new Setting (application record).

    - Requires authenticated active user.
    - Optionally ensures uniqueness by app_name.
    """

    # Optional uniqueness check on app_name
    if Setting.app_name:
        result = await session.execute(
            select(HippoSetting).where(HippoSetting.app_name == Setting.app_name)
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=400, detail="Setting with this app_name already exists")

    data = Setting.model_dump()
    # data.pop("id", None)  # ensure DB auto-generates numeric ID

    new_setting = HippoSetting(**data)
    session.add(new_setting)
    await session.commit()
    await session.refresh(new_setting)

    return new_setting