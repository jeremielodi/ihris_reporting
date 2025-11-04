from manage.models import Base, HippoUser, HippoAccessFacility, ViewOrgUnitList
from manage.services.user.schemas import HippoUserCreate, HippoUserRead, HippoUserUpdate, HippoUserChangePassword
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user,  get_password_hash
from datetime import datetime
from passlib.context import CryptContext


apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

# Get all degrees
@apiRouter.get("/users/", response_model=list[HippoUserRead], 
                    dependencies=[Depends(get_current_active_user)],)
async def get_users(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoUser))
    users = result.scalars().all()
    return users


# find a user by id
@apiRouter.get("/users/{user_id}", response_model=HippoUserRead,  dependencies=[Depends(get_current_active_user)],)
async def get_user(user_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(HippoUser).where(HippoUser.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@apiRouter.post(
    '/users/changeSelfPassword',
    response_model=HippoUserRead,
    dependencies=[Depends(get_current_active_user)]
)
async def changeSelfPassword(
    data: HippoUserChangePassword,
    session: AsyncSession = Depends(get_session)
):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    # find user
    result = await session.execute(
        select(HippoUser).where(HippoUser.id == data.user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # check confirm
    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # check old password
    if not pwd_context.verify(data.old_password, user.password):
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    # update to new password
    user.password = pwd_context.hash(data.new_password)
    session.add(user)

    try:
        await session.commit()
        await session.refresh(user)
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating password: {e}")

    return user


@apiRouter.post("/users/", response_model=HippoUserRead, dependencies=[Depends(get_current_active_user)])
async def create_user(
    user: HippoUserCreate,
    session: AsyncSession = Depends(get_session),
):
    # build IDs
    user_id = f"user|{user.username}"
    access_id = f"access|{user.username}"

    # ensure unique username
    existing = await session.execute(
        select(HippoUser).where(HippoUser.username == user.username)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists.",
        )

    now = datetime.now()

    db_user = HippoUser(
        id=user_id,
        username=user.username,
        password=get_password_hash(user.password),  # hash
        email=user.email,
        role=None,  # adjust if your model field is named differently
        firstname=user.firstname,
        lastname=user.lastname,
        created=user.created or now,
        last_modified=user.last_modified or now,
        remap=user.remap,
        i2ce_hidden=user.i2ce_hidden,
    )

    db_access_facility = HippoAccessFacility(
        id=access_id,
        parent=user_id,              # if your column is named differently (e.g., parent_id), change here
        location=user.facility_id,
        created=now,
        last_modified=now,
    )

    try:
        session.add(db_user)
        session.add(db_access_facility)
        await session.commit()
    except Exception:
        await session.rollback()
        raise

    # refresh and return
    await session.refresh(db_user)
    return db_user



@apiRouter.put(
    "/users/{user_id}", 
    response_model=HippoUserRead, 
    dependencies=[Depends(get_current_active_user)]
)
async def update_user(
    user_id: str,
    user: HippoUserUpdate,
    session: AsyncSession = Depends(get_session),
):
    # Find existing user
    result = await session.execute(select(HippoUser).where(HippoUser.id == user_id))
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if username is changing and is unique
    if user.username != db_user.username:
        existing = await session.execute(
            select(HippoUser).where(HippoUser.username == user.username)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists.",
            )

    now = datetime.now()

    # Update user fields
    db_user.username = user.username
    if user.password:
        db_user.password = get_password_hash(user.password)  # hash new password if provided
    db_user.email = user.email
    db_user.firstname = user.firstname
    db_user.lastname = user.lastname
    db_user.last_modified = now
    if user.remap is not None:
        db_user.remap = user.remap
    if user.i2ce_hidden is not None:
        db_user.i2ce_hidden = user.i2ce_hidden

    # Update or create access facility
    access_result = await session.execute(
        select(HippoAccessFacility).where(HippoAccessFacility.parent == user_id)
    )
    db_access = access_result.scalar_one_or_none()
    if db_access:
        db_access.location = user.facility_id
        db_access.last_modified = now
    else:
        db_access = HippoAccessFacility(
            id= f"access|{user.username}",
            parent=user_id,
            location=user.facility_id,
            created=now,
            last_modified=now,
        )
        session.add(db_access)

    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise

    await session.refresh(db_user)
    return db_user
