# ---------------------------------------------------------
# IMPORT PEOPLE CONTROLLER (FINAL - MATCH YOUR SCHEMA)
# ---------------------------------------------------------

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from manage.database import SessionLocal
from endpoints.user_api import get_current_active_user

from manage.models import (
    HippoPerson,
    HippoEntityMap,
    HippoAuditLog,
    HippoPersonIdentification,
    HippoEmploymentStatusInfo
)

from manage.services.entity_map import entity_map
from manage.utils import generate_unit_id

import uuid
from datetime import datetime


apiRouter = APIRouter()


# ---------------------------------------------------------
# DB SESSION
# ---------------------------------------------------------
async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


# ---------------------------------------------------------
# HELPER: parse date safely
# ---------------------------------------------------------
def parse_date(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except:
        return None


# ---------------------------------------------------------
# IMPORT PEOPLE
# ---------------------------------------------------------
@apiRouter.post(
    "/people/import/{org_unit_id}",
    dependencies=[Depends(get_current_active_user)]
)
async def import_people(
    payload: list,
    org_unit_id: str,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_active_user),
):
    """
    Bulk import people (iHRIS compatible)
    """

    if not payload:
        raise HTTPException(status_code=400, detail="Empty payload")

    created = 0
    errors = []

    try:
        # 🔹 Get starting sequence ONCE
        maxNumber = await entity_map.getMaxNumber("person", session)

        for index, row in enumerate(payload):

            try:
                maxNumber += 1
                person_id = generate_unit_id(f"person|{maxNumber}", length=10)

                # =====================================================
                # PERSON
                # =====================================================
                p = row.get("person", {})

                new_person = HippoPerson(
                    id=person_id,
                    firstname=p.get("firstname"),
                    lastname=p.get("lastname"),
                    gender=p.get("gender"),
                    marital_status=p.get("marital_status"),
                    birthplace=p.get("birthplace"),
                    birthdate=parse_date(p.get("birthdate")),
                    recruitment_date=parse_date(p.get("recruitment_date")),
                    degree=p.get("degree"),
                    created_by=current_user_id,
                    last_modified= datetime.utcnow()
                )

                session.add(new_person)

                # =====================================================
                # IDENTIFICATION
                # =====================================================
                ident = row.get("identification", {})

                if ident and ident.get("number"):
                    session.add(
                        HippoPersonIdentification(
                            id=str(uuid.uuid4()),
                            person_id=person_id,
                            number=str(ident.get("number")),
                            created_by=current_user_id,
                            last_modified= datetime.utcnow()
                        )
                    )

                # =====================================================
                # EMPLOYMENT (IMPORTANT TABLE)
                # =====================================================
                emp = row.get("employment", {})

                if emp:
                    session.add(
                        HippoEmploymentStatusInfo(
                            id=str(uuid.uuid4()),
                            person_id=person_id,

                            grade=emp.get("grade"),
                            cadre=emp.get("job"),  # ⚠️ mapping job → cadre (adapt if needed)
                            classification=emp.get("classification"),
                            facility_id=org_unit_id,
                            job_type=emp.get("job_type"),
                            # employee_status=emp.get("current_position"),

                            seniority=emp.get("seniority", 0),
                            
                            employment_date=parse_date(emp.get("employment_date")),
                            start_service_date=parse_date(emp.get("start_service_date")),

                            created_by=current_user_id,
                            last_modified= datetime.utcnow()
                        )
                    )

                # =====================================================
                # ENTITY MAP
                # =====================================================
                session.add(
                    HippoEntityMap(
                        id=person_id,
                        entity_type="person",
                        max_number=maxNumber
                    )
                )

                # =====================================================
                # AUDIT
                # =====================================================
                session.add(
                    HippoAuditLog(
                        id=uuid.uuid4(),
                        user_id=current_user_id,
                        operation=f'import agent {person_id}'
                    )
                )

                created += 1

            except Exception as row_error:
                errors.append({
                    "index": index,
                    "error": str(row_error)
                })

        # 🔥 ONE COMMIT → FAST
        await session.commit()

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "created": created,
        "failed": len(errors),
        "errors": errors
    }