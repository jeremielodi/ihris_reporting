from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class HippoSpecialityBase(BaseModel):
    id: Optional[str] = None  # Use Optional for id, as it may not be set on creation
    parent: Optional[str] = '|'
    last_modified: Optional[datetime] = datetime(1900, 1, 1, 0, 0, 0)
    created: Optional[datetime] = datetime.now()
    name: Optional[str] = None
    code: Optional[str] = None

class HippoSpecialityCreate(HippoSpecialityBase):
    id: Optional[str] = None
    created: Optional[datetime] = datetime.now()
    last_modified: Optional[datetime] = datetime.now()  # Default to now if not provided

class HippoSpecialityUpdate(HippoSpecialityBase):
    last_modified: Optional[datetime] = datetime.now()  # Default to now if not provided

class HippoSpecialityRead(HippoSpecialityBase):
    id: str
    
    model_config = ConfigDict(from_attributes=True)