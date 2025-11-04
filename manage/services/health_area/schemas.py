from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class HippoHealthAreaBase(BaseModel):
    id: Optional[str] = None  # Use Optional for id, as it may not be set on creation
    name: Optional[str] = None
    code: Optional[str] = None
    last_modified: Optional[datetime] = datetime(1900, 1, 1, 0, 0, 0)
    created: Optional[datetime] = datetime.now()
    remap: Optional[str] = None
    i2ce_hidden: Optional[int] = 0
    county:Optional[str] = None
  

class HippoHealthAreaCreate(HippoHealthAreaBase):
    id: Optional[str] = None
    created: Optional[datetime] = datetime.now()
    last_modified: Optional[datetime] = datetime.now()  # Default to now if not provided
    name:str


class HippoHealthAreaUpdate(HippoHealthAreaBase):
    last_modified: Optional[datetime] = datetime.now()  # Default to now if not provided


class HippoHealthAreaRead(HippoHealthAreaBase):
    id: str
    county:Optional[str] = '|'
    code: Optional[str] = None
    county_name : Optional[str] = None

    class Config:
        orm_mode = True
