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
from manage.services.region import region
from manage.services.district import district
from manage.services.county import county
from manage.services.health_area import health_area
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

manageApiRouter = APIRouter()

manageApiRouter.include_router(degree.apiRouter, tags=["degrees"])
manageApiRouter.include_router(users.apiRouter, tags=["users"])
manageApiRouter.include_router(classification.apiRouter, tags=["classifications"])
manageApiRouter.include_router(role.apiRouter, tags=["roles"])
manageApiRouter.include_router(grade.apiRouter, tags=["grades"])
manageApiRouter.include_router(gender.apiRouter, tags=["genders"])
manageApiRouter.include_router(status.apiRouter, tags=["status"])
manageApiRouter.include_router(cadre.apiRouter, tags=["cadres"])
manageApiRouter.include_router(country.apiRouter, tags=["countries"])
manageApiRouter.include_router(region.apiRouter, tags=["regions"])
manageApiRouter.include_router(county.apiRouter, tags=["counties"])
manageApiRouter.include_router(district.apiRouter, tags=["districts"])
manageApiRouter.include_router(health_area.apiRouter, tags=["healthAreas"])
manageApiRouter.include_router(facility.apiRouter, tags=["facilities"])
manageApiRouter.include_router(facilityType.apiRouter, tags=["FacilityTypes"])
manageApiRouter.include_router(job_type.apiRouter, tags=["job_types"])
manageApiRouter.include_router(job_title.apiRouter, tags=["job_titles"])
manageApiRouter.include_router(salary_source.apiRouter, tags=["salary_sources"])
manageApiRouter.include_router(major.apiRouter, tags=["educational_majors"])
manageApiRouter.include_router(institution_type.apiRouter, tags=["institution_types"])
manageApiRouter.include_router(level.apiRouter, tags=["educational_levels"])
manageApiRouter.include_router(employment_status.apiRouter, tags=["employment_status"])
manageApiRouter.include_router(reason_departure.apiRouter, tags=["reason_departures"])
manageApiRouter.include_router(payment_frequency.apiRouter, tags=["reason_departures"])
manageApiRouter.include_router(marital_status.apiRouter, tags=["marital_status"])
manageApiRouter.include_router(units.apiRouter, tags=["organization_units"])
manageApiRouter.include_router(people.apiRouter, tags=["people"])
manageApiRouter.include_router(employment_info.apiRouter, tags=["employment_infos"])
manageApiRouter.include_router(passport.apiRouter, tags=["persion_passport"])
manageApiRouter.include_router(contact_type.apiRouter, tags=["contact_types"])
manageApiRouter.include_router(contact.apiRouter, tags=["contacts"])
manageApiRouter.include_router(identification_type.apiRouter, tags=["identification_types"])
manageApiRouter.include_router(identification.apiRouter, tags=["identifications"])
manageApiRouter.include_router(employment_status_report.apiRouter, tags=["employment_status_report"])
manageApiRouter.include_router(timesheet.apiRouter, tags=["timesheets"])
manageApiRouter.include_router(settings.apiRouter, tags=["settings"])
manageApiRouter.include_router(level.apiRouter, tags=["OrganizationLevels"])
manageApiRouter.include_router(dashboard.router, tags=["Dashboards"])
manageApiRouter.include_router(standards.apiRouter, tags=["Standars"])
manageApiRouter.include_router(organization_unit_type_api.apiRouter, tags=["OrgUnitType"])