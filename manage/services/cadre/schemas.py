from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class HippoCadreBase(BaseModel):
    id: Optional[str] = None  # Use Optional for id, as it may not be set on creation
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    code: Optional[str] = None
    translate_key: Optional[str] = None
    parent: Optional[str] = '|'
    last_modified: Optional[datetime] = datetime(1900, 1, 1, 0, 0, 0)
    created: Optional[datetime] = datetime.now()
    remap: Optional[str] = None
    i2ce_hidden: Optional[int] = 0

class HippoCadreCreate(HippoCadreBase):
    id: Optional[str] = None
    created: Optional[datetime] = datetime.now()
    last_modified: Optional[datetime] = datetime.now()  # Default to now if not provided
    name:str


class HippoCadreUpdate(HippoCadreBase):
    last_modified: Optional[datetime] = datetime.now()  # Default to now if not provided


class HippoCadreRead(HippoCadreBase):
    id: str
    translate_key: str | None
    

    class Config:
        orm_mode = True
