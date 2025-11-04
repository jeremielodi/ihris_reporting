from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class HippoEmployeeStatusBase(BaseModel):
    id: Optional[str] = None  # Use Optional for id, as it may not be set on creation
    code: Optional[str] = None
    name: Optional[str] = None
    translate_key: Optional[str] = None
    parent: Optional[str] = '|'
    last_modified: Optional[datetime] = datetime(1900, 1, 1, 0, 0, 0)
    created: Optional[datetime] = datetime.now()
    remap: Optional[str] = None
    i2ce_hidden: Optional[int] = 0
  

class HippoEmployeeStatusCreate(HippoEmployeeStatusBase):
    id: Optional[str] = None
    created: Optional[datetime] = datetime.now()
    last_modified: Optional[datetime] = datetime.now()  # Default to now if not provided
    name:str


class HippoEmployeeStatusUpdate(HippoEmployeeStatusBase):
    last_modified: Optional[datetime] = datetime.now()  # Default to now if not provided


class HippoEmployeeStatusRead(HippoEmployeeStatusBase):
    id: str
    

    class Config:
        orm_mode = True
