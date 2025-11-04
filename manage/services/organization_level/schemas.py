from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class OrganizationUnitLevel(BaseModel):
    id: Optional[str] = None  # Use Optional for id, as it may not be set on creation
    name: Optional[str] = None
    level : Optional[int] = None


class OrganizationUnitLevelRead(OrganizationUnitLevel):
    id: Optional[str] = None
    
    class Config:
        orm_mode = True