from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer, Enum, DateTime
from config.Database2 import Base
import datetime


class Person(Base):
    __tablename__ = "internal_completeness"

    id = Column(String, primary_key=True)
    fullname = Column(String)
    firstname = Column(String)
    surname = Column(String)
    othername = Column(String)
    gender = Column(String)
    birth_date = Column(String)
    dependents = Column(String)
    degree = Column(String)
    marital_status = Column(String)
    mobile_phone = Column(String)
    address = Column(String)
    ref_on_employment = Column(String)
    matricule = Column(String)
    ref_engagement = Column(String)
    position = Column(String)
    cadre_id = Column(String)
    cadre = Column(String)
    classification_id = Column(String)
    classification = Column(String)
    job = Column(String)
    salary_grade_id = Column(String)
    salary_grade = Column(String)
    salaire = Column(String)
    prime = Column(String)
    identifie = Column(String)
    year_of_appointment = Column(String)
    facility_name = Column(String)
    facility = Column(String)
    health_area_id = Column(String)
    health_area_name = Column(String)
    county = Column(String)
    county_name = Column(String)
    district = Column(String)
    district_name = Column(String)


class PersonTimesheet(Base):
    __tablename__ = "hippo_person_timesheet"
    id = Column(String, primary_key=True)
    parent = Column(String)
    last_modified = Column(DateTime)
    created = Column(DateTime)
    jours_abs_justif = Column(Integer)
    jours_abs_non_justif = Column(Integer)
    jours_conge = Column(Integer)
    jours_ferie = Column(Integer)
    jours_maladie = Column(Integer)
    jours_mission = Column(Integer)
    jours_prestes = Column(Integer)
    jours_prevus = Column(Integer)
    mois_annee = Column(DateTime)
    prime_locale = Column(String)
    prime_pepfar = Column(String)
    prime_ptf = Column(String)
    prime_risque = Column(String)
    projet = Column(String)
    salaire_recu = Column(String)


class PersonScheduledTrainingCourse(Base):

    __tablename__ = "hippo_person_scheduled_training_course"
    id = Column(String, primary_key=True)
    parent = Column(String)
    last_modified = Column(DateTime)
    created = Column(DateTime)
    attending = Column(String)
    average = Column(String)
    certification_date = Column(String)
    completed = Column(String)
    duty_commencement_date = Column(String)
    evaluation_deux = Column(String)
    evaluation_trois = Column(String)
    evaluation_un = Column(String)
    is_retraining = Column(String)
    notes = Column(String)
    postest = Column(String)
    pretest = Column(String)
    request_date = Column(DateTime)
    scheduled_training_course = Column(String)
    source_financement = Column(String)
    training_course_evaluation = Column(String)
    training_course_mod = Column(String)


class ScheduledTrainingCourse(Base):

    __tablename__ = "hippo_scheduled_training_course"
    id = Column(String, primary_key=True)
    parent = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    instructors = Column(DateTime)
    location = Column(String)
    training_course = Column(String)


class TrainingCourse(Base):

    __tablename__ = "hippo_training_course"
    id = Column(String, primary_key=True)
    parent = Column(String)
    name = Column(String)


class TrainingCourseExam(Base):

    __tablename__ = "hippo_training_course_exam"
    id = Column(String, primary_key=True)
    parent = Column(String)
    score = Column(String)
    training_course_exam_type = Column(String)


class TrainingCourseExamType(Base):
    __tablename__ = "hippo_training_course_exam_type"
    id = Column(String, primary_key=True)
    name = Column(String)


class Country(Base):
    __tablename__ = "hippo_country"
    id = Column(String, primary_key=True)
    name = Column(String)
    i2ce_hidden = Column(Integer)


class District(Base):
    __tablename__ = "hippo_district"
    id = Column(String, primary_key=True)
    parent = Column(String)
    name = Column(String)
    i2ce_hidden = Column(Integer)


class County(Base):
    __tablename__ = "hippo_county"
    id = Column(String, primary_key=True)
    parent = Column(String)
    name = Column(String)
    i2ce_hidden = Column(Integer)
    district = Column(String)


class HealthArea(Base):
    __tablename__ = "hippo_health_area"
    id = Column(String, primary_key=True)
    i2ce_hidden = Column(Integer)
    parent = Column(String)
    name = Column(String)
    county = Column(String)


class Facility(Base):
    __tablename__ = "hippo_facility"
    id = Column(String, primary_key=True)
    location = Column(String)
    name = Column(String)
    i2ce_hidden = Column(Integer)


class User(Base):
    __tablename__ = "user"
    id = Column(String, primary_key=True)
    password = Column(String)
    username = Column(String)


class AccessFacility(Base):
    __tablename__ = "hippo_access_facility"
    id = Column(String, primary_key=True)
    location = Column(String)
    parent = Column(String)


class Cadre(Base):
    __tablename__ = "hippo_cadre"
    id = Column(String, primary_key=True)
    name = Column(String)
    i2ce_hidden = Column(Integer)


class Classification(Base):
    __tablename__ = "hippo_classification"
    id = Column(String, primary_key=True)
    name = Column(String)
    i2ce_hidden = Column(Integer)


class Job(Base):
    __tablename__ = "hippo_job"
    id = Column(String, primary_key=True)
    title = Column(String)
    i2ce_hidden = Column(Integer)



class Record(Base):
    __tablename__ = "record"
    id =Column(Integer, primary_key=True)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    created = Column(DateTime, default=datetime.datetime.utcnow)
    form =Column(Integer)
    parent_form =Column(Integer, default=0)
    parent_id = Column(Integer,default=0)


class Hippo_person(Base):
    __tablename__ = "hippo_person"
    id =Column(String,primary_key=True)
    parent = Column(String)
    last_modified =  Column(DateTime, default=datetime.datetime.utcnow)
    created =Column(DateTime, default=datetime.datetime.utcnow)
    nationality = Column(String, default="country|CD")
    residence =  Column(String, default="district|703")
    firstname =Column(String)
    surname = Column(String)
    othername = Column(String)
    degree = Column(String)
    csd_uuid = Column(String)

class PersonValidation (Base):
    __tablename__ = "person_validation"
    id =Column(Integer,primary_key=True, nullable=False)
    parent = Column(String)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    validatedBy = Column(String)
    code = Column(String)
    facility = Column(String)
    healthArea =  Column(String)
    county = Column(String)
    district= Column(String)
    country = Column(String)

class PersonValidator(Base):
    __tablename__ = "person_validator"
    id =Column(Integer,primary_key=True, nullable=False)
    username = Column(String)
    name = Column(String)

class HealthAreaBaseListe(Base):
    __tablename__ = "health_area_base_list"
    id = Column(String, primary_key=True)
    parent = Column(String)
    ha_id = Column(String)
    value = Column(Integer)