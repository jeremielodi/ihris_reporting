
from datetime import datetime
from fastapi import APIRouter, Depends, Depends, Request, Response
from jinja2 import FileSystemLoader
from helpers.helpers import download_dataframe_as_xlsx, is_datetime
from models.crud import (get_people2, get_person_scheduled_training_course,
                         get_person_scheduled_training_course, get_scheduled_training_course, scheduled_training_course_details)
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from manage.database import SessionLocal, engine
from models.validation_crud import validation_count
from reports.reports import download_data
from models.models import Hippo_person, Person, Record
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

router = APIRouter()




@router.get("/list")
async def people(org_unit_id: str = "0", search: str = "",
    matricule: str = None, birth_date: str = None,
    page: int = 1, limit: int = 25,
    column_filter: str = None,
    download_xlsx: int = 0,
    filename: str = '',
    session: AsyncSession = Depends(get_session),
):
    response = await get_people2(org_unit_id = org_unit_id,
        search=search,
        birth_date_filter=birth_date,
        matricule_filter=matricule,
        limit=limit, page=page,
        column_filter=column_filter,
        download_xlsx=download_xlsx,
        db=session
    )

    if download_xlsx == 1:
        return download_dataframe_as_xlsx(
            df=response,
            filename=f'IHRIS - {filename}'
        )
    
    # val = validation_count(
    #      facility=fosa_id,
    #      healthArea=zs_id ,
    #      county=tr_id,
    #      district=pr_id,
    #      db=db
    #  )
    return {
        "page": page,
        "limit": limit,
        "total_records": response['total_records'],
        "data": response['data']['data'],
        #'validated': val
    }
 
 
@router.post("/person")
def create_person(
     firstname:str, 
     surname:str, 
     othername:str, 
     degree:str,  
     residence:str,
     db: Session = Depends(get_session),
           
    ):

    record = Record(id= 5987023, form = 53 )

    person =  Hippo_person()
    person.id  = "person|5987024" 
    person.parent=  "0|0",
    person.firstname= firstname,
    person.surname = surname,
    person.othername =  othername, 
    person.degree = degree, 
    person.residence = residence,
    person.csd_uuid = "IHJHSSZ"
    
    db.add(person)
    db.commit()
    
    return 

@router.patch("/person/{person_id}")
def update_person(person_id: str):
    return 1 

@router.get('/download')
async def download(org_unit_id: str = "0", filter: str = 'all', title: str = 'data', db: AsyncSession = Depends(get_session)):

    df, _title = await download_data(org_unit_id=org_unit_id, filter=filter,
        db= db
    )

    return download_dataframe_as_xlsx(
        df=df,
        filename=f'{_title} - {title}'
    )

''' Person person_scheduled_training_course'''


@router.get("/person_scheduled_training_course")
def person_scheduled_training_course(person_id: str, db: AsyncSession = Depends(get_session)):

    res = get_person_scheduled_training_course(
        person_id=person_id,
        db=db
    )
    return res
 

@router.get("/scheduled_training_course")
def scheduled_training_course(startDate: str, endDate:str,db: AsyncSession = Depends(get_session), category:str="1", download:int =0):
    res  = get_scheduled_training_course(db=db, category=category, startDate=startDate, endDate=endDate)
    if download == 1 : 
        env = Environment(loader=FileSystemLoader("templates"))
        template = env.get_template("scheduled_training_course.html")
        _time = datetime.now().strftime( "%d-%m-%Y %H:%M:%S")
        rendered_html = template.render(
            data=res,
            dates=[
                datetime.strptime(startDate, '%Y-%m-%d'),
                datetime.strptime(endDate, '%Y-%m-%d')
            ],
            current_date= _time
        )
        pdf_content = HTML(string=rendered_html).write_pdf()
        return Response(content=pdf_content, media_type="application/pdf", 
            headers={
            'Access-Control-Expose-Headers': 'Content-Disposition',
            'Content-Disposition': f'attachment; filename="FORMATIONS ORGANISEES-{_time}.pdf"'}
        )
    return {
        'data': res
    }



@router.get('/scheduled_training_course_details/{id}')
def _scheduled_training_course_details(id: str,db: AsyncSession = Depends(get_session),download:int=0, title:str=None):
    
    res = scheduled_training_course_details(db=db, scheduled_training_course_id=id)
    
    if download == 1: 
        env = Environment(loader=FileSystemLoader("templates"))
        env.filters['is_datetime'] = is_datetime
        template = env.get_template("scheduled_training_course_details.html")
        _time = datetime.now().strftime( "%d-%m-%Y %H:%M:%S")
        rendered_html = template.render(
            data = res['data'],
            title = title,
            current_date= _time
        )
        pdf_content = HTML(string=rendered_html).write_pdf()
        return Response(content=pdf_content, media_type="application/pdf", 
             headers={
             'Access-Control-Expose-Headers': 'Content-Disposition',
             'Content-Disposition': f'attachment; filename="FORMATIONS ORGANISEES-{_time}.pdf"'}
        )
    return  res


 

