from sqlalchemy.orm import Session
from config.Database2 import SessionLocal
from sqlalchemy.sql import text

def dashboard_data(db:Session):
    query = f""" SELECT hippo_training_course_category.name,
    (
        SELECT count(*) FROM hippo_scheduled_training_course
        JOIN hippo_training_course  on  hippo_training_course.id  = hippo_scheduled_training_course.training_course
        where  hippo_training_course.training_course_category =  hippo_training_course_category.id 
    ) as  'scheduled_training',
    (
        SELECT count(*) FROM hippo_person_scheduled_training_course
        JOIN hippo_scheduled_training_course  on  hippo_scheduled_training_course.id  = hippo_person_scheduled_training_course.scheduled_training_course
        JOIN hippo_training_course  on  hippo_training_course.id  = hippo_scheduled_training_course.training_course
        join  hippo_demographic on hippo_demographic.parent = hippo_person_scheduled_training_course.parent
        where  hippo_training_course.training_course_category =  hippo_training_course_category.id  and 
        gender ='gender|M'
    ) as  'person_scheduled_training_m',
    (
        SELECT count(*) FROM hippo_person_scheduled_training_course
        JOIN hippo_scheduled_training_course  on  hippo_scheduled_training_course.id  = hippo_person_scheduled_training_course.scheduled_training_course
        JOIN hippo_training_course  on  hippo_training_course.id  = hippo_scheduled_training_course.training_course
        join  hippo_demographic on hippo_demographic.parent = hippo_person_scheduled_training_course.parent
        where  hippo_training_course.training_course_category =  hippo_training_course_category.id  and 
        gender ='gender|F'
    ) as  'person_scheduled_training_f'
    FROM  hippo_training_course_category
         """
    result  = db.execute(text(query))
    scheduled_training = []
    person_scheduled_training_f = []
    person_scheduled_training_m = []
    labels = []
    labels1 = []
    i = 0;

    for key in result.fetchall() : 
        scheduled_training.append(key.scheduled_training)
        person_scheduled_training_f.append(key.person_scheduled_training_f)
        person_scheduled_training_m.append(key.person_scheduled_training_m)
        labels.append(key.name)
        labels1.append((++i))

    return {
        "labels" : labels, 
        "labels1" :labels1, 
        "scheduled_training": scheduled_training,
        "person_scheduled_training_f": person_scheduled_training_f,
        "person_scheduled_training_m": person_scheduled_training_m  
    }
 
def  scheduled_training_course(db:Session):
    query =""" 
         SELECT hippo_training_course.id, hippo_training_course.name, hippo_training_course_category.name as 'category',
 
    (SELECT count(*) FROM hippo_scheduled_training_course where  hippo_scheduled_training_course.training_course =  hippo_training_course.id) as  'scheduled_training_course',
    (
        SELECT count(*) FROM  hippo_person_scheduled_training_course
        join  hippo_demographic on hippo_demographic.parent = hippo_person_scheduled_training_course.parent
        where  hippo_person_scheduled_training_course.scheduled_training_course in 
        (SELECT hippo_scheduled_training_course.id FROM hippo_scheduled_training_course where  hippo_scheduled_training_course.training_course =  hippo_training_course.id)
        and   gender ='gender|M'
    ) as 'gender_m',(
        SELECT count(*) FROM  hippo_person_scheduled_training_course
        join  hippo_demographic on hippo_demographic.parent = hippo_person_scheduled_training_course.parent
        where  hippo_person_scheduled_training_course.scheduled_training_course in 
        (SELECT hippo_scheduled_training_course.id FROM hippo_scheduled_training_course where  hippo_scheduled_training_course.training_course =  hippo_training_course.id)
        and   gender ='gender|F'
    ) as 'gender_f' from hippo_training_course
    left join  hippo_training_course_category on hippo_training_course_category.id = hippo_training_course.training_course_category
    """
    result  = db.execute(text(query))

    return {
        "data": result.fetchall()
    }
