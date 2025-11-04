from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class HippoUserBase(BaseModel):
    id: Optional[str] = None  # Use Optional for id, as it may not be set on creation
    last_modified: Optional[datetime] =  datetime.now()
    created: Optional[datetime] = datetime.now()
    remap: Optional[str] = None
    i2ce_hidden: Optional[int] =  Field(0)
    username: str = Field(None, min_length=5, max_length=50)
    password: str = Field(None, min_length=5, max_length=150, exclude=True)
    firstname: Optional[str] = Field(None, min_length=3, max_length=50)
    lastname: str = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr]

class HippoUserCreate(HippoUserBase):
    username: str = Field(None, min_length=5, max_length=50)
    password: str = Field(None, min_length=5, max_length=150, exclude=True)
    firstname: Optional[str] = Field(None, min_length=3, max_length=50)
    lastname: str = Field(None, min_length=3, max_length=50)
    email: EmailStr
    facility_id:str

class HippoUserUpdate(HippoUserCreate):
    id:str

class HippoUserRead(HippoUserBase):
    id: str  # Usually, primary key id is required on create
    email: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    username: Optional[str] = None
    access_facility_id : Optional[str] = None  #
    access_facility_name : Optional[str] = None  #
    class Config:
        orm_mode = True


class HippoUserChangePassword(BaseModel):
    confirm_password: str
    new_password:  str
    old_password:  str
    user_id:  str
    