from pydantic import BaseModel, EmailStr,validator
from typing import Optional
from datetime import date, datetime

class HippoTimesheetBase(BaseModel):
    id: Optional[str] = None  # Use Optional for id, as it may not be set on creation
    person_id: str
    created: Optional[datetime] = datetime.now()
    created_by: Optional[str] = None
    last_modified: Optional[datetime] = datetime(1900, 1, 1, 0, 0, 0)
    last_modified_by: Optional[str] = None
    days_absence_justified: Optional[int] = 0
    days_absence_unjustified: Optional[int] = 0
    days_leave: Optional[int] = 0
    days_holiday: Optional[int] = 0
    days_sick: Optional[int] = 0
    days_mission: Optional[int] = 0
    days_worked: Optional[int] = 0
    days_planned: Optional[int] = 0
    month_year:date
    bonus_local: Optional[int] = 0
    bonus_pepfar: Optional[int] = 0
    bonus_partner: Optional[int] = 0
    bonus_risk: Optional[int] = 0
    project: Optional[str] = None
    salary_received: Optional[int] = 0
    i2ce_hidden: Optional[int] = None

class HippoTimesheetCreate(HippoTimesheetBase):
    id: Optional[str] = None  # Usually, primary key id is required on create
    created: Optional[datetime] = datetime.now()
    last_modified: Optional[datetime] = datetime.now()  # Default to now if not provided

    @validator("month_year", pre=True)
    def parse_month_year(cls, v):
        if isinstance(v, str):
            # accept "YYYY-MM" or "YYYY-MM-DD"
            try:
                return date.fromisoformat(v if len(v) == 10 else f"{v}-01")
            except ValueError:
                # fallback: try datetime
                return datetime.fromisoformat(v).date()
        return v

class HippoTimesheetUpdate(HippoTimesheetCreate):
    last_modified: Optional[datetime] = datetime.now()  # Default to now if not provided


class HippoTimesheetRead(HippoTimesheetBase):
    id: str
    

    class Config:
        orm_mode = True
