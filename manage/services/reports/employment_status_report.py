
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user
from sqlalchemy import text
from pathlib import Path

apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


@apiRouter.get("/employment_status_report/", response_model=list, dependencies=[Depends(get_current_active_user)],)
async def get_employment_staus_report(db: AsyncSession = Depends(get_session)):
    try:
        result = await db.execute(text("""
                                    
            SELECT t1.*, t2.* 
            FROM (select * from z_employment_status_view limit 100) t1
            LEFT JOIN (
                select * 
                from public.get_all_org_units_table()
            ) as t2 ON t2.node_id = t1.facility_id
            where t1.facility_id is not null
            LIMIT 10
                                
        """))
        rows = result.mappings().all()   # returns list of dict-like rows
        return rows
    
    except Exception:
        raise



@apiRouter.post(
    "/employment_status_report/generate",
    response_model=bool,
    dependencies=[Depends(get_current_active_user)]
)
async def generate_employment_status_report(db: AsyncSession = Depends(get_session)):
    try:
        # Call procedure with async SQLAlchemy
        await db.execute(text("CALL generate_employment_status_report()"))
        await db.commit()
        return True
    except Exception as e:
        # You may want to log e for debugging
        await db.rollback()
        return False

async def save_employment_status_report(db: AsyncSession = Depends(get_session)):
    result = await db.execute(text(SQL))
    rows = result.mappings().all()
    if not rows:
        return {"ok": True, "path": None, "message": "No rows to export."}

    EXPORT_DIR = Path("/opt/exports") 
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = EXPORT_DIR / f"employment_status_report_{ts}.csv"

    # Build CSV in-memory and write once (simple + safe for ~thousands of rows)
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

    with open(out_path, "w", encoding="utf-8", newline="") as f:
        f.write(buf.getvalue())

    return {"ok": True, "path": str(out_path)}