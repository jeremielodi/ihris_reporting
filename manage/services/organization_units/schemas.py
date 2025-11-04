from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class ViewOrgUnitListBase(BaseModel):
    id: Optional[str] = None  # Use Optional for id, as it may not be set on creation
    parent: Optional[str] = None
    name: Optional[str] = None
    code: Optional[str] = None
    type : Optional[str] = None
    level : Optional[str] = None


class OrgUnitCreate(ViewOrgUnitListBase):
    created: Optional[datetime] = datetime.now()
    last_modified: Optional[datetime] = datetime.now()  # Default to now if not provided
    name:str

class OrgUnitUpdate(ViewOrgUnitListBase):
    last_modified: Optional[datetime] = datetime.now()  # Default to now if not provided
    name:str
    id:str


class ViewOrgUnitListRead(ViewOrgUnitListBase):
    id: Optional[str] = None
    

    class Config:
        orm_mode = True
