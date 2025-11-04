from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class HippoSettingBase(BaseModel):
    id: Optional[str] = None  # Use Optional for id, as it may not be set on creation
    app_name:  Optional[str] = None
    app_version: Optional[str] = None
    responsible_name: Optional[str] = ''
    responsible_number: Optional[str] = ''
    logo: Optional[str] = None
    last_modified:  Optional[datetime] = datetime.now()
    created: Optional[datetime] = datetime.now()

class HippoSettingCreate(HippoSettingBase):
    id: Optional[str] = None
    created: Optional[datetime] = datetime.now()
    last_modified: Optional[datetime] = datetime.now()  # Default to now if not provided
    app_name:str
    app_version:str


class HippoSettingUpdate(HippoSettingBase):
    last_modified: Optional[datetime] = datetime.now()  # Default to now if not provided


class HippoSettingRead(HippoSettingBase):
    id: str
    app_name: str
    app_version:str

    class Config:
        orm_mode = True
