from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import date, datetime

class Dashboard(BaseModel):
    uuid: Optional[UUID] = None
    mb_dashboard_id: int
    created : Optional[datetime] = None
    created_by: Optional[str] = None
    last_modified: Optional[datetime]  = Field(default_factory=datetime.utcnow)
    created: Optional[datetime] = Field(default_factory=datetime.utcnow)
    label: str

    model_config = ConfigDict(from_attributes=True)


class RoleDashboard(BaseModel):
    uuid: Optional[str] = None
    role_id: str
    dashboard_uuid: str

    model_config = ConfigDict(from_attributes=True)


class RoleDashboardAssign(BaseModel):
    role_id: str
    dashboard_uuids: list[str] = None

