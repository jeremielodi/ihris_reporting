from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class HippoClassificationBase(BaseModel):
    id: Optional[str] = None  # Use Optional for id, as it may not be set on creation
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    parent: Optional[str] = '|'
    last_modified: Optional[datetime] = datetime(1900, 1, 1, 0, 0, 0)
    created: Optional[datetime] = datetime.now()
    remap: Optional[str] = None
    i2ce_hidden: Optional[int] = None
  

class HippoClassificationCreate(HippoClassificationBase):
    id: Optional[str] = None
    created: Optional[datetime] = datetime.now()
    last_modified: Optional[datetime] = datetime.now()  # Default to now if not provided
    name:str
    code: Optional[str] = None
    description: Optional[str] = None


class HippoClassificationUpdate(HippoClassificationBase):
    last_modified: Optional[datetime] = datetime.now()  # Default to now if not provided


class HippoClassificationRead(HippoClassificationBase):
    id: str
    

    class Config:
        orm_mode = True
