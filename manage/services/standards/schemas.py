from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID

class OrganizationUnitStandardsBase(BaseModel):
    classification_id: Optional[str] = None
    org_unit_type_id: Optional[str] = None
    number_of_positions: Optional[int] = None
    created_by: Optional[str] = None
    last_modified_by: Optional[str] = None
    i2ce_hidden: Optional[int] = 0

class OrganizationUnitStandardsCreate(OrganizationUnitStandardsBase):
    pass

class OrganizationUnitStandardsUpdate(OrganizationUnitStandardsBase):
    pass

class OrganizationUnitStandardsRead(OrganizationUnitStandardsBase):
    uuid: Optional[UUID] = None
    created: Optional[datetime] = None
    last_modified: Optional[datetime]  
    org_unit_type_name : Optional[str]  
    classification_name : Optional[str] 

    class Config:
         orm_mode = True