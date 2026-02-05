from fastapi.middleware.cors import CORSMiddleware
import endpoints.person_api
import endpoints.user_api
import endpoints.reports_api
import endpoints.utils_api
import endpoints.person_file_api
from fastapi import Depends, FastAPI
import secrets
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from config.Database import  docAccess
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import weasyprint
import logging
from manage.database import  engine
from manage.models import Base
from manage.routes import manageApiRouter
import os
from pathlib import Path
import endpoints.validation_api
from  endpoints.metabase import metabase_apy
from endpoints.pyramid_api import router as pyramid_router
weasyprint.DEBUG = False
logging.basicConfig(level=logging.DEBUG)

app = FastAPI(docs_url=None, redoc_url=None, openapi_url = None)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR"))

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url = None,
)
origins = ["*"] 
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables (for demo purposes; use Alembic for production!)
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


security = HTTPBasic()
def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, docAccess['username'])
    correct_password = secrets.compare_digest(credentials.password, docAccess["password"])
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

app.include_router(manageApiRouter, prefix="/manage", tags=["manage"],)

app.include_router(endpoints.user_api.api_user_router, tags=['users'])
app.include_router(endpoints.person_api.router, dependencies=[Depends(endpoints.user_api.get_current_active_user)], tags=['people'], prefix="/people")
app.include_router(endpoints.reports_api.router, dependencies=[Depends(endpoints.user_api.get_current_active_user)],tags=['reports'], prefix="/reports")


app.include_router(metabase_apy.router, tags=['reports'],dependencies=[Depends(endpoints.user_api.get_current_active_user)],prefix="/reports")


app.include_router(pyramid_router,dependencies=[Depends(endpoints.user_api.get_current_active_user)], tags=['location'])
app.include_router(pyramid_router, dependencies=[Depends(endpoints.user_api.get_current_active_user)], tags=['Training'])

app.include_router(endpoints.utils_api.router,prefix="/utils",   dependencies=[Depends(endpoints.user_api.get_current_active_user)],tags=['Utils'])



app.include_router(endpoints.person_file_api.router,prefix="/files",  tags=['Files'])

app.include_router(endpoints.validation_api.router)

@app.get("/")
def home():
    return {"massage": "iHRIS Reporting fast v1.3.1"}


 
 

