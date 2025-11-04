from datetime import datetime
import json
from fastapi import APIRouter, Depends, Response, Query
from jinja2 import Environment, FileSystemLoader
from helpers.helpers import download_dataframe_as_xlsx
from models.crud import get_person_timesheet, get_revenu_report_utils
from sqlalchemy.orm import Session
from reports.reports import (
    completude_timesheet,
    get_dashboard_data,
    get_salaire_prime_report,
    performance_bonus_calc,
    revenvus_report_data,
    get_internal_completeness_report_career,
)
from weasyprint import HTML

from sqlalchemy.ext.asyncio import AsyncSession
from manage.database import SessionLocal as AsyncSessionLocal
from config.Database2 import SessionLocal as SyncSessionLocal

from starlette.concurrency import run_in_threadpool  # ✅ offload blocking calls

router = APIRouter()

# --- DB deps ---
def get_db():
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


# ---------------------------
# Dashboard (already async/IO-bound)
# ---------------------------
@router.get('/dashboard')
async def dashboard_data(
    org_unit_id: str = "0",
    session: AsyncSession = Depends(get_session),                         
):
    # assuming get_dashboard_data is async; if not, offload with run_in_threadpool
    if ( org_unit_id == "0" ):
        return {"message": "No org unit selected"}
    
    result = await get_dashboard_data(org_unit_id=org_unit_id, db=session)
    return result


# ---------------------------
# Person timesheet (async)
# ---------------------------
@router.get("/person_timesheet")
async def person_timesheet(person_id: str, db: Session = Depends(get_db)):
    # get_person_timesheet looks async; if it's sync, wrap in run_in_threadpool
    result = await get_person_timesheet(person_id=person_id, db=db)
    return result


# ---------------------------
# Timesheet report (mixed: Pandas + Jinja2 + WeasyPrint -> blocking)
# ---------------------------
@router.get("/timesheet_report")
async def times_report(
    org_unit_id: str = "0",
    zs_filter: int = 0,
    start_date: str | None = None,
    end_date: str | None = None,
    download: int = 0,
    title: str = "",
    session: AsyncSession = Depends(get_session),
):
    if ( org_unit_id == "0" ):
        return {"message": "No org unit selected"}
    # completude_timesheet likely does Pandas/CPU; offload
    res, intervals, subtotal = await completude_timesheet(org_unit_id=org_unit_id, zs_filter=zs_filter, start_date=start_date, end_date=end_date,  db=session)
    

    # 1) XLSX download (blocking: DF->xlsx)
    if download in (1, 2):
        # generate detailed frame (blocking) in thread
        res_dl = await run_in_threadpool(
            completude_timesheet,
            org_unit_id, zs_filter, start_date, end_date, download ,session
        )
        # download_dataframe_as_xlsx does I/O; offload
        return await run_in_threadpool(
            download_dataframe_as_xlsx,
            res_dl,
            f'Rapport de prestation - {title}',
        )

    # 2) PDF download (Jinja2 + WeasyPrint are blocking)
    if download == 3:
        env = Environment(loader=FileSystemLoader("templates"))  # light, ok inline
        template = env.get_template("timesheet_report.html")
        _time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        # mutate a copy to add index (Pandas operation done earlier; here it's Python list/dict)
        res_with_index = res.copy()
        res_with_index['_index'] = range(1, len(res_with_index) + 1)

        # Blocking HTML render + PDF generation -> threadpool
        rendered_html = await run_in_threadpool(
            template.render,
            data=res_with_index,
            dates=intervals,
            current_date=_time,
            title=title,
            subtotal=subtotal
        )
        pdf_content = await run_in_threadpool(HTML(string=rendered_html).write_pdf)

        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                'Access-Control-Expose-Headers': 'Content-Disposition',
                'Content-Disposition': f'attachment; filename="COMPLETUDE DE PRESTATION -{title}-{_time}.pdf"'
            }
        )

    # 3) JSON (Pandas to_json is blocking)
    json_report = await run_in_threadpool(res.to_json, orient="table")
    return {"report": json.loads(json_report), "intervals": intervals}


# ---------------------------
# Revenus report (Pandas + JSON + XLSX blocking)
# ---------------------------
@router.get("/revenu_report")
async def revenu_report(
    org_unit_id: str = "0",
    zs_filter: int = 0,
    start_date: str | None = None,
    end_date: str | None = None,
    report_type: int = 0,
    cadres_ids: list[str] = Query(None),
    jobs_ids: list[str] = Query(None),
    class_ids: list[str] = Query(None),
    select_option: list[str] = Query(None),
    download: int = 0,
    title: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    if ( org_unit_id == "0" ):
        return {"message": "No org unit selected"}
    # parse JSON arrays (cheap)
    select_option = json.loads(select_option[0])
    cadres_ids = json.loads(cadres_ids[0])
    jobs_ids = json.loads(jobs_ids[0])
    class_ids = json.loads(class_ids[0])

    # heavy report calc -> threadpool
    res, intervals = await  revenvus_report_data(
        org_unit_id=org_unit_id, report_type = report_type, zs_filter = zs_filter, 
        start_date = start_date, end_date=end_date,
        cadres_ids = cadres_ids, jobs_ids = jobs_ids, class_ids = class_ids, select_option = select_option, db=session
    )
    

    if download == 1:
        s = ' '.join(select_option) + ' ' + ' '.join(cadres_ids) + ' '.join(jobs_ids) + ' ' + ' '.join(class_ids)
        return await run_in_threadpool(download_dataframe_as_xlsx, res, f'Revenus -{title} - {s}')

    json_report = await run_in_threadpool(res.to_json, orient="table")
    return {"report": json.loads(json_report), "intervals": intervals}


# ---------------------------
# Internal completeness (already async)
# ---------------------------
@router.get("/comp/internal")
async def read_root(org_unit_id: str = "0", filter: int = 0,
                     session: AsyncSession = Depends(get_session),
                    ):
    if ( org_unit_id == "0" ):
        return {"message": "No org unit selected"}
    a = await get_internal_completeness_report_career(org_unit_id=org_unit_id, filter=filter, db=session)
    json_report = await run_in_threadpool(a.to_json, orient="table")
    return json.loads(json_report)


# ---------------------------
# Revenus utils (DB sync) – cheap, keep sync or offload if needed
# ---------------------------
@router.get("/revenu_report_utils")
async def revenu_report_utils(db: Session = Depends(get_db)):
    # If get_revenu_report_utils is DB-bound sync and potentially slow, offload:
    return await run_in_threadpool(get_revenu_report_utils, db)


# ---------------------------
# Performance bonus (Pandas + Jinja2 + PDF)
# ---------------------------
@router.get("/performance_bonus_calc")
async def bonus_report(
    org_unit_id: str = "0",
    zs_filter: int = 0,
    start_date: str | None = None,
    end_date: str | None = None,
    download: int = 0,
    title: str = "",
    session: AsyncSession = Depends(get_session),
):
    if ( org_unit_id == "0" ):
        return {"message": "No org unit selected"}
    # heavy calc -> threadpool
    res, intervals, subtotal = await performance_bonus_calc(
        org_unit_id = org_unit_id, zs_filter = zs_filter, start_date =start_date,
        end_date = end_date, download = download, db=session
    )

    if download == 1:
        env = Environment(loader=FileSystemLoader("templates"))
        template = env.get_template("performance_bonus.html")
        _time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        rendered_html = await run_in_threadpool(
            template.render,
            data=res,
            dates=intervals,
            subtotal=subtotal,
            current_date=_time
        )
        pdf_content = await run_in_threadpool(HTML(string=rendered_html).write_pdf)
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                'Access-Control-Expose-Headers': 'Content-Disposition',
                'Content-Disposition': f'attachment; filename="PRIME DE PERFORMANCE-{_time}.pdf"'
            }
        )

    json_report = await run_in_threadpool(res.to_json, orient="table")
    sub_json = await run_in_threadpool(subtotal.to_json)
    return {
        "report": json.loads(json_report),
        "intervals": intervals,
        "subdata": json.loads(sub_json)
    }


# ---------------------------
# Salaire / prime (async + XLSX)
# ---------------------------
@router.get("/situation_salaire_prime")
async def salaire_prime_report(
    org_unit_id: str = "0", zs_filter: int = 0, 
    title: str = "", download: int = 0,
    session: AsyncSession = Depends(get_session)
    ):
    if ( org_unit_id == "0" ):
        return {"message": "No org unit selected"}
    res = await get_salaire_prime_report(org_unit_id=org_unit_id, zs_filter=zs_filter, db=session)

    if download == 1:
        return await run_in_threadpool(download_dataframe_as_xlsx, res, f'SITUATION SALAIRE PRIME - {title}')

    json_report = await run_in_threadpool(res.to_json, orient="table")
    return {"report": json.loads(json_report)}
