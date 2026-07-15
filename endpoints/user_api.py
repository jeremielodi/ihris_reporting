import os
from fastapi import APIRouter
from datetime import datetime, timedelta
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from config.Database2 import SessionLocal
from manage.database import SessionLocal
from models.usercrud import (
    _get_access_facility,
    _login,
    create_refresh_token,
    get_valid_refresh_token,
    revoke_refresh_token,
    findById,
)
from pydantic import BaseModel

# JWT signing secret. Must be set via env var in production.
# Falls back to the previous hardcoded value so existing tokens/deployments
# keep working until this is rotated deliberately (see .env_sample).
SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7",
)
ALGORITHM = "HS256"
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/reporting/login")




async def get_db() -> SessionLocal:
    async with SessionLocal() as session:
        yield session


class User(BaseModel):
    id: str | None = None
    username: str
    full_name: str | None = None
    disabled: bool | None = None


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        userid: str = payload.get("userid")

        usertype = payload.get("type")
        if usertype is not None:
            return userid

        if userid is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception



async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
   # if current_user.disabled:
    #    raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

api_user_router = APIRouter()


@api_user_router.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user

ACCESS_TOKEN_EXPIRE_MINUTES = 120

class UserLogin(BaseModel):
    user_id: str
    username: str
    token: str
    refresh_token: str
    access: dict
    validator: int

class UserLoginModel(BaseModel):
    username: str
    password: str

class RefreshTokenModel(BaseModel):
    refresh_token: str

class RefreshedToken(BaseModel):
    token: str
    refresh_token: str

@api_user_router.post('/users/reporting/login', response_model=UserLogin)
async def reporting_login(userCreate: UserLoginModel,  db: Session = Depends(get_db)):
    user = await _login(username=userCreate.username, password=userCreate.password, db=db)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    if not verify_password(userCreate.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    # S'assurer que _get_access_facility est sync, sinon await directement
    access_payload = await _get_access_facility(db=db, userid=user.id)

    access_token = create_access_token(
        data={"userid": user.id, "sub": user.username, "type": "reporting"},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = await create_refresh_token(db=db, user_id=user.id, expire_days=REFRESH_TOKEN_EXPIRE_DAYS)

    return UserLogin(
        user_id=user.id,
        username=user.username,
        token=access_token,
        refresh_token=refresh_token,
        access=access_payload,
        validator=1
    )


@api_user_router.post('/users/reporting/refresh', response_model=RefreshedToken)
async def reporting_refresh(payload: RefreshTokenModel, db: Session = Depends(get_db)):
    """
    Exchanges a valid, non-expired refresh token for a new access token.
    The refresh token is rotated (the old one is revoked) on every use.
    """
    row = await get_valid_refresh_token(db=db, token=payload.refresh_token)
    if not row:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user_id = row.user_id
    await revoke_refresh_token(db=db, row=row)

    user = await findById(user_id=user_id, db=db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    access_token = create_access_token(
        data={"userid": user.id, "sub": user.username, "type": "reporting"},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    new_refresh_token = await create_refresh_token(db=db, user_id=user.id, expire_days=REFRESH_TOKEN_EXPIRE_DAYS)

    return RefreshedToken(token=access_token, refresh_token=new_refresh_token)


@api_user_router.post('/users/reporting/logout')
async def reporting_logout(payload: RefreshTokenModel, db: Session = Depends(get_db)):
    """
    Revokes a refresh token so it can no longer be used to mint new access
    tokens. Always reports success, since the end state (token unusable)
    is the same whether it existed or not.
    """
    row = await get_valid_refresh_token(db=db, token=payload.refresh_token)
    if row:
        await revoke_refresh_token(db=db, row=row)
    return {"ok": True}


def serialize_access_facility(access: dict) -> dict:
    # access is the dict returned by _get_access_facility(...)
    def mini(o):
        if not o:
            return None
        # return only JSON-safe fields
        return {
            "id": getattr(o, "id", None),
            "name": getattr(o, "name", None),
        }

    return {
        "access_facility_row": (
            None if not access["access_facility_row"]
            else {
                "id": getattr(access["access_facility_row"], "id", None),
                "parent": getattr(access["access_facility_row"], "parent", None),
                "location": getattr(access["access_facility_row"], "location", None),
            }
        ),
        "access_facility": mini(access["access_facility"]),
        "access_facility_type": access["access_facility_type"],
        "access_facility_target": access["access_facility_target"],
        "facility_parents": [mini(p) for p in access.get("facility_parents", [])],
    }