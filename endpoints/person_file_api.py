from datetime import datetime
from fastapi import APIRouter, Depends, Depends, Response, Request
from jinja2 import Environment, FileSystemLoader
from helpers.helpers import generate_qr_code
from sqlalchemy.orm import Session
from manage.database import SessionLocal, engine
from models.crud import get_person_scheduled_training_course, get_person_timesheet
from weasyprint import HTML
from sqlalchemy.sql import text
from sqlalchemy.ext.asyncio import AsyncSession
from config.sqlquery import person_file_employments, person_file_query
 



router = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


@router.get("/person")
async def personFile(id, request: Request, db: Session = Depends(get_session) ):
    query =  person_file_query(id)

    data  = await db.execute(text(query))

    result = data.mappings().all() 
    if (len(result)  == 0): 
        return {"error": 'No such person'}
    person = result[0]

    res = await db.execute(text(person_file_employments(id)))
    employments = res.mappings().all() 

    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("person-file.html")
    _time = datetime.now().strftime( "%d-%m-%Y %H:%M:%S")
   # person['validation_date']  =
    data = [
            {
                'title':  "Informations individuelles",
                'values': [
                    {
                        'key':  'Nom',
                        'value': person.firstname
                    },
                    {
                        'key':  'Postnom',
                        'value': person.surname
                    },
                    {
                        'key':  'prenom',
                        'value': person.othername 
                    },
                     {
                        'key':  " Nationalité",
                        'value': ''
                    },
                    {
                        'key':  " Niveau d'Etude",
                        'value': person.degree
                    },
                    {
                        'key':  "Etablissement de formation",
                        'value': None
                    },
                    {
                        'key':  "Pays de formation",
                        'value': None
                    },
                    
                    {
                        'key':  "Residence",
                        'value': person.residence
                    }
                ]
            },{
                'title':  "Identification",
                'values': [
                    {
                        'key':  "Type",
                        'value': 'Matricule'
                    },
                     {
                        'key':  "Numero d'identification",
                        'value': ''
                    },
                    # {
                    #     'key':  "Date de delivrance",
                    #     'value':   person.created.strftime("%d-%m-%Y")  if  (person.created != None and isinstance(person.created ,datetime))  else  None  
                    # },
                    # {  
                    #     'key':  "Numéro d’ordre professionnel",
                    #     'value':  None
                    # }
                ]
            },
            {
                'title':  "Informations démographiques",
                'values': [
                     {
                        'key':  "Lieu de naissance",
                        'value':  None
                    },
                    # {
                    #     'key':  "Date de naissance",
                    #     'value':   person.birth_date.strftime("%d-%m-%Y")  if (person.birth_date != None and isinstance(person.birth_date ,datetime)) else  None 
                    # },
                    
                    #  {
                    #     'key':  "Genre",
                    #     'value': person.gender.replace("gender|", "") if (person.gender != None )  else  person.gender
                    # },
                    # {
                    #     'key':  "Etat civil",
                    #     'value': person.marital_status
                    # },
                    # {
                    #     'key':  "Nombre de personnes en charge",
                    #     'value': person.dependents
                    # }
                ]
            },
            {
                'title':  "Contact personnel",
                'values': [
                    # {
                    #     'key':  "Adresse physique",
                    #     'value': person.contact_personal_address
                    # },
                    #  {
                    #     'key':  "Téléphone mobile",
                    #     'value': person.contact_personal_mobile_phone
                    # },
                    # {
                    #     'key':  "Téléphone alternatif",
                    #     'value': person.contact_personal_alt_telephone
                    # },
                    # {
                    #     'key':  "Adresse e-mail",
                    #     'value': person.contact_personal_email
                    # },
                ]
            },
            {
                'title':  "Contact professionnel",
                'values': [
                    # {
                    #     'key':  "Adresse physique",
                    #     'value': person.contact_work_address
                    # },
                    #  {
                    #     'key':  "Téléphone mobile",
                    #     'value': person.contact_work_mobile_phone
                    # },
                    # {
                    #     'key':  "Téléphone alternatif",
                    #     'value': person.contact_work_alt_telephone
                    # },
                    # {
                    #     'key':  "Adresse e-mail",
                    #     'value': person.contact_work_email
                    # }
                ]
            }
        ]
    i  = 0
    for p in employments :
        i += 1
        data.append(
            {
                'title':  f"Information sur le statut d'emploi ({i})",
                'values': [
                        {
                            'key':  "Categorie",
                            'value': p.cadre
                        },
                        {
                            'key':  "Profession",
                            'value': p.classification
                        },
                        {
                            'key':  "Fonction",
                            'value': p.job
                        },
                        # {
                        #     'key':  "Grade",
                        #     'value': p.salary_grade
                        # },
                        # {
                        #     'key':  "Date d'engagement",
                        #     'value': p.year_of_appointment.strftime("%d-%m-%Y")  if (p.year_of_appointment != None and isinstance(p.year_of_appointment,datetime) ) else  None
                        # },
                        # {
                        #     'key':  "Structure d'affectation",
                        #     'value': p.facility
                        # },
                        # {
                        #     'key':  "Zone de santé d'affectation",
                        #     'value': p.health_area
                        # },
                        # {
                        #     'key':  "Province d'affectation",
                        #     'value': p.district
                        # },
                        # {
                        #     'key':  "Référence commission d'affectation",
                        #     'value': p.ref_on_employment
                        # },
                        # {
                        #     'key':  "Référence arrêté d'admission sous statut",
                        #     'value': p.ref_engagement
                        # },

                        # {
                        #     'key':  "Référence acte de nomination",
                        #     'value': None
                        # },

                        #  {
                        #     'key':  "Salaire",
                        #     'value': "OUI" if p.salaire == 1 else  ("NON" if p.salaire == 0 else None)
                        # },
                        #  {
                        #     'key':  "Prime",
                        #     'value': "OUI" if p.prime == 1 else  ("NON" if p.prime == 0 else None)
                        # },
                        #  {
                        #     'key':  "Position administrative",
                        #     'value': p.employee_status
                        # },
                        # {
                        #     'key':  "Est identifié",
                        #     'value': "OUI" if p.identifie == 1 else  ("NON" if p.identifie == 0 else None)  
                        # },

                    ]

            }
        )
    totalCom = 0
    totalLen = 0
    for gp in data: 
        subtotalCom  = 0
        totalLen = totalLen + len(gp['values'])
        for v in gp['values']:
            x = 0
            if v['value'] != None : 
                x = 1  
                totalCom = totalCom + 1 
                subtotalCom  = subtotalCom + 1
            v['comp'] = x

        # gp['comp'] = "{:.0f}%".format(subtotalCom / len(gp['values'])*100) 
    
    data.append(
        {
            'title':  "COMPLETUDE GENERALE",
            'values': [],
            'comp': "{:.0f}%".format((totalCom /totalLen)*100)
        }
    )
    qr_data= generate_qr_code(str(request.url))

    training_courses = get_person_scheduled_training_course(
            person_id=id,
            db=db
        )
 
    person_timesheet =  get_person_timesheet(
        person_id=id, 
        db=db 
    )
 
   
    rendered_html = template.render(
        data=data,
        date=_time,
        qr_data= qr_data,
        person = person,
        courses = training_courses,
        person_timesheet = person_timesheet
    )   

   
     
    pdf_content = HTML(string=rendered_html).write_pdf()
    return Response(content=pdf_content, media_type="application/pdf", 
        headers={
           'Access-Control-Expose-Headers': 'Content-Disposition',
           'Content-Disposition': f'attachment;filename="IHRIS - FICHE - {person.firstname} {person.othername} {person.surname} {_time}.pdf"'
        }
    )