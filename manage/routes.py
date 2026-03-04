from fastapi import APIRouter
from manage.services.degree import degree
from manage.services.user import users
from manage.services.classification import classification
from manage.services.role import role
from manage.services.grade import grade
from manage.services.gender import gender
from manage.services.employee_status import status
from manage.services.cadre import cadre
from manage.services.country import country
from manage.services.facility import facility
from manage.services.facility_type import type as facilityType
from manage.services.job_type import job_type
from manage.services.job_title import job_title
from manage.services.salary_source import salary_source
from manage.services.educational_major import major
from manage.services.educational_level import level
from manage.services.institution_type import institution_type
from manage.services.employment_status import employment_status
from manage.services.reason_departure import reason_departure
from manage.services.payment_frequency import payment_frequency
from manage.services.marital_status import marital_status
from manage.services.people import people
from manage.services.employment_status_info import employment_info
from manage.services.organization_units import units
from manage.services.passport import passport
from manage.services.contact_type import contact_type
from manage.services.contact import contact
from manage.services.identification_type import identification_type
from manage.services.identification import identification
from manage.services.reports import employment_status_report
from manage.services.timesheet import timesheet
from manage.services.settings import settings
from manage.services.organization_level import level
from manage.services.dashboard import dashboard
from manage.services.organization_unit_type import organization_unit_type_api
from manage.services.standards import standards
from manage.services.norms import norm
from manage.services.norms import norm_requirement
from manage.services.document_type import docment_type
from manage.services.document import document

router = APIRouter()

router.include_router(degree.apiRouter, tags=["degrees"])
router.include_router(users.apiRouter, tags=["users"])
router.include_router(classification.apiRouter, tags=["classifications"])
router.include_router(role.apiRouter, tags=["roles"])
router.include_router(grade.apiRouter, tags=["grades"])
router.include_router(gender.apiRouter, tags=["genders"])
router.include_router(status.apiRouter, tags=["status"])
router.include_router(cadre.apiRouter, tags=["cadres"])
router.include_router(country.apiRouter, tags=["countries"])
router.include_router(facility.apiRouter, tags=["facilities"])
router.include_router(facilityType.apiRouter, tags=["FacilityTypes"])
router.include_router(job_type.apiRouter, tags=["job_types"])
router.include_router(job_title.apiRouter, tags=["job_titles"])
router.include_router(salary_source.apiRouter, tags=["salary_sources"])
router.include_router(major.apiRouter, tags=["educational_majors"])
router.include_router(institution_type.apiRouter, tags=["institution_types"])
router.include_router(level.apiRouter, tags=["educational_levels"])
router.include_router(employment_status.apiRouter, tags=["employment_status"])
router.include_router(reason_departure.apiRouter, tags=["reason_departures"])
router.include_router(payment_frequency.apiRouter, tags=["reason_departures"])
router.include_router(marital_status.apiRouter, tags=["marital_status"])
router.include_router(units.apiRouter, tags=["organization_units"])
router.include_router(people.apiRouter, tags=["people"])
router.include_router(employment_info.apiRouter, tags=["employment_infos"])
router.include_router(passport.apiRouter, tags=["persion_passport"])
router.include_router(contact_type.apiRouter, tags=["contact_types"])
router.include_router(contact.apiRouter, tags=["contacts"])
router.include_router(identification_type.apiRouter, tags=["identification_types"])
router.include_router(identification.apiRouter, tags=["identifications"])
router.include_router(employment_status_report.apiRouter, tags=["employment_status_report"])
router.include_router(timesheet.apiRouter, tags=["timesheets"])
router.include_router(settings.apiRouter, tags=["settings"])
router.include_router(level.apiRouter, tags=["OrganizationLevels"])
router.include_router(dashboard.router, tags=["Dashboards"])
router.include_router(standards.apiRouter, tags=["Standars"])
router.include_router(organization_unit_type_api.apiRouter, tags=["OrgUnitType"])
router.include_router(norm.apiRouter, tags=["Norms"])
router.include_router(norm_requirement.APIRouter, tags=["Norm Requirements"])
router.include_router(docment_type.apiRouter, tags=["Document type"])
router.include_router(document.apiRouter, tags=["Document"])