"""
Employment Status Report API
-----------------------------

This module provides endpoints for:

1. Fetching employment status report data.
2. Triggering report generation via database procedure.
3. Exporting report results to CSV file.

The report combines:
- Employment status view (z_employment_status_view)
- Organizational hierarchy (get_all_org_units_table())

All endpoints require authenticated active users.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user
from sqlalchemy import text
from pathlib import Path

# Initialize router
apiRouter = APIRouter()


async def get_session() -> AsyncSession:
    """
    Provides an asynchronous database session.

    - Opens AsyncSession
    - Yields it during request lifecycle
    - Automatically closes after completion
    """
    async with SessionLocal() as session:
        yield session


# -------------------------------------------------------------------
# FETCH EMPLOYMENT STATUS REPORT (PREVIEW)
# -------------------------------------------------------------------
@apiRouter.get(
    "/employment_status_report/",
    response_model=list,
    dependencies=[Depends(get_current_active_user)],
)
async def get_employment_staus_report(db: AsyncSession = Depends(get_session)):
    """
    Retrieve employment status report data.

    This query:
        - Selects from z_employment_status_view (limited rows for preview).
        - Joins organizational hierarchy data.
        - Ensures facility_id is not NULL.
        - Limits output size for performance safety.

    Returns:
        List[dict]: Combined employment + org unit data.
    """
    try:
        result = await db.execute(text("""
            SELECT t1.*, t2.* 
            FROM (
                SELECT * 
                FROM z_employment_status_view 
                LIMIT 100
            ) t1
            LEFT JOIN (
                SELECT * 
                FROM public.get_all_org_units_table()
            ) AS t2 
            ON t2.node_id = t1.facility_id
            WHERE t1.facility_id IS NOT NULL
            LIMIT 10
        """))

        # Convert SQL result to list of dictionary-like rows
        rows = result.mappings().all()
        return rows

    except Exception:
        # Re-raise exception (could add logging here)
        raise


# -------------------------------------------------------------------
# TRIGGER REPORT GENERATION (STORED PROCEDURE)
# -------------------------------------------------------------------
@apiRouter.post(
    "/employment_status_report/generate",
    response_model=bool,
    dependencies=[Depends(get_current_active_user)]
)
async def generate_employment_status_report(
    db: AsyncSession = Depends(get_session)
):
    """
    Trigger database stored procedure to generate
    employment status report data.

    Typically used when:
        - Report is precomputed
        - Materialized view or summary table needs refresh

    Process:
        1. Call stored procedure.
        2. Commit transaction.
        3. Return True if successful.
        4. Rollback and return False on failure.

    Returns:
        bool: True if procedure executed successfully.
    """
    try:
        await db.execute(text("CALL generate_employment_status_report()"))
        await db.commit()
        return True

    except Exception as e:
        # Rollback on failure to maintain DB integrity
        await db.rollback()
        # Logging should be added in production
        return False


# -------------------------------------------------------------------
# EXPORT REPORT TO CSV FILE
# -------------------------------------------------------------------
async def save_employment_status_report(
    db: AsyncSession = Depends(get_session)
):
    """
    Execute report query and export results to CSV file.

    Steps:
        1. Execute predefined SQL query (SQL must be defined elsewhere).
        2. Fetch rows as dictionaries.
        3. Create export directory if it doesn't exist.
        4. Generate timestamped filename.
        5. Write CSV file safely.
        6. Return export path.

    Returns:
        dict:
            {
                "ok": bool,
                "path": str | None,
                "message": optional
            }
    """

    # Execute report SQL (SQL variable must exist globally)
    result = await db.execute(text(SQL))
    rows = result.mappings().all()

    # If no data, return early
    if not rows:
        return {"ok": True, "path": None, "message": "No rows to export."}

    # Define export directory
    EXPORT_DIR = Path("/opt/exports")
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    # Generate timestamped filename
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = EXPORT_DIR / f"employment_status_report_{ts}.csv"

    # Build CSV in memory
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

    # Write file to disk
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        f.write(buf.getvalue())

    return {"ok": True, "path": str(out_path)}