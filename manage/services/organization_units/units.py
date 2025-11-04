from manage.models import ViewOrgUnitList, HippoEntityMap, HippoAuditLog
from manage.services.organization_units.schemas import ViewOrgUnitListRead, OrgUnitCreate, OrgUnitUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.future import select
from manage.database import SessionLocal, engine
from endpoints.user_api import get_current_active_user
from sqlalchemy import text
from manage.services.entity_map import entity_map
from manage.utils import generate_unit_id
import uuid
import json
import io
import pandas as pd
from typing import List
from datetime import datetime


apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

@apiRouter.post("/organization_units", response_model=ViewOrgUnitListRead, dependencies=[Depends(get_current_active_user)])
async def create_org_unit(
    orgUnit:OrgUnitCreate,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_active_user),
):

    orgUnitData = orgUnit.dict()  # get dict from pydantic model
    orgUnitId = generate_unit_id(prefix=f"orgUnit|{orgUnit.level}", length=10)
    orgUnitData['id'] = orgUnitId
    
    new_orgUnit = ViewOrgUnitList(**orgUnitData)
    session.add(new_orgUnit)

    auditLog = HippoAuditLog(id= uuid.uuid4(), user_id=current_user_id, operation=f'add new org unit {orgUnitId}')
    session.add(auditLog)

    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise

    await session.commit()
    await session.refresh(new_orgUnit)
    return new_orgUnit

@apiRouter.put("/organization_units/{org_id}",)
async def update_person(org_id: str,
    orgUnit:OrgUnitUpdate, 
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_active_user),
):
  
    result = await session.execute(select(ViewOrgUnitList).where(ViewOrgUnitList.id == org_id))
    existing_org_unit = result.scalar_one_or_none()
    if not existing_org_unit:
        raise HTTPException(status_code=404, detail="Org Unit not found")
    
    for key, value in orgUnit.dict().items():
        if value != None and key != 'created':
            setattr(existing_org_unit, key, value)

    setattr(existing_org_unit, "last_modified_by", current_user_id)

    auditLog = HippoAuditLog(id= uuid.uuid4(), user_id=current_user_id, operation=f'update new orgUnit {org_id}, {orgUnit.name}')
    session.add(auditLog)

    await session.commit()
    await session.refresh(existing_org_unit)
    return existing_org_unit  


# Get all healthareas
@apiRouter.get("/organization_units", response_model=list[ViewOrgUnitListRead], dependencies=[Depends(get_current_active_user)],)
async def get_OrganisationUnit(db: AsyncSession = Depends(get_session)):
    result = await db.execute(text("""
        SELECT *
        FROM organization_unit                                      
    """))
    rows = result.mappings().all()
    return rows


# Get all healthareas
@apiRouter.get("/organization_units/{id}", response_model=ViewOrgUnitListRead, dependencies=[Depends(get_current_active_user)],)
async def get_OrganisationUnit(id:str,db: AsyncSession = Depends(get_session)):
    result = await db.execute(text(f"""
        SELECT *
        FROM organization_unit 
        WHERE id='{id}'                                     
    """))
    rows = result.mappings().all()
    if len(rows) == 0:
        raise HTTPException(status_code=404, detail="OrgUnit not found")
    return rows[0]


# Get all healthareas
@apiRouter.get("/organization_units/children/{parentId}", response_model=list, dependencies=[Depends(get_current_active_user)],)
async def get_OrganisationUnit(parentId:str,db: AsyncSession = Depends(get_session)):
    
    result = await db.execute(text(f"""
        SELECT *
        FROM organization_unit 
        WHERE parent='{parentId}' 
        ORDER BY name                     
    """))
    rows = result.all()
    return rows

# Get all healthareas
@apiRouter.get("/organization_units/tree/{parentId}", response_model=list, dependencies=[Depends(get_current_active_user)],)
async def get_OrganisationUnitTree(parentId:str,db: AsyncSession = Depends(get_session)):
    
    result = await db.execute(text(f"""
        WITH RECURSIVE tree AS (

            SELECT 
                id,
                name,
                parent,
                1 AS level,
                ARRAY[id::text] AS path_ids,
                name::text AS path_text
            FROM organization_unit
            WHERE id= '{parentId}'

            UNION ALL

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
    """))
    rows = result.all()
    return rows


# Get all healthareas
@apiRouter.get("/organization_units/path/{parentId}", response_model=list, dependencies=[Depends(get_current_active_user)],)
async def get_OrgUnitUpTree(parentId:str,db: AsyncSession = Depends(get_session)):
    
    result = await db.execute(text("""
       WITH RECURSIVE up AS (
            SELECT id, name, parent,  level, 0 AS hops
            FROM organization_unit
            WHERE id =:id

            UNION ALL
            SELECT p.id, p.name, p.parent, p.level, u.hops + 1
            FROM organization_unit p
            JOIN up u ON p.id = u.parent
        )
        SELECT *
        FROM up
        ORDER BY hops DESC;   
               
    """), { 'id': parentId})
    rows = result.all()
    return rows

# Export organization units to XLSX
@apiRouter.get("/organization_units/export/xlsx/", dependencies=[Depends(get_current_active_user)])
async def export_org_units_to_xlsx(
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_active_user)
):
    """
    Export all organization units to Excel format with columns: id, name, code, parent, level
    """
    try:
        # Query all organization units
        result = await db.execute(text("""
            SELECT id, name, code, parent, level
            FROM organization_unit
            ORDER BY level, name
        """))
        rows = result.mappings().all()
        
        if not rows:
            raise HTTPException(status_code=404, detail="No organization units found")
        
        # Convert to DataFrame
        df = pd.DataFrame([dict(row) for row in rows])
        
        # Reorder columns to match requested format
        df = df[['id', 'name', 'code', 'parent', 'level']]
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Organization Units', index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Organization Units']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        
        # Create audit log
        audit_log = HippoAuditLog(
            id=uuid.uuid4(), 
            user_id=current_user_id, 
            operation='export organization units to xlsx'
        )
        db.add(audit_log)
        await db.commit()
        
        # Return file as download
        filename = f"organization_units_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

# Import organization units from JSON array
@apiRouter.post("/organization_units/import/json", dependencies=[Depends(get_current_active_user)])
async def import_org_units_from_json(
    org_units_data: List[dict],
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_active_user)
):
    """
    Import organization units from JSON array
    Expected fields in each object: name, code, parent, level
    ID will be auto-generated if not provided
    """
    try:
        imported_count = 0
        updated_count = 0
        errors = []
        
        for index, org_unit_data in enumerate(org_units_data):
            try:
                # Validate required fields
                required_fields = ['name', 'level']
                for field in required_fields:
                    if field not in org_unit_data:
                        errors.append(f"Row {index + 1}: Missing required field '{field}'")
                        continue
                
                
                # Create new organization unit
                org_unit_id = generate_unit_id(prefix=f"orgUnit|{org_unit_data['level']}", length=10)
                if org_unit_data['id'] is not None :
                    org_unit_id = org_unit_data['id']
                
                new_org_unit = ViewOrgUnitList(
                    id=org_unit_id,
                    name=org_unit_data['name'],
                    code=org_unit_data.get('code'),
                    parent=org_unit_data.get('parent'),
                    level=org_unit_data['level']
                )
                    
                session.add(new_org_unit)
                imported_count += 1
                    
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
                continue
        
        # Create audit log
        audit_log = HippoAuditLog(
            id=uuid.uuid4(),
            user_id=current_user_id,
            operation=f'import organization units from json - {imported_count} imported, {updated_count} updated'
        )
        session.add(audit_log)
        
        await session.commit()
        
        return {
            "message": "Import completed",
            "imported_count": imported_count,
            "updated_count": updated_count,
            "error_count": len(errors),
            "errors": errors
        }
        
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")