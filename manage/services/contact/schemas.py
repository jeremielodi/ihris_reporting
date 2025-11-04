from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID

class HippoContactBase(BaseModel):
    id: Optional[UUID] = None  # Use Optional for id, as it may not be set on creation
    mobile_phone: Optional[str] = None
    address: Optional[str] = None
    person_id: Optional[str] = None
    contact_type: Optional[str] = None
    telephone: Optional[str] = None
    alt_telephone: Optional[str] = None
    email: Optional[str] = None
    fax: Optional[str] = None
    notes: Optional[str] = None
    last_modified: Optional[datetime] = datetime(1900, 1, 1, 0, 0, 0)
    created: Optional[datetime] = datetime.now()
    i2ce_hidden: Optional[int] = None
  

class HippoContactCreate(HippoContactBase):
    id: Optional[UUID] = None
    created: Optional[datetime] = datetime.now()
    last_modified: Optional[datetime] = datetime.now()  # Default to now if not provided
    person_id: str
    contact_type: str
    
class HippoContactUpdate(HippoContactBase):
    last_modified: Optional[datetime] = datetime.now()  # Default to now if not provided


class HippoContactRead(HippoContactBase):
    id: UUID
    

    class Config:
        orm_mode = True
