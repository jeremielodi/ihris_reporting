from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

class HippoPassportBase(BaseModel):
    id: Optional[str] = None
    path:  Optional[str] = None
    person_id: Optional[str] = None
    created_by:  Optional[str] = None
    i2ce_hidden: Optional[str] = None
    created: datetime = Field(default_factory=datetime.utcnow)


class HippoPassportCreate(HippoPassportBase):
    # Required fields override optionals from base:
    person_id: str

class HippoPassportRead(HippoPassportBase):
    id: str

    class Config:
        orm_mode = True
