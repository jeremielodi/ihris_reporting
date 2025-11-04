from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime, date

class HippoPersonIdentificationBase(BaseModel):
    id: Optional[str] = None  # Use Optional for id, as it may not be set on creation
    parent: Optional[str] = '|'
    last_modified: Optional[datetime] = datetime(1900, 1, 1, 0, 0, 0)
    created: Optional[datetime] = datetime.now()
    remap: Optional[str] = None
    i2ce_hidden: Optional[int] = 0
    number : Optional[str] = None
    expiration_date: Optional[date] = None
    acquisition_date: Optional[date] = None
    type_id : Optional[str] = None
    person_id : Optional[str] = None
    country : Optional[str] = None

class HippoPersonIdentificationCreate(HippoPersonIdentificationBase):
    id: Optional[str] = None
    number : str

    @validator("acquisition_date", pre=True)
    def parse_acquisition_date(cls, v):
        print(v)
        # Accept "1992-03-13", "1992-03-13T00:00:00", or "...Z"
        if isinstance(v, str):
            print(v)
            v = v.replace("Z", "+00:00")
            # keep only the date portion if a datetime string is provided
            return date.fromisoformat(v.split("T")[0])
        return v

    @validator("expiration_date", pre=True)
    def parse_expiration_date(cls, v):
        print(v)
        # Accept "1992-03-13", "1992-03-13T00:00:00", or "...Z"
        if isinstance(v, str):
            print(v)
            v = v.replace("Z", "+00:00")
            # keep only the date portion if a datetime string is provided
            return date.fromisoformat(v.split("T")[0])
        return v


class HippoPersonIdentificationUpdate(HippoPersonIdentificationCreate):
    last_modified: Optional[datetime] = datetime.now()  # Default to now if not provided


class HippoPersonIdentificationRead(HippoPersonIdentificationBase):
    id: str
    type_name: Optional[str]=None
    country_name: Optional[str]=None

    class Config:
        orm_mode = True
