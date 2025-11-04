from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date, datetime


class HippoEmploymentStatusInfoBase(BaseModel):
    id :  Optional[str] = None
    person_id: Optional[str] = None
    grade : Optional[str] = None
    cadre : Optional[str] = None
    classification : Optional[str] = None
    employment_date : Optional[date]= None
    start_service_date: Optional[date]= None
    facility_id : Optional[str] = None
    position_decision_ref: Optional[str] = None
    ref_engagement : Optional[str] = None
    salary_source : Optional[str] = None
    salary : Optional[int] = 0
    job_type : Optional[str] = None
    allowance : Optional[int] = 0
    created_by : Optional[str] = None
    employee_status : Optional[str] = None
    last_modified_by : Optional[str] = None
    last_modified :  Optional[datetime]= None
    i2ce_hidden : Optional[int] = 0
    seniority: Optional[int] = 0
    created : Optional[date]= None
    

class HippoEmploymentStatusInfoCreate(HippoEmploymentStatusInfoBase):
    # Required fields override optionals from base:
    classification: str
    person_id: str
    grade: str
    facility_id:str
    employment_date: date                                  # <-- date, required
    created: Optional[datetime] = datetime.now()
    last_modified: Optional[datetime] = datetime.now()

    @validator("employment_date", pre=True)
    def parse_birthdate(cls, v):
        print(v)
        # Accept "1992-03-13", "1992-03-13T00:00:00", or "...Z"
        if isinstance(v, str):
            v = v.replace("Z", "+00:00")
            # keep only the date portion if a datetime string is provided
            return date.fromisoformat(v.split("T")[0])
        return v
    
    @validator("start_service_date", pre=True)
    def parse_start_service_date(cls, v):
        # Accept "1992-03-13", "1992-03-13T00:00:00", or "...Z"
        if isinstance(v, str):
            v = v.replace("Z", "+00:00")
            # keep only the date portion if a datetime string is provided
            return date.fromisoformat(v.split("T")[0])
        return v
    

class HippoEmploymentStatusInfoUpdate(HippoEmploymentStatusInfoCreate):
     id:str
     last_modified: Optional[datetime] = datetime.now()


class HippoEmploymentStatusInfoRead(HippoEmploymentStatusInfoBase):
    id: Optional[str]=None
    cadre_name: Optional[str]=None
    classification_name: Optional[str]=None
    grade_name: Optional[str]=None
    employee_status_name : Optional[str]=None
    salary_source_name : Optional[str]=None
    job_type_name : Optional[str]=None

    class Config:
        orm_mode = True
