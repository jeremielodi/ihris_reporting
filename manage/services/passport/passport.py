# app/main.py
import uuid
import imghdr
import os
from pathlib import Path
from manage.utils import createUploadDirs
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from starlette.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user
from manage.services.passport.schemas import HippoPassportCreate,HippoPassportRead
from manage.models import HippoPersonPassport
from sqlalchemy.future import select

apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


# Serve uploaded files (http://localhost:8000/uploads/<filename>)
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR"))
UPLOAD_DIR.mkdir(parents=True, mode=777, exist_ok=True)

ALLOWED_TYPES = {"jpeg","jpg", "png", "webp", "gif"}

def _detect_type(byte_head: bytes) -> str | None:
    # imghdr is simple; for stricter validation use Pillow
    return imghdr.what(None, h=byte_head)


@apiRouter.get("/passport/upload/{person_id}")
async def get_image(
    person_id:str, 
    session: AsyncSession = Depends(get_session),
    response_model=list[HippoPassportRead],
    ):
        result = await session.execute(select(HippoPersonPassport).where(HippoPersonPassport.person_id == person_id))
        regions = result.scalars().all()
        return regions

@apiRouter.post("/passport/upload/{person_id}")
async def upload_image(
    person_id:str, 
    username: str = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session), file: UploadFile = File(...)):
    # Basic content-type check
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    # Read a small head chunk to validate type; then stream the rest
    head = await file.read(1024)
    
    root, ext  = os.path.splitext(file.filename)
    ext = ext.replace('.','')
    if ext not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported image type")

    # Build a safe filename
    
    datePath, passportDir = createUploadDirs("passports")
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
    
    data = HippoPassportCreate(id=uuid.uuid4().hex, path=filename, person_id=person_id)
    new_photo = HippoPersonPassport(**data.dict())
    session.add(new_photo)
    await session.commit()
    await session.refresh(new_photo)
    return JSONResponse({"filename": filename, "url": url})
