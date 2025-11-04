
import os
import uuid
from manage.models import HippoSetting
from manage.services.settings.schemas import HippoSettingRead, HippoSettingUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, UploadFile,File, HTTPException
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user
from manage.utils import createUploadDirs
from fastapi.responses import JSONResponse

apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

# Get all settings
@apiRouter.get("/settings/", response_model=list[HippoSettingRead], dependencies=[Depends(get_current_active_user)],)
async def get_settings(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoSetting))
    settings = result.scalars().all()
    return settings


# find a Setting by id
@apiRouter.get("/settings/{setting_id}", response_model=HippoSettingRead)
async def get_Setting(setting_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoSetting).where(HippoSetting.id == setting_id))
    Setting = result.scalar_one_or_none()
    if not Setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return Setting


# update an existing Setting
@apiRouter.put("/settings/{setting_id}", response_model=HippoSettingRead)
async def update_Setting(setting_id: int, Setting:HippoSettingUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoSetting).where(HippoSetting.id == setting_id))
    existing_Setting = result.scalar_one_or_none()
    if not existing_Setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    for key, value in Setting.dict().items():
        if value != None and (key != 'id') and (key != 'created'):
            setattr(existing_Setting, key, value)
    await session.commit()
    await session.refresh(existing_Setting)
    return existing_Setting  


@apiRouter.post("/settings/logo/upload/{appId}")
async def upload_image(
    appId:int, 
    username: str = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session), file: UploadFile = File(...)):
    # Basic content-type check
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    # Read a small head chunk to validate type; then stream the rest
    head = await file.read(1024)
    
    ALLOWED_TYPES = {"jpeg","jpg", "png", "webp", "gif"}
    root, ext  = os.path.splitext(file.filename)
    ext = ext.replace('.','')
    if ext not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported image type")

    # Build a safe filename
    
    datePath, passportDir = createUploadDirs("logo")
    filename = f"{uuid.uuid4().hex}.{ext}"
    dest = passportDir / filename
    filename = f"{datePath}/{filename}"
    # Write the head + remaining body to disk (streaming, avoids loading entire file)
    with dest.open("wb") as f:
        f.write(head)
        # stream remaining chunks
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)

    # Optionally: save path in DB here

    url = f"/uploads/{filename}"
    
    result = await session.execute(select(HippoSetting).where(HippoSetting.id == appId))
    existing_Setting = result.scalar_one_or_none()
    if not existing_Setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    setattr(existing_Setting, 'logo', filename)

    await session.commit()
    await session.refresh(existing_Setting)

    return JSONResponse({"filename": filename, "url": url})


