from sqlalchemy.orm import Session
from models.models import  PersonValidation
 

def person_validation(db: Session, person_id: str,  facility:str,healthArea:str,county:str, district:str, userId:str, code:str  ):
    valisation = PersonValidation(
          parent= person_id,
         # date =  ,
            code = code,
           validatedBy = userId,
           facility = facility,
           healthArea = healthArea,
           county = county,
           district= district,
           country= "country|CD"
     )
    db.add(valisation)
    db.commit()
    db.refresh(valisation)
    return valisation

def validation_count(
        facility:str,
        healthArea:str,
        county:str,
        district:str,
        db: Session):
    
    if(facility != "0"):
        return db.query(PersonValidation).where(PersonValidation.facility == facility).count()
    if(healthArea != "0"):
        return db.query(PersonValidation).where(PersonValidation.healthArea == healthArea).count()
    if(county != "0"):
        return db.query(PersonValidation).where(PersonValidation.county == county).count()
    if(district != "0"):
        return db.query(PersonValidation).where(PersonValidation.district == district).count()
    return db.query(PersonValidation).count()

def validated_ids(
        facility:str,
        healthArea:str,
        county:str,
        district:str,
        db: Session):
    if(facility != "0"):
        ids = db.query(PersonValidation.parent).where(PersonValidation.facility == facility).all()
    if(healthArea != "0"):
        ids = db.query(PersonValidation.parent).where(PersonValidation.healthArea == healthArea).all()
    if(county != "0"):
        ids = db.query(PersonValidation.parent).where(PersonValidation.county == county).all()
    if(district != "0"):
        ids =  db.query(PersonValidation.parent).where(PersonValidation.district == district).all()
    ids =  db.query(PersonValidation.parent).all()
    id_list = [id[0] for id in ids] 
    return id_list

def find_person_validation(db: Session, person_ids: list[str]):
    valisations = db.query(PersonValidation).where(PersonValidation.parent.in_(person_ids)).all()
    return valisations