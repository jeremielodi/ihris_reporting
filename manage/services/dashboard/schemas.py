from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import date, datetime

class Dashboard(BaseModel):
    uuid: Optional[UUID] = None
    mb_dashboard_id: int
    created : Optional[datetime]
    created_by: Optional[str]
    last_modified: Optional[datetime]  = Field(default_factory=datetime.utcnow)
    created: Optional[datetime] = Field(default_factory=datetime.utcnow)
    label: str

    class Config:
        orm_mode = True


class RoleDashboard(BaseModel):
    uuid: Optional[str] = None
    role_id: str
    dashboard_uuid: str

    class Config:
        orm_mode = True


class RoleDashboardAssign(BaseModel):
    role_id: str
    dashboard_uuids: list[str] = None

