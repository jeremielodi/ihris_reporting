from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class HippoDegreeBase(BaseModel):
    id: Optional[str] = None  # Use Optional for id, as it may not be set on creation
    parent: Optional[str] = '|'
    last_modified: Optional[datetime] = datetime(1900, 1, 1, 0, 0, 0)
    created: Optional[datetime] = datetime.now()
    remap: Optional[str] = None
    i2ce_hidden: Optional[int] = None
    name: Optional[str] = None
    code: Optional[str] = None

class HippoDegreeCreate(HippoDegreeBase):
    id: Optional[str] = None
    created: Optional[datetime] = datetime.now()
    last_modified: Optional[datetime] = datetime.now()  # Default to now if not provided


class HippoDegreeUpdate(HippoDegreeBase):
    last_modified: Optional[datetime] = datetime.now()  # Default to now if not provided


class HippoDegreeRead(HippoDegreeBase):
    id: str
    

    class Config:
        orm_mode = True
