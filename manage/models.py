from sqlalchemy import Column, String, Integer, Date, DateTime,Numeric, Text, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)

class HippoEntityMap(Base):
    __tablename__ = "hippo_entity_map"
    id = Column(String(255), primary_key=True)
    entity_type = Column(String(50), nullable=False, index=True)
    max_number = Column(Integer, nullable=False)


class HippoAccessFacility(Base):
    __tablename__ = "hippo_access_facility"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    location = Column(String(255), nullable=True)


class HippoApplication(Base):
    __tablename__ = "hippo_application"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    desired_wage = Column(String(255), nullable=True)
    felony = Column(Integer, nullable=True)
    felony_circumstance = Column(String(255), nullable=True)
    full_time = Column(Integer, nullable=True)
    hear = Column(String(255), nullable=True)
    hours = Column(String(255), nullable=True)
    other_info = Column(String(255), nullable=True)
    position = Column(String(255), nullable=True)
    start_date = Column(DateTime, nullable=True)



class HippoCadre(Base):
    __tablename__ = "hippo_cadre"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)
    code = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    translate_key = Column(String(255), nullable=True)


class HippoClassification(Base):
    __tablename__ = "hippo_classification"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    code = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)


class HippoSalarySource(Base):
    __tablename__ = "hippo_salary_source"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    code = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)



class HippoSalaryGrade(Base):
    __tablename__ = "hippo_salary_grade"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    notes = Column(String(255), nullable=True)
    midpoint = Column(String(255), nullable=True)
    start = Column(String(255), nullable=True)
    end = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)





class HippoContactType(Base):
    __tablename__ = "hippo_contact_type"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)
    code = Column(String(255), nullable=True)

class HippoContact(Base):
    __tablename__ = "hippo_contact"
    id = Column(UUID(as_uuid=True), primary_key=True)
    person_id = Column(String(255), index=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    created_by = Column(String(255), index=True)
    last_modified_by = Column(String(255), index=True)
    i2ce_hidden = Column(Integer, nullable=True)
    address = Column(String(255), nullable=True)
    alt_telephone = Column(String(255), nullable=True)
    contact_group = Column(String(255), nullable=True)
    contact_type = Column(String(255), nullable=True, index=True)
    email = Column(String(255), nullable=True)
    fax = Column(String(255), nullable=True)
    mobile_phone = Column(String(255), nullable=True)
    notes = Column(String(255), nullable=True)
    telephone = Column(String(255), nullable=True)


class HippoContactGroup(Base):
    __tablename__ = "hippo_contact_group"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)



class HippoCountry(Base):
    __tablename__ = "hippo_country"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    alpha_two = Column(String(255), nullable=True)
    code = Column(Integer, nullable=True)
    csd_uuid = Column(String(255), nullable=True)
    location = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)
    primary = Column(Integer, nullable=True)


class HippoCounty(Base):
    __tablename__ = "hippo_county"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    csd_uuid = Column(String(255), nullable=True)
    district = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    code = Column(String(255), nullable=True)


class HippoCurrency(Base):
    __tablename__ = "hippo_currency"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    code = Column(String(255), nullable=True)
    country = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    symbol = Column(String(255), nullable=True)


class HippoDegree(Base):
    __tablename__ = "hippo_degree"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)
    code = Column(String(255), nullable=True)

class HippoEducationalMajor(Base):
    __tablename__ = "hippo_educational_major"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=False)
    code = Column(String(255), nullable=True)

class HippoEducationalLevel(Base):
    __tablename__ = "hippo_educational_level"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=False)
    code = Column(String(255), nullable=True)


class HippoInstitutionType(Base):
    __tablename__ = "hippo_institution_type"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=False)
    code = Column(String(255), nullable=True)



class HippoDepartment(Base):
    __tablename__ = "hippo_department"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)


class HippoDistrict(Base):
    __tablename__ = "hippo_district"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    code = Column(String(255), nullable=True)
    csd_uuid = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    region = Column(String(255), nullable=True)

class HippoFacilityType(Base):
    __tablename__ = "hippo_facility_type"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    code = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)

class HippoFacility(Base):
    __tablename__ = "hippo_facility"

    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    location = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    code = Column(String(255), nullable=True)
    csd_uuid = Column(String(255), nullable=True)
    facility_type = Column(String(255), nullable=True)
    latitude = Column(String(255), nullable=True)
    longitude = Column(String(255), nullable=True)


class HippoRegion(Base):
    __tablename__ = "hippo_region"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    code = Column(String(255), nullable=True)
    country = Column(String(255), nullable=True)
    csd_uuid = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)

class HippoHealthArea(Base):
    __tablename__ = "hippo_health_area"

    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    code = Column(String(255), nullable=True)
    county = Column(String(255), nullable=True, index=True)
    name = Column(String(255), nullable=True)
    population = Column(String(255), nullable=True)


class HippoEducation(Base):
    __tablename__ = "hippo_education"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    degree = Column(String(255), nullable=True)
    institution = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    major = Column(String(255), nullable=True)
    start_date = Column(DateTime, nullable=True)
    type = Column(String(255), nullable=True)
    year = Column(Integer, nullable=True)


class HippoEmployer(Base):
    __tablename__ = "hippo_employer"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)


class HippoEmploymentStatus(Base):
    __tablename__ = "hippo_employment_status"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=False)
    code = Column(String(255), nullable=True)

class HippoPaymentFrequency(Base):
    __tablename__ = "hippo_payment_frequency"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=False)
    code = Column(String(255), nullable=True)


class HippoReasonDeparture(Base):
    __tablename__ = "hippo_reason_departure"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=False)
    code = Column(String(255), nullable=True)


class HippoGender(Base):
    __tablename__ = "hippo_gender"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)


class HippoHoliday(Base):
    __tablename__ = "hippo_holiday"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    description = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)
    type = Column(String(255), nullable=True)


class HippoHoursOfWork(Base):
    __tablename__ = "hippo_hours_of_work"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    code = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)


class HippoJobType(Base):
    __tablename__ = "hippo_job_type"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)
    code = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)

class HippoJobTitle(Base):
    __tablename__ = "hippo_job_title"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)
    cadre = Column(String(255), nullable=True, index=True)
    classification = Column(String(255), nullable=True, index=True)
    description = Column(String(255), nullable=True)


class HippoLevel(Base):
    __tablename__ = "hippo_level"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    code = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    rank = Column(Integer, nullable=True)


class HippoLevelTitle(Base):
    __tablename__ = "hippo_level_title"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)
    rank = Column(Integer, nullable=True)


class HippoLocation(Base):
    __tablename__ = "hippo_location"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    address = Column(String(255), nullable=True)
    city = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)
    postal_code = Column(String(255), nullable=True)
    province = Column(String(255), nullable=True)


class HippoMaritalStatus(Base):
    __tablename__ = "hippo_marital_status"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)


class HippoMedicalLeave(Base):
    __tablename__ = "hippo_medical_leave"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    end_date = Column(DateTime, nullable=True)
    medical_leave_reason = Column(String(255), nullable=True)
    medical_leave_type = Column(String(255), nullable=True)
    notes = Column(String(255), nullable=True)
    start_date = Column(DateTime, nullable=True)


class HippoMedicalLeaveReason(Base):
    __tablename__ = "hippo_medical_leave_reason"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)


class HippoMedicalLeaveType(Base):
    __tablename__ = "hippo_medical_leave_type"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)


class HippoMembership(Base):
    __tablename__ = "hippo_membership"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    end_date = Column(DateTime, nullable=True)
    name = Column(String(255), nullable=True)
    notes = Column(String(255), nullable=True)
    start_date = Column(DateTime, nullable=True)
    type = Column(String(255), nullable=True)


class HippoMembershipType(Base):
    __tablename__ = "hippo_membership_type"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)


class HippoNationality(Base):
    __tablename__ = "hippo_nationality"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)


class HippoNote(Base):
    __tablename__ = "hippo_note"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    note = Column(String(255), nullable=True)
    note_type = Column(String(255), nullable=True)
    notes = Column(String(255), nullable=True)
    timestamp = Column(DateTime, nullable=True)


class HippoNoteType(Base):
    __tablename__ = "hippo_note_type"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)


class HippoOrganisation(Base):
    __tablename__ = "hippo_organisation"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)


class HippoOrganisationLevel(Base):
    __tablename__ = "hippo_organisation_level"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)


class HippoOrganisationType(Base):
    __tablename__ = "hippo_organisation_type"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)


class HippoOvertimeRule(Base):
    __tablename__ = "hippo_overtime_rule"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    description = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)


class HippoPayrollPeriod(Base):
    __tablename__ = "hippo_payroll_period"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    end_date = Column(DateTime, nullable=True)
    name = Column(String(255), nullable=True)
    start_date = Column(DateTime, nullable=True)


class HippoPermission(Base):
    __tablename__ = "hippo_permission"
    id = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=True)

class HippoPerson(Base):
    __tablename__ = "hippo_person"
    id = Column(String(255), primary_key=True)
    firstname = Column(String(255), nullable=True)
    middlename = Column(String(255), nullable=True)
    lastname = Column(String(255), nullable=True)
    gender = Column(String(255), nullable=True, index=True)
    address = Column(String(255), nullable=True)
    birthplace = Column(String)
    birthdate = Column(Date, nullable=True)
    recruitment_date = Column(Date, nullable=True)
    email = Column(String(255), nullable=True)
    marital_status = Column(String(255), nullable=True, index=True)
    nationality = Column(String(255), nullable=True, index=True)
    residence = Column(String(255), nullable=True, index=True)
    telephone = Column(String(255), nullable=True)
    title = Column(String(255), nullable=True)
    user_id = Column(String(255), nullable=True, index=True)
    degree  = Column(String(255), nullable=True, index=True)
    created_by = Column(String(255), nullable=True, index=True)
    last_modified_by = Column(String(255), nullable=True, index=True)
    last_modified = Column(DateTime, default=None)
    i2ce_hidden = Column(Integer, nullable=True, index=True)
    created = Column(DateTime, default=datetime.datetime.now())
    dependents = Column(Integer, nullable=True)

class HippoPersonPassport(Base):
    __tablename__ = "hippo_person_photo_passport"
    id = Column(String(255), primary_key=True)
    path = Column(String(255), nullable=False)
    person_id =  Column(String(255), nullable=True, index=True)
    created_by = Column(String(255), nullable=True, index=True)
    i2ce_hidden = Column(Integer, nullable=True, index=True)
    created = Column(DateTime, default=datetime.datetime.now())
    
class HippoEmploymentStatusInfo(Base):
    __tablename__ = "hippo_employment_status_info"
    id = Column(String(255), primary_key=True)
    person_id = Column(String(255), nullable=False, index=True)
    grade = Column(String(255), nullable=True, index=True)
    cadre = Column(String(255), nullable=True, index=True)
    classification = Column(String(255), nullable=True, index=True)
    employment_date = Column(DateTime, default=None)
    start_service_date = Column(DateTime, default=None)
    facility_id = Column(String(255), nullable=True, index=True)
    position_decision_ref= Column(String(255), nullable=True)
    ref_engagement = Column(String(255), nullable=True)
    salary_source = Column(String(255), nullable=True, index=True)
    salary = Column(Integer, nullable=True)
    job_type = Column(String(255), nullable=True, index=True)
    allowance = Column(Integer, nullable=True)
    employee_status = Column(String(255), nullable=True, index=True)
    created_by = Column(String(255), nullable=True, index=True)
    last_modified_by = Column(String(255), nullable=True, index=True)
    last_modified = Column(DateTime, default=None)
    i2ce_hidden = Column(Integer, nullable=True, index=True)
    seniority= Column(Integer, default=0)
    created = Column(DateTime, default=datetime.datetime.now())


class HippoIdentificationType(Base):
    __tablename__ = "hippo_identification_type"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default= datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=False)
    code = Column(String(255), nullable=True)

class HippoPersonIdentification(Base):
    __tablename__ = "hippo_person_identification"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default= datetime.datetime.now())
    created_by = Column(String(255), nullable=True, index=True)
    last_modified_by = Column(String(255), nullable=True, index=True)
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    number = Column(String(255), nullable=False)
    expiration_date = Column(Date,  nullable=True)
    acquisition_date = Column(Date,  nullable=True)
    type_id = Column(String(255), nullable=True, index=True)
    person_id = Column(String(255), nullable=True, index=True)
    country = Column(String(255), nullable=True, index=True)


class HippoPersonnelPosition(Base):
    __tablename__ = "hippo_personnel_position"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    position = Column(String(255), nullable=True)
    personnel = Column(String(255), nullable=True)


class HippoPersonnelPositionType(Base):
    __tablename__ = "hippo_personnel_position_type"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)


class HippoPersonnelStatus(Base):
    __tablename__ = "hippo_personnel_status"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)


class HippoPersonnelType(Base):
    __tablename__ = "hippo_personnel_type"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)


class HippoPhone(Base):
    __tablename__ = "hippo_phone"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    number = Column(String(255), nullable=True)
    type = Column(String(255), nullable=True)


class HippoPosition(Base):
    __tablename__ = "hippo_position"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    name = Column(String(255), nullable=True)
    position_type = Column(String(255), nullable=True)


class HippoPositionType(Base):
    __tablename__ = "hippo_position_type"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    name = Column(String(255), nullable=True)


class HippoProvince(Base):
    __tablename__ = "hippo_province"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    code = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)


class HippoQualification(Base):
    __tablename__ = "hippo_qualification"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)


class HippoQualificationLevel(Base):
    __tablename__ = "hippo_qualification_level"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)


class HippoRace(Base):
    __tablename__ = "hippo_race"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)


class HippoReligion(Base):
    __tablename__ = "hippo_religion"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)


class HippoRole(Base):
    __tablename__ = "hippo_role"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    assignable = Column(Integer, default=1)
    is_default = Column(Integer, default=0)
    homepage = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True, unique=True)
    created_by = Column(String(255), nullable=True)
    trickle_up = Column(String(255), nullable=True)


class HippoSalaryScale(Base):
    __tablename__ = "hippo_salary_scale"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    code = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    rank = Column(Integer, nullable=True)


class HippoSector(Base):
    __tablename__ = "hippo_sector"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)


class HippoSectorType(Base):
    __tablename__ = "hippo_sector_type"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)


class HippoSex(Base):
    __tablename__ = "hippo_sex"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)

class HippoEmployeeStatus(Base):
    __tablename__ = "hippo_employee_status"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)
    translate_key = Column(String(255), nullable=True)


class HippoSpeciality(Base):
    __tablename__ = "hippo_speciality"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)


class HippoSpecialityType(Base):
    __tablename__ = "hippo_speciality_type"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)


class HippoStatus(Base):
    __tablename__ = "hippo_status"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)


class HippoStrikeType(Base):
    __tablename__ = "hippo_strike_type"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)


class HippoTraining(Base):
    __tablename__ = "hippo_training"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    course = Column(String(255), nullable=True)
    end_date = Column(DateTime, nullable=True)
    name = Column(String(255), nullable=True)
    notes = Column(String(255), nullable=True)
    start_date = Column(DateTime, nullable=True)
    training_type = Column(String(255), nullable=True)


class HippoTrainingType(Base):
    __tablename__ = "hippo_training_type"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)


class HippoUnion(Base):
    __tablename__ = "hippo_union"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    name = Column(String(255), nullable=True)


class HippoUser(Base):
    __tablename__ = "hippo_user"

    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    password = Column(String(255), nullable=True)
    role = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)
    firstname = Column(String(255), nullable=True)
    lastname = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    creator = Column(String(255), nullable=True)


class HippoJob(Base):
    __tablename__ = "hippo_job"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), default='|')
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default= datetime.datetime.now())
    remap = Column(String(255), nullable=True)
    i2ce_hidden = Column(Integer, nullable=True)
    cadre = Column(String(255), nullable=True)
    classification = Column(String(255), nullable=True)
    code = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    title = Column(String(255), nullable=True)
    salary_grade = Column(String(255), nullable=True)



class HippoPersonTimesheet(Base):
    __tablename__ = "hippo_person_timesheet"

    id = Column(String(255), primary_key=True, comment="Identifiant unique")
    person_id = Column(String(255), index=True,nullable=False, comment="Parent (hiérarchie)")

    created = Column(DateTime, nullable=True, comment="Date de création")
    created_by = Column(String(255), nullable=True, comment="Créé par")

    last_modified = Column(DateTime, nullable=True, comment="Dernière modification")
    last_modified_by = Column(String(255), nullable=True, comment="Dernière modification par")
    i2ce_hidden = Column(Integer, nullable=True, comment="Masqué (1) ou 0)")

    days_absence_justified = Column(Integer, nullable=True, comment="Jours d'absence justifiée")
    days_absence_unjustified = Column(Integer, nullable=True, comment="Jours d'absence non justifiée")
    days_leave = Column(Integer, nullable=True, comment="Jours de congé")
    days_holiday = Column(Integer, nullable=True, comment="Jours fériés")
    days_sick = Column(Integer, nullable=True, comment="Jours de maladie")
    days_mission = Column(Integer, nullable=True, comment="Jours en mission")
    days_worked = Column(Integer, nullable=True, comment="Jours prestés / travaillés")
    days_planned = Column(Integer, nullable=True, comment="Jours prévus")

    month_year = Column(Date, nullable=True, comment="Mois et année de référence")

    bonus_local = Column(Numeric(12, 2), default=0, comment="Prime locale")
    bonus_pepfar = Column(Numeric(12, 2), default=0, comment="Prime PEPFAR")
    bonus_partner = Column(Numeric(12, 2), default=0, comment="Prime PTF (partenaire technique et financier)")
    bonus_risk = Column(Numeric(12, 2), default=0, comment="Prime de risque")

    project = Column(String(255), nullable=True, comment="Projet")
    salary_received = Column(Numeric(12, 2), nullable=True, comment="Salaire reçu")


class HippoModule(Base):
    __tablename__ = "hippo_module"
    id = Column(Integer, primary_key=True)
    label = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    icon = Column(String(50), nullable=True)
    parent = Column(Integer, nullable=True)

class HippoModulePage(Base):
    __tablename__ = "hippo_module_page"
    code = Column(String(255), primary_key=True)
    label = Column(String(255), nullable=True)
    url = Column(String(255), nullable=True)
    is_tree_item = Column(Integer, default=1)
    module_id = Column(Integer, nullable=False)
    application_id = Column(String(255), nullable=True)

class HippoRolePage(Base):
    __tablename__ = "hippo_role_page"
    uuid = Column(UUID, primary_key=True)  
    role_id = Column(String(255), nullable=False)
    page_code = Column(String(255), nullable=False)

class HippoUserRole(Base):
    __tablename__ = "hippo_user_role"
    uuid = Column(UUID, primary_key=True)
    user_id = Column(String(255), nullable=False)
    role_id = Column(String(255), nullable=False)


class HippoDashboard(Base):
    __tablename__ = "hippo_dashboard"
    uuid = Column(UUID, nullable=False, primary_key=True)
    mb_dashboard_id = Column(Integer, nullable=False)
    label = Column(String(255), nullable=False)
    last_modified = Column(DateTime, default=datetime.datetime.now())
    created = Column(DateTime, default=datetime.datetime.now())
    created_by = Column(String(255), index=True)
    last_modified_by = Column(String(255), index=True)
    

class HippoRoleDashboard(Base):
    __tablename__ = "hippo_role_dashboard"
    uuid = Column(UUID, primary_key=True)
    role_id = Column(String(255), nullable=False)
    dashboard_uuid = Column(UUID, nullable=False)
    last_modified = Column(DateTime, default=None)
    created = Column(DateTime, default=datetime.datetime.now())
    created_by = Column(String(255), index=True)
    last_modified_by = Column(String(255), index=True)


class HippoSetting(Base):
    __tablename__ = "setting"
    id = Column(Integer, primary_key=True)  
    app_name = Column(String(255), nullable=False)
    app_version = Column(String(255), nullable=False)
    responsible_name = Column(String(255), nullable=False)
    responsible_number = Column(String(255), nullable=False)
    logo = Column(String(255), nullable=True)
    created = Column(DateTime, default=datetime.datetime.now())
    last_modified = Column(DateTime, default=datetime.datetime.now())

class HippoAuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(UUID(as_uuid=True), primary_key=True)
    created = Column(DateTime, default=datetime.datetime.now())
    user_id = Column(String(255), nullable=False)
    operation = Column(Text, nullable=False)

class OrganizationUnitType(Base):
    __tablename__ = "organization_unit_type"
    
    id = Column(String(255), primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    position = Column(Integer, default=0)
    created = Column(DateTime(timezone=True), default=datetime.datetime.now())
    
class ViewOrgUnitList(Base):
    __tablename__ = "organization_unit"
    id = Column(String(255), primary_key=True)
    parent = Column(String(255), nullable=False)
    name = Column(String(255))
    created = Column(DateTime, default=datetime.datetime.now())
    last_modified = Column(DateTime, default=datetime.datetime.now())
    code = Column(String(25), nullable=True)
    type = Column(String(255))
    level = Column(String(255))


class OrganizationUnitStandards(Base):
    __tablename__ = "organization_unit_standards"
    
    uuid = Column(UUID(as_uuid=True), primary_key=True)
    classification_id = Column(String(255))
    org_unit_type_id = Column(String(255))
    number_of_positions = Column(Integer)
    last_modified = Column(DateTime(timezone=True),  default=datetime.datetime.now())
    created = Column(DateTime(timezone=True),  default=datetime.datetime.now())
    created_by = Column(String(255))
    last_modified_by = Column(String(255))
    i2ce_hidden = Column(Integer, default=0)

class OrganizationLevel(Base):
    __tablename__ = "organisation_level"
    id = Column(String(255), primary_key=True)
    name = Column(String(255))
    level = Column(Integer)