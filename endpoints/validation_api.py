from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from config.Database2 import SessionLocal
from endpoints.user_api import get_current_active_user
from models.models import PersonValidator, User
from models.validation_crud import person_validation
 

router = APIRouter(
    prefix="/validation",
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get('/person/{person_id}')
def validation(
        person_id: str,
        facility:str,
        healthArea:str,
        county:str,
        district:str, 
        current_user: Annotated[User, Depends(get_current_active_user)],
        db: Session = Depends(get_db),
    ):

    user = db.query(User).where(
        User.username == current_user
    ).first()
    if  user != None:
        validatorData  =  db.query(PersonValidator).where(
        PersonValidator.username == user.username).first()
        if(validatorData!=None):
            return  person_validation(
                person_id= person_id,
                facility = facility,
                healthArea= healthArea,
                county= county,
                district= district,
                userId = user.username,
                code= validatorData.name,
                db = db
            )
    return {"error": "Utilisateur non autorisé"}

 