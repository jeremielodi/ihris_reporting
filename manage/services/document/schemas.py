from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date, datetime

class DocumentBase(BaseModel):
    id: Optional[str] = None
    path:  Optional[str] = None
    description: str
    type_id: Optional[str] = None
    person_id: Optional[str] = None
    created_by:  Optional[str] = None
    i2ce_hidden: Optional[str] = None
    created: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    last_modified_by: Optional[str] = None


class DocumentCreate(DocumentBase):
    # Required fields override optionals from base:
    person_id: str

class DocumentRead(DocumentBase):
    id: str
    document_type_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
