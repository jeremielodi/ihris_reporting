from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID

class HippoAuditLogBase(BaseModel):
    id: Optional[UUID] = None  # Use Optional for id, as it may not be set on creation
    user_id: Optional[str] = None
    operation: Optional[str] = None
    created: Optional[datetime] = datetime.now()

class HippoAuditLogCreate(HippoAuditLogBase):
    id: Optional[str] = None
    created: Optional[datetime] = datetime.now()
    operation:str


class HippoAuditLogUpdate(HippoAuditLogBase):
    created: Optional[datetime] = datetime.now()

class HippoAuditLogRead(HippoAuditLogBase):
    id: str
    translate_key: str | None
    

    class Config:
        orm_mode = True
