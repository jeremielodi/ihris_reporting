from sqlalchemy.orm import Session
from config.Database2 import SessionLocal
from models.models import (Cadre, Classification, HealthAreaBaseListe, Job, Person, PersonScheduledTrainingCourse,
                           PersonTimesheet, ScheduledTrainingCourse, TrainingCourse, TrainingCourseExam,
                           TrainingCourseExamType)
from sqlalchemy.sql import text
from sqlalchemy import and_, desc,text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import json
from sqlalchemy import text
from fastapi import Depends
from models.validation_crud import find_person_validation
from reports.reports import get_internal_completeness_data
from endpoints.validation_api import validation

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


# Get Person list,params:   pr_id: str = "0",tr_id: str ="0", zs_id: str = "0", 
# filter: str ="",page: int = 0, limit: int = 25,column_filter: str = None,

async def get_people2(org_unit_id: str = "0",
                search: str = None, page: int = 1, limit: int = 20, column_filter: str = None,
                birth_date_filter: str = None,
                matricule_filter: str = None,
                download_xlsx: int = 0,
                db: AsyncSession = Depends(get_session),
                ):
    data = await get_internal_completeness_data(org_unit_id=org_unit_id, db=db)

    if (len(data)) == 0 :
        return {
            "data": { 'data': []},
            "total_records": 0
        }
    if column_filter is not None:
        data = data[data[column_filter].isnull()]

    max_records = (len(data))


    if search != 'null':
        data = data[data['fullname'].str.contains(
            search.strip().upper()) == True]

    if matricule_filter != 'null':
        data = data[data['matricule'].str.contains(
            matricule_filter.strip().upper()) == True]

    if birth_date_filter != 'null' and len(birth_date_filter) > 5:
        data = data[data['birth_date'].str.contains(
            birth_date_filter.strip().upper()) == True]

    data = data.drop_duplicates(subset=['id'])
    data = data.sort_values(by=['fullname'])
    if download_xlsx == 1:
        return data
    data['index'] = range(0, len(data))
    offset = (page * limit) - limit
    res = data.loc[data['index'].between(offset, offset + limit-1)]

    validations = [] #find_person_validation(db= ge, person_ids=res['id'])
    res['validation'] = 0
    #for index, row in res.iterrows():
    for val in validations:
        res.loc[res['id'] == val.parent,'validation'] = 1
             
    return {
        "data": json.loads(res.to_json(orient="table")),
        "total_records": max_records
    }


def get_people(db: Session, pr_id: str = "0", tr_id: str = "0", zs_id: str = "0", fosa_id: str = "0",
               filter: str = "", page: int = 0, limit: int = 25, column_filter: str = None,
               ):

    query = locationQuery = None
    if (fosa_id != '0'):
        locationQuery = 'facility'
    elif (zs_id != "0"):
        locationQuery = "health_area_id = '" + zs_id + "'"
    elif (tr_id != "0"):
        locationQuery = "county = '" + tr_id + "'"
    elif (pr_id != "0"):
        locationQuery = "district = '" + pr_id + "'"

    if column_filter is not None:
        if locationQuery is not None:
            query = db.query(Person).where(
                and_(
                    text('internal_completeness.' + locationQuery),
                    text('internal_completeness.' + column_filter + ' is null')
                )
            )
        else:
            query = db.query(Person).where(
                and_(
                    text('internal_completeness.' + column_filter + ' is null')
                )
            )
    else:
        if (locationQuery is not None):
            query = db.query(Person).where(
                text('internal_completeness.' + locationQuery))
        else:
            query = db.query(Person)

    if filter != "":
        query.filter(Person.fullname.like("%" + filter + "%"))

    data = query.order_by(Person.fullname.asc()).offset(
        (limit * page) - limit).limit(limit + 1).all()

    return {
        "data":  data,
        "total_records": query.count()
    }


"""
 Get Person timesheet, Params: person_id
"""


def get_person_timesheet(db: Session, person_id: str):

    return db.query(PersonTimesheet).filter(
        PersonTimesheet.parent == person_id
    ).order_by(desc(PersonTimesheet.mois_annee)).limit(12).all()


"""
 Get Person timesheet, Params perspn_id
"""


def get_person_scheduled_training_course(db: Session, person_id: str):

    result = db.query(
        PersonScheduledTrainingCourse,
        ScheduledTrainingCourse,
        TrainingCourse
    ).join(
        ScheduledTrainingCourse, ScheduledTrainingCourse.id == PersonScheduledTrainingCourse.scheduled_training_course
    ).join(
        TrainingCourse,  TrainingCourse.id == ScheduledTrainingCourse.training_course
    ).filter(
        PersonScheduledTrainingCourse.parent == person_id
    ).order_by(desc(PersonScheduledTrainingCourse.id)).all()

    test = []
    # return db.query(TrainingCourseExamType).all()

    if len(result) > 0:
        for elt in result:
            t = db.query(TrainingCourseExam).where(
                TrainingCourseExam.parent == elt.PersonScheduledTrainingCourse.id
            ).all()
            test.append({
                "course": elt.TrainingCourse,
                "scheduled_course": elt.ScheduledTrainingCourse,
                "tests": t,
            })
    return test


def get_revenu_report_utils(db: Session):

    jobs = db.query(Job).where(Job.i2ce_hidden == 0).all()
    classifications = db.query(Classification).where(
        Classification.i2ce_hidden == 0).all()
    cadres = db.query(Cadre).where(Cadre.i2ce_hidden == 0).all()

    return {
        'jobs': jobs,
        'classifications': classifications,
        'cadres': cadres
    }

def get_scheduled_training_course(db:Session,startDate:str, endDate:str, category:str ="1"):
    
        query = """SELECT hippo_scheduled_training_course.id, hippo_scheduled_training_course.name as stc, hippo_training_course.name,
        hippo_training_course_category.name as category_name,
        hippo_scheduled_training_course.start_date, end_date, hippo_scheduled_training_course.instructors,
        (
        SELECT count(*) FROM hippo_person_scheduled_training_course 
        join  hippo_demographic on hippo_demographic.parent = hippo_person_scheduled_training_course.parent
        where   hippo_person_scheduled_training_course.scheduled_training_course = hippo_scheduled_training_course.id
                ) as 'gender_FaM',
        (
        SELECT count(*) FROM hippo_person_scheduled_training_course 
        join  hippo_demographic on hippo_demographic.parent = hippo_person_scheduled_training_course.parent
        where   hippo_person_scheduled_training_course.scheduled_training_course = hippo_scheduled_training_course.id
                    and   gender ='gender|M'
                ) as 'gender_m',
        hippo_county.name as 'location'
        FROM hippo_scheduled_training_course
        left join hippo_training_course on hippo_scheduled_training_course.training_course = hippo_training_course.id
        left join hippo_training_course_category on hippo_training_course_category.id = hippo_training_course.training_course_category 
        left join hippo_county on hippo_county.id  = hippo_scheduled_training_course.location 
        """
       
        query = f"{query} WHERE (hippo_scheduled_training_course.created BETWEEN   '{startDate} 00:00:00'  AND '{endDate} 00:00:00')"
        if category != '1': 
            query =  f"{query} and  hippo_training_course_category.id =  '{category}'"

        result  = db.execute(text(query))
        return   result.fetchall() 

def scheduled_training_course_details(db:Session,scheduled_training_course_id:str):

    query = f"""
    SELECT distinct hippo_person.id, hippo_person.firstname, hippo_person.othername, hippo_person.surname,
        hippo_demographic.gender, 
        hippo_demographic.birth_date,
        hippo_cadre.name as cadre,
         hippo_person_id.id_num,
         hippo_facility.name as facility,
         hippo_health_area.name as health_area

        FROM  hippo_person_scheduled_training_course
             join hippo_demographic on hippo_demographic.parent = hippo_person_scheduled_training_course.parent
             join hippo_person on hippo_person.id = hippo_person_scheduled_training_course.parent
             join hippo_employment_status_rdc on hippo_employment_status_rdc.parent = hippo_person.id
             join hippo_cadre on hippo_employment_status_rdc.cadre = hippo_cadre.id
             join hippo_person_id on hippo_person_id.parent = hippo_person.id
             left join hippo_facility on hippo_facility.id  =  hippo_employment_status_rdc.facility
             left join  hippo_health_area on hippo_health_area.id =  hippo_facility.location 
        WHERE  hippo_person_scheduled_training_course.scheduled_training_course = '{scheduled_training_course_id}'
    """
    result  = db.execute(text(query))
    
    cadres = db.query(Cadre).where(Cadre.i2ce_hidden == 0).all()
    
    return   {
        "data": result.fetchall() ,
        "cadres": cadres
    }



