from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
import uuid as uuid_lib
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Pydantic Models
class DashboardQueryBase(BaseModel):
    dashboard_uuid: uuid_lib.UUID
    query: str = Field(..., max_length=255)
    parameters: Optional[Dict[str, Any]] = Field(default={})
    row_index: int = Field(default=0, ge=0)
    col_index: int = Field(default=0, ge=0)
    created_by: Optional[str] = Field(None, max_length=255)
    last_modified_by: Optional[str] = Field(None, max_length=255)

class DashboardQueryCreate(DashboardQueryBase):
    pass

class DashboardQueryUpdate(BaseModel):
    dashboard_uuid: Optional[uuid_lib.UUID] = None
    query: Optional[str] = Field(None, max_length=255)
    parameters: Optional[Dict[str, Any]] = None
    row_index: Optional[int] = Field(None, ge=0)
    col_index: Optional[int] = Field(None, ge=0)
    last_modified_by: Optional[str] = Field(None, max_length=255)

class DashboardQueryRead(DashboardQueryBase):
    uuid: uuid_lib.UUID
    created: datetime
    last_modified: datetime
    
    class Config:
        orm_mode = True
        from_attributes = True

    

class DashboardQueryRun(BaseModel):
    sql: str
    parameters: Optional[Dict[str, Any]] = Field(default={})