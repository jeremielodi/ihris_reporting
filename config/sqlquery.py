import fastapi


def get_timesheet_query(datestr: str):

    subquery = f" order by hippo_person_timesheet.created desc  limit 145018"
    if datestr != '':
        subquery = f" where date(hippo_person_timesheet.created) >= '{datestr}' order by hippo_person_timesheet.created asc  limit 4000"

    return timesheet_query + subquery


timesheet_query = """
    select  distinct
    CONVERT(hippo_person_timesheet.id, char(200)) as id , 
    CONVERT( hippo_person_timesheet.created, char(200)) as created , 
    CONVERT( hippo_person_timesheet.parent, char(200)) as parent,
    upper(trim(CONVERT( 
    CONCAT(COALESCE(hippo_person.firstname,"")," ", COALESCE(hippo_person.surname,"")," ", COALESCE(hippo_person.othername,"")) , CHAR(200)))) as fullname,
    CONVERT( cast(
    substring(hippo_person_timesheet.salaire_recu, position('=' in hippo_person_timesheet.salaire_recu ) + 1, length(hippo_person_timesheet.salaire_recu))
    as decimal(12)
    ), char(200)) as 'salaire_recu',
    CONVERT( cast(
    substring(hippo_person_timesheet.prime_risque, position('=' in hippo_person_timesheet.prime_risque ) + 1, length(hippo_person_timesheet.prime_risque))
        as decimal(12)
    ), char(200)) as 'prime_risque' ,
    CONVERT( cast(
    substring(hippo_person_timesheet.prime_locale, position('=' in hippo_person_timesheet.prime_locale ) + 1, length(hippo_person_timesheet.prime_locale))
    as decimal(12)
    ), char(200)) as 'prime_locale',
    CONVERT(	cast(
    substring(hippo_person_timesheet.prime_ptf, position('=' in hippo_person_timesheet.prime_ptf ) + 1, length(hippo_person_timesheet.prime_ptf))
    as decimal(12)
    ), char(200)) as 'prime_ptf' 
    ,
        CONVERT( hippo_person_timesheet.jours_prestes,char(200)) as jours_prestes,
        CONVERT(  hippo_person_timesheet.mois_annee, char(200)) as mois_annee,
        CONVERT(hippo_employment_status_rdc.cadre, char(200)) as cadre,
        CONVERT(hippo_employment_status_rdc.job, char(200) )as job,
        CONVERT(hippo_employment_status_rdc.prime, char(20))as prime,
         CONVERT(hippo_employment_status_rdc.salaire, char(20))as salaire,

        CONVERT(hippo_employment_status_rdc.classification, char(200)) as classification,
        CONVERT(hippo_employment_status_rdc.salary_grade, char(200)) as salary_grade,
        CONVERT(hippo_facility.id, char(200)) as  facility,
        CONVERT(hippo_facility.name, char(200)) as  facility_name,
        CONVERT(hippo_health_area.id, char(200))as  health_area,
        CONVERT(hippo_health_area.name, char(200)) as  health_area_name,
        CONVERT(hippo_county.id , char(200)) as county,
        CONVERT(hippo_county.name, char(200))as county_name,
        CONVERT(hippo_county.district, char(200)) as  district,
        CONVERT(hippo_district.name, char(200)) as  district_name
        
    from  
        ihris_mig.hippo_person_timesheet 
        join hippo_employment_status_rdc  on  hippo_employment_status_rdc.parent  =  hippo_person_timesheet.parent 
        left join hippo_facility on hippo_facility.id  =  hippo_employment_status_rdc.facility
        left join  hippo_health_area on hippo_health_area.id =  hippo_facility.location
        left join hippo_county on hippo_county.id = hippo_health_area.county
        left join hippo_district on hippo_district.id = hippo_county.district
        left join hippo_person on hippo_person.id = hippo_person_timesheet.parent
"""

def person_file_query(id ):
   a =   f"""
    select * FROM z_employment_status_view Where id = '{id}'
    """
   return a

def person_file_employments(id):
    q = f"""
        select *
        FROM hippo_employment_status_info
        where person_id= '{id }'
        ORDER BY created asc
    """
    return q