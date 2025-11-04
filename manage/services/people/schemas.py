from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date, datetime

class HippoPersonBase(BaseModel):
    id: Optional[str] = None
    firstname: Optional[str] = None
    middlename: Optional[str] = None
    lastname: Optional[str] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    birthplace: Optional[str] = None
    birthdate: Optional[date] = None
    recruitment_date: Optional[date] = None
    email: Optional[str] = None      
    marital_status: Optional[str] = None
    nationality: Optional[str] = None
    residence: Optional[str] = None
    degree: Optional[str] = None
    last_modified: datetime = Field(default_factory=datetime.utcnow)
    created: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    i2ce_hidden: int = 0
    dependents:  Optional[int] = 0

class HippoPersonCreate(HippoPersonBase):
    # Required fields override optionals from base:
    lastname: str
    gender: str
    birthplace:str
    birthdate: date                                  # <-- date, required
    marital_status: str

    @validator("birthdate", pre=True)
    def parse_birthdate(cls, v):
        # Accept "1992-03-13", "1992-03-13T00:00:00", or "...Z"
        if isinstance(v, str):
            print('istring')
            v = v.replace("Z", "+00:00")
            # keep only the date portion if a datetime string is provided
            return date.fromisoformat(v.split("T")[0])
        return v

    @validator("recruitment_date", pre=True)
    def parse_recruitment_date(cls, v):
        # Accept "1992-03-13", "1992-03-13T00:00:00", or "...Z"
        if isinstance(v, str):
            v = v.replace("Z", "+00:00")
            # keep only the date portion if a datetime string is provided
            return date.fromisoformat(v.split("T")[0])
        return v

class HippoPersonUpdate(HippoPersonCreate):
    last_modified: Optional[datetime] = datetime.now()


class HippoPersonRead(HippoPersonBase):
    id: str
    marital_status_id:Optional[str] = None
    nationality_id:Optional[str] = None
    gender_id:Optional[str] = None
    degree_id:Optional[str] = None
    dependents:Optional[int] = None

    class Config:
        orm_mode = True


class PeopelQueryParameters(HippoPersonBase):
    id: Optional[str] 
    name: Optional[str] 
    matricule: Optional[str]