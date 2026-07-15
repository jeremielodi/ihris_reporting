from pydantic import BaseModel, ConfigDict
from typing import Dict, List, Optional
from uuid import UUID

class NormRequirementBase(BaseModel):
    organization_unit_type_id: str
    classification_id: str
    required: int

class NormRequirementCreate(NormRequirementBase):
    pass

class NormRequirementUpdate(BaseModel):
    required: int
    organization_unit_type_id: str
    classification_id: str

class NormRequirementRead(NormRequirementBase):
    id: UUID
    classification_name: Optional[str]
    organization_unit_type_name: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class FacilityResult(BaseModel):
    org_unit_id: str
    organization_unit_type_id: str
    required: Dict[str, int] | None
    actual: Optional[Dict[str, int]] = None
    missing: Dict[str, int]
    excess: Dict[str, int]
    compliance_ratio: float

class NodeRollup(BaseModel):
    org_unit_id: str
    level: str
    required_total: int
    actual_total: int
    missing_total: int
    compliance_ratio: float