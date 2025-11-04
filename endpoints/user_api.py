from fastapi import APIRouter
from datetime import datetime, timedelta
from typing import Annotated
from fastapi import Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from config.Database2 import SessionLocal
from manage.database import SessionLocal
from models.models import PersonValidator
from models.usercrud import _get_access_facility, _login
from sqlalchemy.future import select
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, EmailStr
# to get a string like this run:
# openssl rand -hex 32

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 48000

fake_users_db = {
    "ihris-reporting": {
        "username": "ihris-reporting",
        "full_name": "IHRIS Reporting",
        "hashed_password": "$2b$12$4qzbD.4iqbjeP/ET5ICNeeTwsYxwKx4YlUGom4YE3Ft/WSEOv3TEy",
        "disabled": False,
    },
    "usimamizi": {
        "username": "usimamizi",
        "full_name": "USIMAMIZI KC",
        "hashed_password": "$2b$12$iyGsXMwdD5kh86HA22d94utrv2Nk.AcM4xojz8/5FKmgmL2JSExyq",
        "disabled": False,
    }
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")




async def get_db() -> SessionLocal:
    async with SessionLocal() as session:
        yield session


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    userid: str | None = None
    username: str | None = None


class User(BaseModel):
    id: str | None = None
    username: str
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


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


@api_user_router.post("/token", response_model=Token, tags=['users'],)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):

    user = authenticate_user(
        fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={ "userid": user.id, "sub": user.username}, expires_delta=access_token_expires
    )
   
    return {"access_token": access_token, "token_type": "bearer", "validator": validator}


@api_user_router.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user

ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Exemple

class UserLogin(BaseModel):
    user_id: str
    username: str
    token: str
    access: dict
    validator: int

class UserLoginModel(BaseModel):
    username: str
    password: str

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

    return UserLogin(
        user_id=user.id,
        username=user.username,
        token=access_token,
        access=access_payload,
        validator=1
    )


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