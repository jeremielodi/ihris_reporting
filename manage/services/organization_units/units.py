# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

# ORM models (Org Unit view/table + audit + entity map)
from manage.models import ViewOrgUnitList, HippoEntityMap, HippoAuditLog

# Pydantic schemas (request validation + response serialization)
from manage.services.organization_units.schemas import (
    ViewOrgUnitListRead,
    OrgUnitCreate,
    OrgUnitUpdate
)

# Async database session
from sqlalchemy.ext.asyncio import AsyncSession

# FastAPI utilities
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse

# SQLAlchemy query builder for ORM-style queries
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

# Database session factory
from manage.database import SessionLocal, engine

# Authentication dependency (protects endpoints)
from endpoints.user_api import get_current_active_user

# Raw SQL execution
from sqlalchemy import text

# Utility service for numbering/id generation (currently not used in this file)
from manage.services.entity_map import entity_map

# Utility function to generate org unit IDs
from manage.utils import generate_unit_id

# Misc
import uuid
import json
import io
import pandas as pd
from typing import List
from datetime import datetime


# Create API router instance
apiRouter = APIRouter()


# ---------------------------------------------------------
# Dependency: Get Async DB Session
# ---------------------------------------------------------
async def get_session() -> AsyncSession:
    """
    Provides an async database session to endpoints.
    Ensures proper session lifecycle management (open/close).
    """
    async with SessionLocal() as session:
        yield session


# ---------------------------------------------------------
# CREATE ORGANIZATION UNIT
# ---------------------------------------------------------
@apiRouter.post(
    "/organization_units",
    response_model=ViewOrgUnitListRead,
    dependencies=[Depends(get_current_active_user)]
)
async def create_org_unit(
    orgUnit: OrgUnitCreate,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_active_user),
):
    """
    Create a new organization unit.

    - Generates a new org unit ID using `generate_unit_id`.
    - Inserts the org unit in `organization_unit` (via ViewOrgUnitList model).
    - Creates an audit log entry (HippoAuditLog).
    """

    # Convert Pydantic model -> dict
    orgUnitData = orgUnit.model_dump()

    # Generate an ID with prefix based on org unit level (e.g. orgUnit|3xxxxx)
    orgUnitId = generate_unit_id(prefix=f"orgUnit|{orgUnit.level}", length=10)
    orgUnitData['id'] = orgUnitId

    # Create ORM instance and stage it for insertion
    new_orgUnit = ViewOrgUnitList(**orgUnitData)
    session.add(new_orgUnit)

    # Audit trail: record who created the org unit
    auditLog = HippoAuditLog(
        id=uuid.uuid4(),
        user_id=current_user_id,
        operation=f'add new org unit {orgUnitId} - {new_orgUnit.name}'
    )
    session.add(auditLog)

    # Commit transaction safely
    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise

    # NOTE: This second commit is redundant because you already committed above.
    # Keeping it as-is (comment only), but you can safely remove the next line.
    await session.commit()

    # Refresh to get DB-generated fields (if any)
    await session.refresh(new_orgUnit)
    return new_orgUnit


# ---------------------------------------------------------
# UPDATE ORGANIZATION UNIT
# ---------------------------------------------------------
@apiRouter.put("/organization_units/{org_id}")
async def update_org_unit(
    org_id: str,
    orgUnit: OrgUnitUpdate,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_active_user),
):
    """
    Update an existing organization unit by ID.

    - Loads org unit via ORM query.
    - Applies non-null fields from request (excluding 'created').
    - Sets last_modified_by for auditing.
    - Creates audit log entry.
    """

    # Fetch existing org unit
    result = await session.execute(
        select(ViewOrgUnitList).where(ViewOrgUnitList.id == org_id)
    )
    existing_org_unit = result.scalar_one_or_none()

    if not existing_org_unit:
        raise HTTPException(status_code=404, detail="Org Unit not found")

    # Apply incoming fields (partial update behavior)
    for key, value in orgUnit.model_dump().items():
        if value is not None and key != 'created':
            setattr(existing_org_unit, key, value)

    # Track who modified the org unit
    setattr(existing_org_unit, "last_modified_by", current_user_id)

    # Audit trail: record update action
    auditLog = HippoAuditLog(
        id=uuid.uuid4(),
        user_id=current_user_id,
        operation=f'update new orgUnit {org_id}, {orgUnit.name}'
    )
    session.add(auditLog)

    await session.commit()
    await session.refresh(existing_org_unit)
    return existing_org_unit


# ---------------------------------------------------------
# DELETE ORGANIZATION UNIT
# ---------------------------------------------------------
@apiRouter.delete("/organization_units/{org_id}")
async def delete_org_unit(
    org_id: str,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_active_user),
):
    """
    Delete an organization unit.

    The DB enforces organization_unit_parent_fkey (ON DELETE NO ACTION), so
    this is rejected with a 409 if the unit still has children - the
    caller has to delete or re-parent them first. Note that other tables
    referencing an org unit by id (facility.location, hippo_person.residence,
    etc.) are plain string columns with no FK constraint, so deleting a
    unit still "in use" there won't be blocked; those references just go
    stale rather than raising an error.
    """
    result = await session.execute(select(ViewOrgUnitList).where(ViewOrgUnitList.id == org_id))
    org_unit = result.scalar_one_or_none()

    if not org_unit:
        raise HTTPException(status_code=404, detail="Org Unit not found")

    auditLog = HippoAuditLog(
        id=uuid.uuid4(),
        user_id=current_user_id,
        operation=f'delete orgUnit {org_id}, {org_unit.name}'
    )
    session.add(auditLog)

    await session.delete(org_unit)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cannot delete: this organization unit still has child units. Delete or move them first."
        )

    return {"detail": "Organization unit deleted successfully"}


# ---------------------------------------------------------
# GET ALL ORGANIZATION UNITS
# ---------------------------------------------------------
@apiRouter.get(
    "/organization_units",
    response_model=list[ViewOrgUnitListRead],
    dependencies=[Depends(get_current_active_user)],
)
async def get_OrganisationUnit(db: AsyncSession = Depends(get_session)):
    """
    Return all organization units.

    Uses a raw SQL query against the `organization_unit` table.
    """

    result = await db.execute(text("""
        SELECT *
        FROM organization_unit
    """))

    # mappings() returns dict-like rows (safer for JSON responses)
    rows = result.mappings().all()
    return rows


# ---------------------------------------------------------
# GET ORGANIZATION UNIT DETAILS BY ID
# ---------------------------------------------------------
@apiRouter.get(
    "/organization_units/{id}",
    response_model=ViewOrgUnitListRead,
    dependencies=[Depends(get_current_active_user)],
)
async def get_OrganisationUnit(id: str, db: AsyncSession = Depends(get_session)):
    """
    Return one organization unit by ID.

    WARNING: this uses f-string SQL interpolation, which risks SQL injection.
    Prefer parameterized queries (like you did in /path endpoint).
    """

    result = await db.execute(text("""
        SELECT *
        FROM organization_unit
        WHERE id=:id
    """), {"id": id})

    rows = result.mappings().all()
    if len(rows) == 0:
        raise HTTPException(status_code=404, detail="OrgUnit not found")

    return rows[0]


# ---------------------------------------------------------
# GET CHILDREN OF A PARENT ORG UNIT
# ---------------------------------------------------------
@apiRouter.get(
    "/organization_units/children/{parentId}",
    response_model=list,
    dependencies=[Depends(get_current_active_user)],
)
async def get_OrganisationUnit(parentId: str, db: AsyncSession = Depends(get_session)):
    """
    Return direct children of an org unit, ordered by name.

    WARNING: uses f-string SQL interpolation (SQL injection risk).
    Prefer parameterized query (WHERE parent=:parentId).
    """

    result = await db.execute(text("""
        SELECT *
        FROM organization_unit
        WHERE parent=:parentId
        ORDER BY name
    """), {"parentId": parentId})

    rows = result.mappings().all()
    return [dict(row) for row in rows]


# ---------------------------------------------------------
# GET ORG UNIT TREE (DOWNWARD) FROM A PARENT ID
# ---------------------------------------------------------
@apiRouter.get(
    "/organization_units/tree/{parentId}",
    response_model=list,
    dependencies=[Depends(get_current_active_user)],
)
async def get_OrganisationUnitTree(parentId: str, db: AsyncSession = Depends(get_session)):
    """
    Returns a hierarchical tree (downward recursion) starting from parentId.

    - Uses a recursive CTE.
    - Tracks path to avoid cycles (c.id <> ALL(t.path_ids)).
    - Returns: id, name, parent, level, path_text ordered by path_ids.
    """

    result = await db.execute(text("""
        WITH RECURSIVE tree AS (

            -- Start node
            SELECT
                id,
                name,
                parent,
                1 AS level,
                ARRAY[id::text] AS path_ids,
                name::text AS path_text
            FROM organization_unit
            WHERE id= :parentId

            UNION ALL

            -- Recursive step: add children
            SELECT
                c.id,
                c.name,
                c.parent,
                t.level + 1,
                t.path_ids || c.id,
                t.path_text || ' / ' || c.name
            FROM organization_unit c
            JOIN tree t ON c.parent = t.id
            WHERE c.id <> ALL(t.path_ids)
        )
        SELECT id, name, parent, level, path_text
        FROM tree
        ORDER BY path_ids;
    """), {"parentId": parentId})

    rows = result.mappings().all()
    return [dict(row) for row in rows]


# ---------------------------------------------------------
# GET ORG UNIT PATH (UPWARD) TO ROOT
# ---------------------------------------------------------
@apiRouter.get(
    "/organization_units/path/{parentId}",
    response_model=list,
    dependencies=[Depends(get_current_active_user)],
)
async def get_OrgUnitUpTree(parentId: str, db: AsyncSession = Depends(get_session)):
    """
    Returns the path from a node up to the root (upward recursion).

    - Uses a recursive CTE "up".
    - Adds a 'hops' counter to sort from root -> leaf (DESC).
    - Uses a parameterized query (:id) to avoid SQL injection.
    """

    result = await db.execute(text("""
       WITH RECURSIVE up AS (
            SELECT id, name, parent, level, 0 AS hops
            FROM organization_unit
            WHERE id = :id

            UNION ALL

            SELECT p.id, p.name, p.parent, p.level, u.hops + 1
            FROM organization_unit p
            JOIN up u ON p.id = u.parent
        )
        SELECT *
        FROM up
        ORDER BY hops DESC;
    """), {'id': parentId})

    rows = result.mappings().all()
    return [dict(row) for row in rows]


# ---------------------------------------------------------
# EXPORT ORGANIZATION UNITS TO XLSX
# ---------------------------------------------------------
@apiRouter.get(
    "/organization_units/export/xlsx/",
    dependencies=[Depends(get_current_active_user)]
)
async def export_org_units_to_xlsx(
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_active_user)
):
    """
    Export all organization units to an Excel (.xlsx) file.

    - Queries columns: id, name, code, parent, level.
    - Builds an in-memory Excel file with pandas + openpyxl.
    - Auto-adjusts column widths.
    - Records an audit log entry.
    - Returns a StreamingResponse as an attachment download.
    """
    try:
        # Fetch org units in a stable order (level then name)
        result = await db.execute(text("""
            SELECT id, name, code, parent, level
            FROM organization_unit
            ORDER BY level, name
        """))

        rows = result.mappings().all()
        if not rows:
            raise HTTPException(status_code=404, detail="No organization units found")

        # Convert rows -> DataFrame for easier export to Excel
        df = pd.DataFrame([dict(row) for row in rows])

        # Ensure column order matches expected export format
        df = df[['id', 'name', 'code', 'parent', 'level']]

        # Create an Excel file in memory (BytesIO)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Organization Units', index=False)

            # Auto-adjust column widths for readability
            worksheet = writer.sheets['Organization Units']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        max_length = max(max_length, len(str(cell.value)))
                    except Exception:
                        pass
                worksheet.column_dimensions[column_letter].width = min(max_length + 2, 50)

        # Reset stream position before sending it
        output.seek(0)

        # Audit trail: record export action
        audit_log = HippoAuditLog(
            id=uuid.uuid4(),
            user_id=current_user_id,
            operation='export organization units to xlsx'
        )
        db.add(audit_log)
        await db.commit()

        # Build a timestamped filename
        filename = f"organization_units_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        # Stream file as downloadable attachment
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        # Convert unexpected errors into a standard HTTP 500 response
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


# ---------------------------------------------------------
# IMPORT ORGANIZATION UNITS FROM JSON ARRAY
# ---------------------------------------------------------
@apiRouter.post(
    "/organization_units/import/json",
    dependencies=[Depends(get_current_active_user)]
)
async def import_org_units_from_json(
    org_units_data: List[dict],
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_active_user)
):
    """
    Import organization units from a JSON array.

    Expected fields per item:
      - name (required)
      - level (required)
      - code (optional)
      - parent (optional)
      - id (optional: if provided, it will be used)

    Behavior:
      - If 'id' is missing, generate it using generate_unit_id(prefix=orgUnit|<level>).
      - Inserts each org unit in the DB (no upsert currently).
      - Collects row-level errors and returns them in response.
      - Records an audit log entry with import counts.
    """
    try:
        imported_count = 0
        updated_count = 0  # NOTE: not currently used; no update/upsert logic implemented
        errors = []

        # Process each incoming object
        for index, org_unit_data in enumerate(org_units_data):
            try:
                # Validate required fields
                required_fields = ['name', 'level']
                for field in required_fields:
                    if field not in org_unit_data:
                        errors.append(f"Row {index + 1}: Missing required field '{field}'")
                        # Skip current row (continue the outer loop)
                        raise ValueError("Missing required fields")

                # Generate new organization unit ID unless provided
                org_unit_id = generate_unit_id(
                    prefix=f"orgUnit|{org_unit_data['level']}",
                    length=10
                )

                # If caller provided an ID, use it (but be careful with None)
                if org_unit_data.get('id') is not None:
                    org_unit_id = org_unit_data['id']

                # Create ORM instance
                new_org_unit = ViewOrgUnitList(
                    id=org_unit_id,
                    name=org_unit_data['name'],
                    code=org_unit_data.get('code'),
                    parent=org_unit_data.get('parent'),
                    level=org_unit_data['level']
                )

                # Stage for insertion
                session.add(new_org_unit)
                imported_count += 1

            except Exception as e:
                # Capture per-row errors without stopping the full import
                errors.append(f"Row {index + 1}: {str(e)}")
                continue

        # Audit trail: record import action summary
        audit_log = HippoAuditLog(
            id=uuid.uuid4(),
            user_id=current_user_id,
            operation=f'import organization units from json - {imported_count} imported, {updated_count} updated'
        )
        session.add(audit_log)

        await session.commit()

        # Return import summary + errors
        return {
            "message": "Import completed",
            "imported_count": imported_count,
            "updated_count": updated_count,
            "error_count": len(errors),
            "errors": errors
        }

    except Exception as e:
        # Rollback on fatal error
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")