from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class OrganizationUnitLevel(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    level: Optional[int] = None


class OrganizationUnitLevelCreate(BaseModel):
    # id optional: if not provided, API will generate it
    id: Optional[str] = None
    name: str
    level: int


class OrganizationUnitLevelUpdate(BaseModel):
    # partial update
    name: Optional[str] = None
    level: Optional[int] = None


class OrganizationUnitLevelRead(OrganizationUnitLevel):
    id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)