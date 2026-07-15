from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class DocumentTypeBase(BaseModel):
    id: Optional[str] = None  # Use Optional for id, as it may not be set on creation
    name: str
    created: Optional[datetime] = datetime.now()
    i2ce_hidden: Optional[int] = None
    created_by: Optional[str] = None
    last_modified_by: Optional[str] = None
    

class DocumentTypeCreate(DocumentTypeBase):
    id: Optional[str] = None
    created: Optional[datetime] = datetime.now()
    last_modified: Optional[datetime] = datetime.now()  # Default to now if not provided


class DocumentTypeUpdate(DocumentTypeBase):
    last_modified: Optional[datetime] = datetime.now()  # Default to now if not provided


class DocumentTypeRead(DocumentTypeBase):
    id: str
    

    model_config = ConfigDict(from_attributes=True)
