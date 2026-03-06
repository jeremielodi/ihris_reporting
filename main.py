"""
FastAPI application entrypoint (iHRIS Reporting)

What this module does
---------------------
- Creates the FastAPI app instance
- Configures CORS and static file mounts (/static, /uploads)
- Initializes DB tables at startup (dev/demo only)
- Registers all API routers with consistent prefixes/tags/dependencies
- Exposes a health/home endpoint "/"
"""

from __future__ import annotations

import logging
import os
import secrets
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import weasyprint

# ----------------------------
# Internal imports (your app)
# ----------------------------
import endpoints.person_api
import endpoints.user_api
import endpoints.reports_api
import endpoints.utils_api
import endpoints.person_file_api
import endpoints.validation_api
from security import SecurityHeadersMiddleware
from endpoints.metabase import metabase_apy
from endpoints.pyramid_api import router as pyramid_router

from config.Database import docAccess
from manage.database import engine
from manage.models import Base
from manage.routes import router as manageApiRouter


# ---------------------------------------------------------
# Logging / third-party setup
# ---------------------------------------------------------
weasyprint.DEBUG = False
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# App factory (recommended)
# ---------------------------------------------------------
def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Why use an app factory?
    - Easier testing (create app with different configs)
    - Cleaner organization (no duplicated app instances)
    - Avoids accidental re-initialization issues
    """

    # Disable auto docs endpoints (as in your current code)
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

    # ----------------------------
    # Templates (if needed)
    # ----------------------------
    # If you actually use templates in endpoints:
    templates = Jinja2Templates(directory="templates")
    # Keep `templates` variable for dependency injection later if needed
    app.state.templates = templates

    # ----------------------------
    # Static files: /static
    # ----------------------------
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # ----------------------------
    # Uploads: /uploads
    # ----------------------------
    upload_dir = Path(os.getenv("UPLOAD_DIR", "uploads")).resolve()
    upload_dir.mkdir(parents=True, exist_ok=True)
    app.state.upload_dir = upload_dir
    app.mount("/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")

    # ----------------------------
    # CORS
    # ----------------------------
    # In production, avoid "*" and restrict allowed origins.
    # origins = ["*"]
    # app.add_middleware(
    #     CORSMiddleware,
    #     allow_origins=origins,
    #     allow_credentials=True,
    #     allow_methods=["*"],
    #     allow_headers=["*"],
    # )

    ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",")  # "https://app.com,https://admin.com"
    ALLOWED_ORIGINS = [o.strip() for o in ALLOWED_ORIGINS if o.strip()]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(SecurityHeadersMiddleware)

    # ----------------------------
    # Routers registration
    # ----------------------------
    register_routes(app)

    # ----------------------------
    # Health/Home
    # ----------------------------
    @app.get("/", tags=["meta"])
    def home():
        return {"message": "iHRIS Reporting v1.3.2"}

    return app


# ---------------------------------------------------------
# Security: Basic auth helper (used for docs or restricted routes)
# ---------------------------------------------------------
security = HTTPBasic()


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """
    Basic-auth guard using credentials stored in config.Database.docAccess.

    NOTE:
    - This is separate from your JWT auth (get_current_active_user).
    - Use this only for endpoints that should be protected via Basic auth.
    """
    correct_username = secrets.compare_digest(credentials.username, docAccess["username"])
    correct_password = secrets.compare_digest(credentials.password, docAccess["password"])

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username


# ---------------------------------------------------------
# Route registration (single place)
# ---------------------------------------------------------
def register_routes(app: FastAPI) -> None:
    """
    Register all routers with consistent prefixes / tags / dependencies.
    Keeps the main app factory clean.
    """

    # Shared auth dependency (JWT)
    # Everything that must be authenticated should use this.
    require_auth = Depends(endpoints.user_api.get_current_active_user)

    # Manage API (already has its own routes inside manage/routes.py)
    app.include_router(manageApiRouter, prefix="/manage", tags=["manage"])

    # Auth / users endpoints (some of these include login endpoints)
    app.include_router(endpoints.user_api.api_user_router, tags=["users"])

    # People endpoints
    app.include_router(
        endpoints.person_api.router,
        prefix="/people",
        tags=["people"],
        dependencies=[require_auth],
    )

    # Reports endpoints
    app.include_router(
        endpoints.reports_api.router,
        prefix="/reports",
        tags=["reports"],
        dependencies=[require_auth],
    )

    # Metabase reporting endpoints (also under /reports)
    app.include_router(
        metabase_apy.router,
        prefix="/reports",
        tags=["reports"],
        dependencies=[require_auth],
    )

    # Pyramid/location endpoints
    # IMPORTANT: You were including pyramid_router twice with different tags.
    # Pick one tag (or split routers if they are truly different modules).
    app.include_router(
        pyramid_router,
        tags=["location"],
        dependencies=[require_auth],
    )

    # Utils endpoints
    app.include_router(
        endpoints.utils_api.router,
        prefix="/utils",
        tags=["utils"],
        dependencies=[require_auth],
    )

    # Files endpoints
    # NOTE: You had no auth dependency here; keep it if intended, otherwise add `dependencies=[require_auth]`.
    app.include_router(
        endpoints.person_file_api.router,
        prefix="/files",
        tags=["files"],
        # dependencies=[require_auth],  # uncomment if required
    )

    # Validation endpoints
    # NOTE: same here: add auth if needed.
    app.include_router(
        endpoints.validation_api.router,
        tags=["validation"],
        # dependencies=[require_auth],  # uncomment if required
    )


# ---------------------------------------------------------
# Create the app instance (ASGI entrypoint)
# ---------------------------------------------------------
app = create_app()