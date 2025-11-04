from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class HippoCountyBase(BaseModel):
    id: Optional[str] = None  # Use Optional for id, as it may not be set on creation
    name: Optional[str] = None
    code: Optional[str] = None
    last_modified: Optional[datetime] = datetime(1900, 1, 1, 0, 0, 0)
    created: Optional[datetime] = datetime.now()
    remap: Optional[str] = None
    i2ce_hidden: Optional[int] = 0
    district:Optional[str] = '|'
  

class HippoCountyCreate(HippoCountyBase):
    id: Optional[str] = None
    created: Optional[datetime] = datetime.now()
    last_modified: Optional[datetime] = datetime.now()  # Default to now if not provided
    name:str


class HippoCountyUpdate(HippoCountyBase):
    last_modified: Optional[datetime] = datetime.now()  # Default to now if not provided


class HippoCountyRead(HippoCountyBase):
    id: str
    district:Optional[str] = '|'
    code: Optional[str] = None

    class Config:
        orm_mode = True
