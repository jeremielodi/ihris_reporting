from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from typing import List


class HippoRoleActionCreate(BaseModel):
    role_id: str
    action_ids:list

class HippoRoleBase(BaseModel):
    id: Optional[str] = None  # Use Optional for id, as it may not be set on creation
    parent: Optional[str] = '|'
    last_modified: Optional[datetime] = datetime(1900, 1, 1, 0, 0, 0)
    created: Optional[datetime] = datetime.now()
    created_by: Optional[str] = None
    remap: Optional[str] = None
    i2ce_hidden: Optional[int] = None
    name: Optional[str] = None

class HippoRoleCreate(HippoRoleBase):
    id: Optional[str]  # Usually, primary key id is required on create
    created: Optional[datetime] = datetime.now()
    last_modified: Optional[datetime] = datetime.now()  # Default to now if not provided


class HippoRoleUpdate(HippoRoleBase):
    last_modified: Optional[datetime] = datetime.now()  # Default to now if not provided


class HippoRoleRead(HippoRoleBase):
    id: str
    

    class Config:
        orm_mode = True


class AssignRolesPayload(BaseModel):
    user_id: str
    role_ids: List[str] = Field(default_factory=list)  # keep same name you used