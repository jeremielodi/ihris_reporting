from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class OrganizationUnitTypeBase(BaseModel):
    name: str
    position: Optional[int] = 0

class OrganizationUnitTypeCreate(OrganizationUnitTypeBase):
    pass

class OrganizationUnitTypeUpdate(BaseModel):
    name: Optional[str] = None
    position: Optional[int] = None

class OrganizationUnitTypeRead(OrganizationUnitTypeBase):
    id: str
    created: Optional[datetime] = None
    
    class Config:
        orm_mode = True