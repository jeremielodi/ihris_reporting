from sqlalchemy.orm import Session
from models.models import AccessFacility, County, Country, District, Facility, HealthArea, User
from manage.models import HippoUser, ViewOrgUnitList,HippoAuditLog, HippoRefreshToken
import hashlib
import secrets
from datetime import datetime, timedelta
from endpoints.pyramid_api import county, facilities
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import  HTTPException
from passlib.context import CryptContext
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
import uuid
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


async def _login(db: Session, username: str, password: str) -> User | None:
    result = await db.execute(select(HippoUser).where(HippoUser.username == username))
    user = result.scalar_one_or_none()
    if not user:
        return None
    
    auditLog = HippoAuditLog(id= uuid.uuid4(), user_id=user.id, operation=f'connextion {user.id} {user.email}')
    db.add(auditLog)
    await db.commit()
    return user

async def findByUsername(username: str, db: Session, ) -> User | None:
    result = await db.execute(select(HippoUser).where(HippoUser.username == username))
    user = result.scalar_one_or_none()
    if not user:
        return None
    return user


async def findById(user_id: str, db: Session) -> User | None:
    result = await db.execute(select(HippoUser).where(HippoUser.id == user_id))
    return result.scalar_one_or_none()

async def _get_access_facility(db: Session, userid: str) -> Dict[str, Any]:
    # find the user's AccessFacility row
    accessResult = await db.execute(
        select(AccessFacility).where(AccessFacility.parent == userid)
    )
    access = accessResult.scalar_one_or_none()
  
    access_facility_type: str = ""
    af: Optional[Any] = None
    target: int = 0

    if access and access.location:
        loc = access.location  # e.g. "facility|...", "health_area|...", etc.
        facilityaResult = await db.execute(
                    select(ViewOrgUnitList).where(ViewOrgUnitList.id == loc)
                )
        af = facilityaResult.scalar_one_or_none()
        access_facility_type = af.type if af else None
        target = 0

    return {
        "access_facility_row": access,          # the AccessFacility row itself
        "access_facility": af,                  # the resolved entity (Facility/HealthArea/County/...)
        "access_facility_type": access_facility_type,  # next child type allowed
        "access_facility_target": target,       # your numeric level flag (0..4)
    }


def _hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


async def create_refresh_token(db: Session, user_id: str, expire_days: int) -> str:
    """
    Generates an opaque refresh token, stores only its hash, and returns
    the plaintext value to send to the client (never persisted as-is).
    """
    token = secrets.token_urlsafe(48)
    row = HippoRefreshToken(
        id=uuid.uuid4(),
        user_id=user_id,
        token_hash=_hash_refresh_token(token),
        expires=datetime.utcnow() + timedelta(days=expire_days),
        revoked=False,
    )
    db.add(row)
    await db.commit()
    return token


async def get_valid_refresh_token(db: Session, token: str) -> HippoRefreshToken | None:
    result = await db.execute(
        select(HippoRefreshToken).where(HippoRefreshToken.token_hash == _hash_refresh_token(token))
    )
    row = result.scalar_one_or_none()
    if not row or row.revoked or row.expires < datetime.utcnow():
        return None
    return row


async def revoke_refresh_token(db: Session, row: HippoRefreshToken) -> None:
    row.revoked = True
    await db.commit()


