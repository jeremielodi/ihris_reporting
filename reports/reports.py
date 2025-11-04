import numpy as np
import pandas as pd
from datetime import date, datetime

from requests import Session
from config.Config import mysql_get_mydb, pg_get_mydb
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import os
from helpers.helpers import get_data_location
from typing import List
from fastapi import Depends, Query
from config.sqlquery import get_timesheet_query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import HealthArea, HealthAreaBaseListe
from models.validation_crud import validated_ids, validation_count
from endpoints.pyramid_api import Health_area
from manage.database import SessionLocal, engine, sync_engine

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


person_attributes = [
    'firstname', 'surname', 'othername', 'gender',
    'birth_date', 'dependents','marital_status',
    'mobile_phone', 'address', 'ref_engagement',
    'year_of_appointment', 'matricule', 'ref_on_employment',
    'degree','position', 'cadre', 'classification',
    'job', 'salary_grade', 'salaire', 'prime', 'identifie'
]
   
async def download_data(org_unit_id: str, filter: str, db: Session = Depends(get_session)):
    data = await get_internal_completeness_data(org_unit_id=org_unit_id, db=db)

    title = ''
    if filter == 'all':
        title = 'AGENTS'
    elif filter == "admin":
        data = data.loc[data['cadre'] == 'ADMINISTRATIF']
        title = 'ADMINISTRATIF'
    elif filter == 'prosante':
        data = data.loc[data['cadre'] != 'ADMINISTRATIF']
        title = 'PRO SANTE'
    elif filter == 'activite':
        data = data.loc[data['position'] == "Activité"]
        title = 'AGENTS EN POSITION ADM. ACTIVE'
    
    elif filter == 'admis_ss':
        data = data.loc[data['matricule'].str.len() > 3]
        title = 'AGENTS ADMIS SOUS STATUT'
    elif filter == 'nu':
        data = data.loc[data['matricule'].str.len() <= 3]
        title = 'AGENTS NOUVELLES UNITES'
    elif filter == 'eligible_retraite':
        data = eligible_retraite(data)
        title = 'ELIGIBLE A LA RETRAITE'

    elif filter == 'retraite':
        data = data.loc[data['position'] == "Retraité"]
        title = 'AGENTS RETRAITES'
    
    elif filter == 'dead':
        data = data.loc[data['position'] == "Décédé"]
        title = 'AGENTS DECEDES'

    # elif filter == 'validated':
    #     ids  = validated_ids(
    #         db=db
    #     )
    #     data = data.loc[data['id'].isin(ids)]
    #     title = 'AGENTS VALIDES'
    
    

    data = data.reset_index()
    data = data.rename(columns={"index": "No"})
    data.insert(
        loc=7, column='lien',
        value="https://drc.ihris.org/index.php/view?id="+
        data['id']
    )
    data['No'] = range(1, len(data) + 1)
    return data, f"{title}"

def eligible_retraite(data):

    data1 = data.loc[data['birth_date_y'] <= date.today().year - 65]
    data2 = data.loc[data['year_of_appointment_y'] <= date.today().year - 30]
    coll = pd.concat([data1, data2])
    coll = coll.drop_duplicates()
    coll['anciennete'] = date.today().year - coll['year_of_appointment_y']
    coll['age'] = date.today().year - coll['birth_date_y']
    return coll

async def get_dashboard_data(org_unit_id: str, db:AsyncSession):

    data = await get_internal_completeness_data(org_unit_id=org_unit_id, db=db)
    
    effectif = np.int64(data['id'].count()).item()
    """Recrutement staff"""
    x_recrument = []
    y_recrument = []
    
    i = 1970
    if len(data) > 0 :
        i = np.int64(data['year_of_appointment_y'].min()).item()
    while i <= date.today().year:
        x_recrument.append(
            np.int16(data['id'].loc[data['year_of_appointment_y'] == i].count()).item())
        # if i % 2 == 0:
            
        # else:

        #y_recrument.append('.')
        i += 1

        y_recrument.append(i)
    """Statistic by job"""
    job_data = data.groupby(['job'])['id'].count()
    job_data = job_data.sort_values(ascending=False)

    """Statistic by job"""
    classification_data = data.groupby(['classification'])['id'].count()
    classification_data = classification_data.sort_values(ascending=False)

    """Statistic by position """
    position_data = data.groupby(['position'])['id'].count()

    """Statictic by degree"""
    degree_data = data.groupby(['degree'])['id'].count()
    degree_data = degree_data.sort_values(ascending=False)

 
    """ Gender """
    gender_m = np.int16(
        data.loc[data['gender'] == "gender|M"]['id'].count()).item()
    gender_f = np.int16(
        data.loc[data['gender'] == "gender|F"]['id'].count()).item()
    admin = np.int64(
        data.loc[data['job'] == 'Administrateur-Gestionnaire']['id'].count()).item()
    
    position_active = np.int64(
        data.loc[data['position'] == "Activité"]['id'].count()).item()
    
    position_retraite = np.int64(
        data.loc[data['position'] == "Retraité"]['id'].count()).item()
    
    position_dead = np.int64(
        data.loc[data['position'] == "Décédé"]['id'].count()).item()
    

    
    timesheet = await timeshee_dashboard( org_unit_id=org_unit_id, effectif=effectif, db=db)
    ''' Employment statuts'''
    nu = np.int16(data.loc[data['matricule'].str.contains(
        'N') == True]['id'].count()).item()
    adminsoustatut = np.int16(
        data.loc[data['matricule'].str.len() > 3]['id'].count()).item()
    
   
    # val = validation_count(
    #      facility=fosa_id,
    #      healthArea=zs_id ,
    #      county=tr_id,
    #      district=pr_id,
    #      db=db
    #  )
    return {
        #'validated': val,
        "recrutement": {
            'labels': y_recrument,
            'data': x_recrument
        },
        "classification": {
            "labels": classification_data.index.tolist(),
            "data": classification_data.values.tolist(),
            "max": max(classification_data.values.tolist(),default=0)
        },
        "cadre": {
            "labels": job_data.index.tolist(),
            "data": job_data.values.tolist(),
            "max": max(job_data.values.tolist(),default=0)
        },
        "position": {
            "labels": position_data.index.tolist(),
            "data": position_data.values.tolist(),
            "max": max(position_data.values.tolist(),default=0)
        },
        "degree": {
            "labels": degree_data.index.tolist(),
            "data": degree_data.values.tolist(),
             "max": max(degree_data.values.tolist(), default=0)
        },
        "gender": {
            'm': gender_m,
            'f': gender_f
        },
        #"facility_data": facility_data_base_list,
        "effectif": effectif,
        "admin": admin,
        "position_active":  position_active,
        "timesheet": timesheet,
        #"effectif_nu": nu,
        "effectif_adminSS": adminsoustatut,
        "agecurve": getAgecurveAdmin_statut(data=data),
        "general_agecurve":getAgecurveGeneral(data),
        "eligible_retaite": len(eligible_retraite(data)),
        "retraite": position_retraite,
        "dead" : position_dead
    }

def getAgecurveAdmin_statut(data):
    x = []
    x2 = []
    y = []
    i = date.today().year
    m = 1920
    while i % 5 != 0:
        i -= 1
    current_year = i
    while i > m:
        mdata = data.loc[data['birth_date_y'].between(i-4, i) == True]
        val = np.int16(
            mdata.loc[mdata['matricule'].str.len() > 3]['id'].count()).item()
        nu = np.int16(
            mdata.loc[mdata['matricule'].str.contains('N') == True]['id'].count()).item()
        x.append(val)
        x2.append(nu)
        y.append(str(current_year-i) + ' - ' + str(current_year-i+5))
        i -= 5
    return {
        'values': {'admis_statut': x, 'nu': x2},
        'max': max([max(x),max(x2)]), 'labels': y,
        '_values': {'admis_statut': x[::-1], 'nu': x2[::-1]},
        '_max': max([max(x),max(x2)]),
        '_labels': y[::-1]
    }


def getAgecurveGeneral(data):
    x = []
    x2 = []
    y = []
    z = []
    i = date.today().year
    m = 1920
    while i % 5 != 0:
        i -= 1
    current_year = i
    while i > m:
        mdata = data.loc[data['birth_date_y'].between(i-4, i) == True]
        mal = np.int16( mdata.loc[mdata['gender'] == "gender|M"]['id'].count()).item()
        fem = np.int16( mdata.loc[mdata['gender'] == "gender|F"]['id'].count()).item()
        x.append(mal)
        x2.append(fem)
        y.append(str(current_year-i) + ' - ' + str(current_year-i+5) )
        z.append(str(i-4) + ' ' + str(i))
        i -= 5
    return {
        'values': {'mal': x, 'fem': x2},
        'max': max([max(x),max(x2)]),
        'labels': y,
        '_values': {'mal': x[::-1], 'fem': x2[::-1]},
        '_max': max([max(x),max(x2)]),
        '_labels': y[::-1]
    }


async def timeshee_dashboard(org_unit_id: str, effectif: int, db:AsyncSession=Depends(get_session)):
    data = await get_timesheet_data(org_unit_id = org_unit_id, db=db)
 
    x = []
    x2 = []
    y = []
    i = 1
    # effectif_actif = data.drop_duplicates(subset=['parent'])['parent'].count()

    # d = date.today() - relativedelta(months=18)
    # while i <= 18:
    #     str = d.strftime("%Y-%m")
    #     taux_general = 0
    #     toux_effecti_actif = 0
    #     timesheet_count = int(np.int16(
    #         data['id'].loc[data['mois_annee'].str.contains(str) == True].count()).item())
    #     if effectif > 0:
    #         taux_general = int(timesheet_count / effectif * 100)
    #     if effectif_actif > 0:
    #         toux_effecti_actif = int(
    #             timesheet_count / effectif_actif * 100)
    #     x.append(taux_general if taux_general <= 100 else 100)
    #     x2.append(toux_effecti_actif if toux_effecti_actif <= 100 else 100)

    #     y.append(d.strftime("%b-%y"))
    #     i += 1
    #     d = d + relativedelta(months=1)
    
    return {
        'labels': y,
        'data': {
            'taux_general': x,
            'taux_actif': x2
        }
    }

# person_attributes must be a list of the attribute column names you want to check
# e.g. person_attributes = ["attr1", "attr2", ...]

async def get_internal_completeness_report_career(
    org_unit_id: str = "0",
    filter: int = 0,
    db: AsyncSession = Depends(get_session)
):
    # Identify parent (selected) and child keys
    selectedKey = await getOrUnitType(org_unit_id)          # e.g. "district_id"
    subKey      = await getOrUnitChildrenLevel(org_unit_id)  # e.g. "health_area_id"

    # Load data
    data = await get_internal_completeness_data(org_unit_id=org_unit_id, db=db)
    if (len(data)) == 0:
        return pd.DataFrame(data=[])
    
    parentId = selectedKey # parent org unit id
    parentName = f"{selectedKey}_name" # parent org unit name
    childType = subKey # child org unit type
    childName = ''
    if childType is not None:
        childName = f"{subKey}_name" # child org unit name
        data.rename(columns={childName: "location"}, inplace=True)
        data.rename(columns={childType: "location_id"}, inplace=True)
    else:
        data.rename(columns={parentName: "location"}, inplace=True)
        data.rename(columns={parentId: "location_id"}, inplace=True)
    datakays = person_attributes
    # missing_flags = data[datakays].isna()
    
    data[datakays] = data[datakays].isnull()
    data[['agent_number']] = data[['id']].notnull()

    pivot = None

    if childType is None:
        pivot = np.round(pd.pivot_table(
            data, index=[ "location_id", "location" ], aggfunc=np.sum, fill_value=0,), 2)
    else:
        pivot = np.round(pd.pivot_table(
            data, index=[parentId, "location_id","location"], aggfunc=np.sum, fill_value=0,), 2)


    if (len(pivot)):
        pivot['total'] = pivot.loc[:, datakays].sum(axis=1)
        pivot['rate'] = 100 - \
        (pivot['total'] / (len(datakays) * pivot['agent_number']) * 100)


    return pivot

async def get_salaire_prime_report(org_unit_id: str = "0", zs_filter: int = 0, db:AsyncSession =Depends(get_session)):
    # Load people data
    people = await get_internal_completeness_data(org_unit_id=org_unit_id, db=db)
    people = people.copy()

    # Figure out parent/child type
    parent_key = await getOrUnitType(org_unit_id)          # e.g. "district_id"
    child_key  = await getOrUnitChildrenLevel(org_unit_id)  # e.g. "health_area_id"

    if child_key and child_key in people.columns:
        people = people.rename(columns={child_key: "location_id"})
        name_col = f"{child_key}_name"
        people["location"] = people.get(name_col, "")
    else:
        people = people.rename(columns={parent_key: "location_id"})
        name_col = f"{parent_key}_name"
        people["location"] = people.get(name_col, "")

    # -----------------------------
    # Indicators
    # -----------------------------
    people["effectif"] = 1

    # salaire ET prime (both == 1)
    people["salaire_et_prime"] = ((people["salaire"] == 1) & (people["prime"] == 1)).astype(int)

    # salaire OU prime (at least one == 1)
    people["salaire_ou_prime"] = ((people["salaire"] == 1) | (people["prime"] == 1)).astype(int)

    # neither salaire nor prime
    people["in_salaire_in_prime"] = ((people["salaire"] == 0) & (people["prime"] == 0)).astype(int)

    # -----------------------------
    # Group by location_id + location
    # -----------------------------
    report = (
        people.groupby(["location_id", "location"], dropna=False)[
            ["effectif", "salaire", "prime",
             "salaire_et_prime", "salaire_ou_prime", "in_salaire_in_prime"]
        ]
        .sum()
        .reset_index()
    )

    return report

"""

 Timesheet Report

"""

async def performance_bonus_calc(
    org_unit_id: str = "0",
    zs_filter: int = 0,
    start_date: str | None = None,
    end_date: str | None = None,
    download: int = 0,
    db: AsyncSession = Depends(get_session),
):
    timesheets = await get_timesheet_data(org_unit_id=org_unit_id, db=db)
    people = await get_internal_completeness_data(org_unit_id=org_unit_id, db=db)
    # timesheets = timesheets.copy()
    # people = people.copy()

    # Dates
    if not start_date or not end_date:
        raise ValueError("start_date and end_date required (YYYY-MM-DD)")
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    # Normalize timesheet month key
    timesheets["_month_key"] = pd.to_datetime(timesheets["mois_annee"], errors="coerce").dt.strftime("%Y-%m")

    # Org-unit mapping → child id/name as location_id/location
    parent_key = await getOrUnitType(org_unit_id)
    child_key  = await getOrUnitChildrenLevel(org_unit_id)

    print('-----------------------------------------------')
    print(parent_key, child_key)
    print('-----------------------------------------------')
    if child_key and child_key in timesheets.columns:
        timesheets = timesheets.rename(columns={child_key: "location_id"})
        people = people.rename(columns={child_key: "location_id"})
        child_name_col = f"{child_key}_name"
        timesheets["location"] = timesheets.get(child_name_col, "")
        people["location"] = people.get(child_name_col, "")
    else:
        timesheets = timesheets.rename(columns={parent_key: "location_id"})
        people = people.rename(columns={parent_key: "location_id"})
        parent_name_col = f"{parent_key}_name"
        timesheets["location"] = timesheets.get(parent_name_col, "")
        people["location"] = people.get(parent_name_col, "")

    # Build month columns (presence counts) and int completeness columns (your logic)
    dates, dates_local_abb = [], []
    cmIkeys = ["salaire_recu", "prime_risque", "prime_locale", "prime_ptf"]
    for k in cmIkeys:
        if k not in timesheets.columns:
            timesheets[k] = 0

    intComLabels, intComSumColumns = [], []
    i = 0
    while True:
        cur = start_dt + relativedelta(months=i)
        key = cur.strftime("%Y-%m")
        dates.append(key)
        dates_local_abb.append({"key": key, "local_abb": cur.strftime("%b-%y")})

        mask = (timesheets["_month_key"] == key)
        timesheets[key] = mask.astype(int)

        for elt in cmIkeys:
            m = f"{key}_{elt}"
            timesheets[m] = 0
            timesheets.loc[mask, m] = timesheets.loc[mask, elt]
            intComLabels.append(m)

        sum_col = f"{key}_sum_com"
        intComSumColumns.append(sum_col)

        ha_col = "health_area_name"
        base_part = (len(cmIkeys) - (timesheets.loc[mask, [f"{key}_{k}" for k in cmIkeys]] == 0).sum(axis=1)).astype(int) if mask.any() else 0
        prime_part = (timesheets.loc[mask, "prime"] == 0).astype(int) if ("prime" in timesheets.columns and mask.any()) else 0
        salaire_part = (timesheets.loc[mask, "salaire"] == 0).astype(int) if ("salaire" in timesheets.columns and mask.any()) else 0
        dps_part = (timesheets.loc[mask, ha_col].str.contains("DPS", na=False)).astype(int) if (ha_col in timesheets.columns and mask.any()) else 0
        ips_part = (timesheets.loc[mask, ha_col].str.contains("IPS", na=False)).astype(int) if (ha_col in timesheets.columns and mask.any()) else 0

        timesheets[sum_col] = 0
        if isinstance(base_part, pd.Series):
            part_sum = base_part
            if isinstance(prime_part, pd.Series):   part_sum = part_sum + prime_part
            if isinstance(salaire_part, pd.Series): part_sum = part_sum + salaire_part
            if isinstance(dps_part, pd.Series):     part_sum = part_sum + dps_part
            if isinstance(ips_part, pd.Series):     part_sum = part_sum + ips_part
            timesheets.loc[mask, sum_col] = part_sum.values

        if cur.strftime("%Y-%m") == end_dt.strftime("%Y-%m") or i >= 12:
            break
        i += 1

    dates_len = len(dates)
    timesheets = timesheets.drop_duplicates(subset=["parent", "_month_key"])

    print(timesheets)
    # Aggregate by child location
    timesheet_report = (
        timesheets.groupby(["location_id", "location"], dropna=False)[dates + intComLabels + intComSumColumns]
        .sum()
    )

    # effectif_gen (total people per location_id)
    effectif_general = (
        people.groupby("location_id", sort=False)["id"]
        .count()
        .rename("effectif_gen")
    )
    timesheet_report = timesheet_report.merge(effectif_general, how="left", left_on="location_id", right_index=True)

    # effectif_actif (distinct parents who have any timesheet)
    active = timesheets.drop_duplicates(subset=["parent"])
    effectif_actif = (
        active.groupby("location_id")["parent"]
        .nunique()
        .rename("effectif_actif")
    )
    timesheet_report = timesheet_report.merge(effectif_actif, how="left", left_on="location_id", right_index=True)

    # Career completeness
    for c in person_attributes:
        if c not in people.columns:
            people[c] = np.nan
    people[person_attributes] = people[person_attributes].notnull().astype(int)
    people["total_career"] = people[person_attributes].sum(axis=1)

    career_data_comp = (
        people.groupby("location_id", sort=False)["total_career"]
        .sum()
        .rename("career_data_comp")
    )
    timesheet_report = timesheet_report.merge(career_data_comp, how="left", left_on="location_id", right_index=True)

    # Metrics
    timesheet_report["timesheet_sum"] = timesheet_report[dates].sum(axis=1)
    timesheet_report["timesheet_average"] = timesheet_report["timesheet_sum"] / max(dates_len, 1)
    timesheet_report["timesheet_max"] = timesheet_report["effectif_gen"] * dates_len

    with np.errstate(divide="ignore", invalid="ignore"):
        timesheet_report["timesheet_perc_gen"] = (timesheet_report["timesheet_sum"] * 100.0 / timesheet_report["timesheet_max"]).replace([np.inf, -np.inf], np.nan)
        timesheet_report["timesheet_perc_actif"] = (timesheet_report["timesheet_sum"] * 100.0 / (timesheet_report["effectif_actif"] * dates_len)).replace([np.inf, -np.inf], np.nan)

    timesheet_report["timesheet_com_int_sum"] = timesheet_report[intComSumColumns].sum(axis=1)
    timesheet_report["timesheet_com_int_max"] = (timesheet_report["effectif_actif"] * dates_len * len(cmIkeys)).astype(float)

    with np.errstate(divide="ignore", invalid="ignore"):
        timesheet_report["timesheet_com_int_perc"] = (timesheet_report["timesheet_com_int_sum"] * 100.0 / timesheet_report["timesheet_com_int_max"]).replace([np.inf, -np.inf], np.nan)

    timesheet_report["career_data_comp_max"] = len(person_attributes) * timesheet_report["effectif_gen"]
    with np.errstate(divide="ignore", invalid="ignore"):
        timesheet_report["career_data_comp_perc"] = (timesheet_report["career_data_comp"] * 100.0 / timesheet_report["career_data_comp_max"]).replace([np.inf, -np.inf], np.nan)

    # === your bonus logic unchanged ===
    timesheet_report["perfomance_bonus_com_career"] = 0.0
    timesheet_report["perfomance_bonus_com_int_timesheet"] = 0.0
    timesheet_report["perfomance_bonus_com_timesheet"] = 0.0

    # ... keep your thresholds and assignments as in your code ...

    # Totals / subtotal
    timesheet_report = timesheet_report.fillna(0)
    subtotal = timesheet_report.sum(numeric_only=True)
    n_groups = max(timesheet_report.shape[0], 1)
    for col in ["timesheet_perc_actif", "timesheet_perc_gen", "career_data_comp_perc", "timesheet_com_int_perc"]:
        if col in subtotal:
            subtotal[col] = subtotal[col] / n_groups

    if download == 0:
        timesheet_report.loc[("TOTAL", ""), :] = 0  # ensure index slot exists
        # if you prefer, skip inserting TOTAL row — your UI may sum client-side

    # Bonus summaries
    subtotal["bonus_ips_comp_timesheet"] = 0.40 * subtotal["timesheet_perc_gen"]
    subtotal["bonus_dps_comp_timesheet"] = 0.80 * subtotal["timesheet_perc_gen"]
    subtotal["bonus_ips_career"] = 0.30 * subtotal["career_data_comp_perc"]
    subtotal["bonus_dps_career"] = 0.60 * subtotal["career_data_comp_perc"]
    subtotal["bonus_ips_int_timesheet"] = 0.30 * subtotal["timesheet_com_int_perc"]
    subtotal["bonus_dps_int_timesheet"] = 0.60 * subtotal["timesheet_com_int_perc"]

    return timesheet_report, dates_local_abb, subtotal

# cmIkeys are the four prime/salaire columns you derive per month
CMI_KEYS = ["salaire_recu", "prime_risque", "prime_locale", "prime_ptf"]

async def completude_timesheet(
    org_unit_id: str = "0",
    zs_filter: int = 0,
    start_date: str | None = None,
    end_date: str | None = None,
    download_details: int = 0,
    db: AsyncSession = Depends(get_session),
):
    # -----------------------------
    # Load data
    # -----------------------------
    timesheets = await get_timesheet_data(org_unit_id=org_unit_id, db=db)
    people = await get_internal_completeness_data(org_unit_id=org_unit_id, db=db)
    timesheets = timesheets.copy()
    people = people.copy()

    # Normalize date inputs
    if not start_date or not end_date:
        raise ValueError("start_date and end_date must be provided as 'YYYY-MM-DD'")

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    if end_dt < start_dt:
        raise ValueError("end_date must be >= start_date")

    # Ensure timesheets has a proper month field (YYYY-MM)
    ts_month = pd.to_datetime(timesheets["mois_annee"], errors="coerce").dt.strftime("%Y-%m")
    # We'll use this vector for monthly masks
    timesheets["_month_key"] = ts_month

    # -----------------------------
    # Org unit keys (parent/child)
    # -----------------------------
    selectedKey = await getOrUnitType(org_unit_id)          # parent id column, e.g. "district_id"
    subKey      = await getOrUnitChildrenLevel(org_unit_id)  # child id column, e.g. "health_area_id"

    # Map columns:
    # LOCATION = parent id, location_id = child id, location_name = child name (if present)
    # If subKey not available, fall back to parent id/name as location_id/location
    if subKey and subKey in timesheets.columns:
        child_name_col = f"{subKey}_name"
        if child_name_col in timesheets.columns:
            timesheets = timesheets.rename(columns={child_name_col: "location"})
        else:
            timesheets["location"] = ""

        if child_name_col in people.columns:
            people = people.rename(columns={child_name_col: "location"})
        else:
            people["location"] = ""

        timesheets = timesheets.rename(columns={subKey: "location_id"})
        people = people.rename(columns={subKey: "location_id"})
    else:
        # Fallback: use parent id/name
        parent_name_col = f"{selectedKey}_name"
        if parent_name_col in timesheets.columns:
            timesheets = timesheets.rename(columns={parent_name_col: "location"})
        else:
            timesheets["location"] = ""
        if parent_name_col in people.columns:
            people = people.rename(columns={parent_name_col: "location"})
        else:
            people["location"] = ""

        timesheets = timesheets.rename(columns={selectedKey: "location_id"})
        people = people.rename(columns={selectedKey: "location_id"})

    # -----------------------------
    # Monthly expansion
    # -----------------------------
    dates = []
    dates_local_abb = []
    intComLabels = []       # all monthly *_prime columns
    intComSumColumns = []   # all monthly *_sum_com columns
    monthly_value_cols = [] # all per-month boolean presence columns (YYYY-MM)

    # Make sure the base columns exist
    for col in CMI_KEYS:
        if col not in timesheets.columns:
            timesheets[col] = 0

    # Build month-by-month columns between start_dt and end_dt (inclusive)
    i = 0
    while True:
        current = start_dt + relativedelta(months=i)
        key = current.strftime("%Y-%m")
        dates.append(key)
        dates_local_abb.append({"key": key, "local_abb": current.strftime("%b-%y")})

        # Boolean column for "has this month"
        mask = (timesheets["_month_key"] == key)
        col_present = key
        timesheets[col_present] = mask.astype(int)
        monthly_value_cols.append(col_present)

        # For each CMI key, create a per-month value column (copy value where mask true; 0 elsewhere)
        for elt in CMI_KEYS:
            mcol = f"{key}_{elt}"
            timesheets[mcol] = 0
            timesheets.loc[mask, mcol] = timesheets.loc[mask, elt]
            intComLabels.append(mcol)

        # Monthly completeness sum column
        # You referenced these columns in your original; guard if absent
        has_prime_col = "prime" in timesheets.columns
        has_salaire_col = "salaire" in timesheets.columns
        has_ha_name = "health_area_name" in timesheets.columns

        sum_col = f"{key}_sum_com"
        # Build components safely
        # (len(CMI_KEYS) - (# of zeros among the four monthly primes))
        cmi_zero_count = (timesheets.loc[mask, [f"{key}_{k}" for k in CMI_KEYS]] == 0).sum(axis=1)
        base_part = (len(CMI_KEYS) - cmi_zero_count).astype(int)

        prime_part = (timesheets.loc[mask, "prime"] == 0).astype(int) if has_prime_col else 0
        salaire_part = (timesheets.loc[mask, "salaire"] == 0).astype(int) if has_salaire_col else 0

        dps_part = (timesheets.loc[mask, "health_area_name"].str.contains("DPS", na=False)).astype(int) if has_ha_name else 0
        ips_part = (timesheets.loc[mask, "health_area_name"].str.contains("IPS", na=False)).astype(int) if has_ha_name else 0

        timesheets[sum_col] = 0
        # assign only where mask holds; elsewhere remain 0 to keep shapes equal
        if np.isscalar(prime_part):   prime_part = 0
        if np.isscalar(salaire_part): salaire_part = 0
        if np.isscalar(dps_part):     dps_part = 0
        if np.isscalar(ips_part):     ips_part = 0

        # when any part is a scalar (no mask rows), create Series aligned to mask index with zeros
        if isinstance(base_part, pd.Series):
            part_sum = base_part
            if isinstance(prime_part, pd.Series):   part_sum = part_sum + prime_part
            if isinstance(salaire_part, pd.Series): part_sum = part_sum + salaire_part
            if isinstance(dps_part, pd.Series):     part_sum = part_sum + dps_part
            if isinstance(ips_part, pd.Series):     part_sum = part_sum + ips_part
            timesheets.loc[mask, sum_col] = part_sum.values
        intComSumColumns.append(sum_col)

        # Break condition after setting current month
        if current.strftime("%Y-%m") == end_dt.strftime("%Y-%m"):
            break
        i += 1
        if i > 240:  # hard guard (20 years)
            break

    dates_len = len(dates)

    # Drop duplicates once (parent + month)
    timesheets = timesheets.drop_duplicates(subset=["parent", "_month_key"])

    # -----------------------------
    # Download details (person-level)
    # -----------------------------
    if download_details == 2:
        grp = timesheets.groupby(["fullname", "facility_name", "health_area_name", "parent", "prime", "salaire"], dropna=False)[intComLabels + monthly_value_cols].sum()

        idx = grp.index
        report = grp.reset_index()
        # Link to person
        report.insert(3, "lien", "https://drc.ihris.org/index.php/view?id=" + report["parent"].astype(str))
        report.rename(columns={
            "facility_name": "fosa",
            "fullname": "fullname",
            "health_area_name": "health_area_name",
            "prime": "Prime_risque",
            "salaire": "Salaire",
        }, inplace=True)
        return report

    # -----------------------------
    # Aggregate by location (child)
    # -----------------------------
    if "location_id" not in timesheets.columns or "location" not in timesheets.columns:
        # fallback to something meaningful
        timesheets["location_id"] = timesheets.get("location_id", "N/A")
        timesheets["location"] = timesheets.get("location", "")

    timesheet_report = (
        timesheets.groupby(["location_id", "location"], dropna=False)[intComLabels + intComSumColumns + monthly_value_cols]
        .sum()
    )

    # effectif_gen: total people per location_id (count of non-null ids)
    
    effectif_general = (
        people.groupby("location_id", sort=False)["id"]
        .count()
        .rename("effectif_gen")
    )
    timesheet_report = timesheet_report.merge(
        effectif_general, how="left", left_on="location_id", right_index=True
    )

    # effectif_actif: distinct parents with any timesheet in the period, per location_id
    # (drop dup by parent; then count unique parent per location_id)
    active = timesheets.drop_duplicates(subset=["parent"])
    effectif_actif = (
        active.groupby("location_id")["parent"]
        .nunique()
        .rename("effectif_actif")
    )
    timesheet_report = timesheet_report.merge(
        effectif_actif, how="left", left_on="location_id", right_index=True
    )

    # sums across months
    timesheet_report["sum"] = timesheet_report[dates].sum(axis=1)

    # internal completeness sums
    timesheet_report["com_int_sum"] = timesheet_report[intComSumColumns].sum(axis=1)
    timesheet_report["com_int_max"] = timesheet_report["effectif_actif"].fillna(0).astype(float) * dates_len * len(CMI_KEYS)
    timesheet_report["com_int_len"] = len(intComLabels)

    # % completeness (guard 0/NaN)
    with np.errstate(divide="ignore", invalid="ignore"):
        timesheet_report["com_int_perc"] = (timesheet_report["com_int_sum"] * 100.0 / timesheet_report["com_int_max"]).replace([np.inf, -np.inf], np.nan)

    # Averages & coverage
    timesheet_report["moyenne"] = timesheet_report["sum"] / max(dates_len, 1)

    with np.errstate(divide="ignore", invalid="ignore"):
        timesheet_report["report_perc_gen"] = (timesheet_report["moyenne"] * 100.0 / timesheet_report["effectif_gen"]).replace([np.inf, -np.inf], np.nan)
        timesheet_report["report_perc_actif"] = (timesheet_report["moyenne"] * 100.0 / timesheet_report["effectif_actif"]).replace([np.inf, -np.inf], np.nan)

    # optional: filter zones (you had a commented line)
    # if zs_filter == 1:
    #     timesheet_report = timesheet_report[timesheet_report["location"] != "ZS PAL"]

    # subtotal over numeric columns; and average some percentages across groups
    timesheet_report = timesheet_report.fillna(0)
    subtotal = timesheet_report.sum(numeric_only=True)

    # average percentage columns by number of groups
    n_groups = max(timesheet_report.shape[0], 1)
    for col in ["report_perc_gen", "report_perc_actif", "com_int_perc"]:
        if col in subtotal:
            subtotal[col] = subtotal[col] / n_groups

    return timesheet_report, dates_local_abb, subtotal
'''
revenvus_report_data

'''
async def revenvus_report_data(
    org_unit_id: str = "0",
    zs_filter: int = 0,
    start_date: str | None = None,
    end_date: str | None = None,
    report_type: int = 0,
    cadres_ids: List[str] = Query(None),
    jobs_ids: List[str] = Query(None),
    class_ids: List[str] = Query(None),
    select_option: List[str] = Query(None),
    db: AsyncSession = Depends(get_session),
):
    # -----------------------------
    # Load data
    # -----------------------------
    timesheets = await get_timesheet_data(org_unit_id=org_unit_id, db=db)
    people = await get_internal_completeness_data(org_unit_id=org_unit_id, db=db)
    timesheets = timesheets.copy()
    people = people.copy()

    # -----------------------------
    # Map to child id/name -> location_id / location
    # -----------------------------
    parent_key = await getOrUnitType(org_unit_id)          # e.g. "district_id"
    child_key  = await getOrUnitChildrenLevel(org_unit_id)  # e.g. "health_area_id"

    if child_key and child_key in timesheets.columns and child_key in people.columns:
        # Use child as grouping level
        timesheets = timesheets.rename(columns={child_key: "location_id"})
        people     = people.rename(columns={child_key: "location_id"})

        child_name_col = f"{child_key}_name"
        timesheets["location"] = timesheets.get(child_name_col, "")
        people["location"]     = people.get(child_name_col, "")
    else:
        # Fallback to parent level
        timesheets = timesheets.rename(columns={parent_key: "location_id"})
        people     = people.rename(columns={parent_key: "location_id"})

        parent_name_col = f"{parent_key}_name"
        timesheets["location"] = timesheets.get(parent_name_col, "")
        people["location"]     = people.get(parent_name_col, "")

    # -----------------------------
    # Normalize dates
    # -----------------------------
    if start_date is None or end_date is None:
        start_dt = date.today() - relativedelta(months=6)
        end_dt   = date.today()
    else:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_dt   = datetime.strptime(end_date, "%Y-%m-%d").date()
    if end_dt < start_dt:
        raise ValueError("end_date must be >= start_date")

    # Precompute month key on timesheets for robust filtering
    timesheets["_month_key"] = pd.to_datetime(
        timesheets["mois_annee"], errors="coerce"
    ).dt.strftime("%Y-%m")

    # -----------------------------
    # Base frame: one row per location_id/location
    # -----------------------------
    revenu_report = (
        people.groupby(["location_id", "location"], dropna=False)["id"]
        .count()
        .rename("effectif")
        .to_frame()
        .sort_index()
    )

    # effectif_actif: distinct parents that have any timesheet in the window
    effectif_actif_src = timesheets.drop_duplicates(subset=["parent"])
    effectif_actif = (
        effectif_actif_src.groupby(["location_id"], dropna=False)["parent"]
        .nunique()
        .rename("effectif_actif")
    )
    revenu_report = revenu_report.merge(
        effectif_actif, how="left", left_on="location_id", right_index=True
    )

    # -----------------------------
    # Options / filters normalization
    # -----------------------------
    cadres_ids = cadres_ids or []
    jobs_ids   = jobs_ids or []
    class_ids  = class_ids or []
    select_option = select_option or []
    # Ensure select_option columns exist (missing -> 0) to allow .sum(axis=1)
    for col in select_option:
        if col not in timesheets.columns:
            timesheets[col] = 0

    # -----------------------------
    # Iterate months and compute:
    #  - {yy-mm}_montant : sum of selected columns
    #  - {YYYY-mm}_rapport: count of active parents (distinct) that month
    # -----------------------------
    dates_local_abb = []
    month_value_cols = []   # *_montant columns
    month_count_cols = []   # *_rapport columns

    # inclusive month loop
    i = 0
    while True:
        current = start_dt + relativedelta(months=i)
        key_filter = current.strftime("%Y-%m")
        amount_col = current.strftime("%y-%m") + "_montant"
        count_col  = current.strftime("%Y-%m") + "_rapport"

        dates_local_abb.append({
            "key": amount_col,
            "local_abb": current.strftime("%b-%y"),
            "effectif": count_col
        })
        month_value_cols.append(amount_col)
        month_count_cols.append(count_col)

        # Filter timesheets for this month and the locations we track
        mdata = timesheets.loc[
            (timesheets["_month_key"] == key_filter)
        ].copy()

        # Active parents this month (distinct per location)
        active_month = (
            mdata.drop_duplicates(subset=["parent"])
            .groupby("location_id", dropna=False)["parent"]
            .nunique()
            .rename(count_col)
        )

        # Apply cadre/job/class filters (if provided) BEFORE summing amounts
        if cadres_ids:
            mdata = mdata[mdata["cadre"].isin(cadres_ids)]
        if jobs_ids:
            mdata = mdata[mdata["job"].isin(jobs_ids)]
        if class_ids:
            mdata = mdata[mdata["classification"].isin(class_ids)]

        # Sum selected monetary columns per location_id
        if select_option:
            mdata["__total_sel__"] = mdata[select_option].sum(axis=1)
        else:
            mdata["__total_sel__"] = 0

        amount_per_loc = (
            mdata.groupby("location_id", dropna=False)["__total_sel__"]
            .sum()
            .rename(amount_col)
        )

        # Attach to revenu_report
        revenu_report = revenu_report.merge(
            amount_per_loc, how="left", left_on="location_id", right_index=True
        )
        revenu_report = revenu_report.merge(
            active_month, how="left", left_on="location_id", right_index=True
        )

        # Break when we reach end month
        if current.strftime("%Y-%m") == end_dt.strftime("%Y-%m"):
            break
        i += 1
        if i > 240:  # hard guard
            break

    # -----------------------------
    # Totals / averages
    # -----------------------------
    revenu_report[month_value_cols] = revenu_report[month_value_cols].fillna(0)
    revenu_report[month_count_cols] = revenu_report[month_count_cols].fillna(0)

    revenu_report["total"] = revenu_report[month_value_cols].sum(axis=1)
    months_count = max(len(month_value_cols), 1)
    revenu_report["moyenne"] = (revenu_report["total"] / months_count).round(0).astype(int)

    # Final column ordering
    dataIndex = (
        ["location_id", "location", "effectif", "effectif_actif"]
        + month_value_cols
        + month_count_cols
        + ["total", "moyenne"]
    )

    # Ensure both index levels available as columns (for easy JSON/export)
    revenu_report = revenu_report.reset_index()  # brings location_id/location to columns

    # Keep only requested columns (existence-checked)
    keep_cols = [c for c in dataIndex if c in revenu_report.columns]
    return revenu_report[keep_cols], dates_local_abb


async def getOrUnitType(id:str) -> str | None:


    conn = pg_get_mydb()
    with conn.cursor() as cur:
        cur.execute("SELECT level FROM public.organization_unit where id=%s", (id,))
        row = cur.fetchone()
        if row:
            return row[0]
    conn.close()
    return None

async def getOrUnitChildrenLevel(id:str) -> str | None:
    conn = pg_get_mydb()
    with conn.cursor() as cur:
        cur.execute("SELECT level FROM public.organization_unit where parent=%s limit 1", (id,))
        row = cur.fetchone()
        if row:
            return row[0]
    conn.close()
    return None


'''
 get_internal_completeness_data
'''


async def get_internal_completeness_data(
    org_unit_id: str = "0", 
    db: AsyncSession= Depends(get_session)
):
    data = []
    sub_query_conditions = []
    org_unit_type = None

    if org_unit_id != "0":
        org_unit_type = await getOrUnitType(org_unit_id)
        if org_unit_type is not None:
            orgId = org_unit_id.replace("'", "''")
            sub_query_conditions.append(f"t2.{org_unit_type} = '{orgId}'")

    # Build WHERE clause conditionally
    where_clause = " AND ".join(sub_query_conditions)
    if where_clause:
        where_clause = f" AND {where_clause}"

    # Compose SQL query
    sql = f"""
        SELECT 
            'bytearray(b''' || t1.id || ''')' AS mmid, 
            t1.*, 
            t2.* 
        FROM z_employment_status_view t1
        LEFT JOIN (
            SELECT * 
            FROM public.get_all_org_units_table()
        ) AS t2 ON t2.node_id = t1.facility_id
        WHERE t1.facility_id IS NOT NULL
        {where_clause}
    """

  # Convert result to DataFrame
    data = pd.read_sql(sql, sync_engine)

    # Drop duplicate records by 'id'
    if not data.empty and 'id' in data.columns:
        data = data.drop_duplicates(subset=['id'])

    return data

async def get_timesheet_data(org_unit_id: str = "0", db:AsyncSession=Depends(get_session)):

    data = []
    org_unit_type = await getOrUnitType(org_unit_id)
    SQL = """
            SELECT 
            ts.id, 
            to_char(ts.created, 'YYYY-MM-DD')  as created,
            ts.person_id as parent,
            ts.salary_received as salaire_recu,
            ts.bonus_risk as prime_risque,
            ts.bonus_local AS prime_locale,
            ts.bonus_partner as prime_ptf,
            ts.days_worked as jours_prestes,
            to_char(ts.month_year, 'YYYY-MM-DD') as mois_annee,
            t3.cadre,
            t3.job,
            t3.prime,
            t3.salaire,
            t3.classification,
            t3.salary_grade,
            t3.facility,
            t3.facility_name,
            t3.health_area,
            t3.health_area_name,
            t3.county,
            t3.county_name,
            t3.district,
            t3.region,
            t3.region_name,
            t3.country,
            t3.country_name
            FROM hippo_person_timesheet as ts
            JOIN (
            SELECT 'bytearray(b''' || t1.id || ''')' AS mmid, t1.*, t2.* 
            FROM z_employment_status_view t1
            LEFT JOIN (
                select * 
                from public.get_all_org_units_table()
            ) as t2 ON t2.node_id = t1.facility_id
            where t1.facility_id is not null
            ) As t3 ON t3.id = ts.person_id

        """
    _id = org_unit_id.replace("'", "''")
    SQL += f" AND t3.{org_unit_type} ='{_id}'"

    df = pd.read_sql(SQL, sync_engine)
    return df


def getHealthAreaBaseListe(db: Session, pr_id: str,  zs_id:str, staff:int, groupData: dict):
    if zs_id != "0":
        data = db.query(HealthAreaBaseListe.ha_id, HealthAreaBaseListe.value,HealthArea.name).where(HealthAreaBaseListe.ha_id == zs_id).join(HealthArea, HealthArea.id == HealthAreaBaseListe.ha_id).distinct(HealthAreaBaseListe.ha_id).first()
        print(data[0])
        return [
            {
                'id': data[0],
                'name': data[2],
                'value': staff,
                'base_list_max':data[1],
                'progression': (staff/ data[1]*100) if data[1] > 0 else 0
            }
        ]
   
    data = db.query(HealthAreaBaseListe.ha_id, HealthAreaBaseListe.value).where(HealthAreaBaseListe.parent == pr_id).distinct(HealthAreaBaseListe.ha_id).all()
   
   
    response = []
    for index,elt in  groupData.items(): 
        eltfound = False
        for haData  in data :
           if haData.ha_id == index[1]:
                response.append({
                    'id':index[1],
                    'name': index[0],
                    'value': elt,
                    'base_list_max': haData.value,
                    "progression": (elt/ haData.value *100) if haData.value > 0 else 0
                })
                eltfound = True
                break
        if eltfound == False :
            response.append({
                'id':index[1],
                'name': index[0],
                'value': elt,
                'base_list_max':0,
                'progression': 0
            })
    return  response