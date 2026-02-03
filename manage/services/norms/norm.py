
from fastapi import APIRouter, Depends, HTTPException
from manage.services.norms import methods as normMethods
from manage.services.norms.schema import FacilityResult, NodeRollup
from manage.database import SessionLocal, engine
from manage.services.organization_units import methods as orgUnitMethods
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from fastapi.responses import StreamingResponse

from io import BytesIO
from datetime import datetime

from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, Alignment


apiRouter = APIRouter()

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session



# ---------------------------------------


@apiRouter.get("/norms/facilities", response_model=list[FacilityResult])
async def check_all_facilities(db: AsyncSession = Depends(get_session)):
    facilities = await normMethods.db_list_facilities(db)

    out = []
    for f in facilities:
        organization_unit_type_id = await normMethods.db_get_organization_unit_type_id(f["id"], db)
        required = await normMethods.db_get_norms(organization_unit_type_id, db)
        actual = await normMethods.db_get_actual_staff(f["id"], db)

        if actual is None:
            actual = {}
        calc = normMethods.compute_facility(required, actual)

        out.append(FacilityResult(
            org_unit_id=f["id"],
            organization_unit_type_id=organization_unit_type_id,
            required=required,
            actual= actual,
            missing=calc["missing"],
            excess=calc["excess"],
            compliance_ratio=calc["compliance_ratio"]
        ))
    return out


@apiRouter.get("/norms/rollup/{node_id}", response_model=NodeRollup)
async def rollup_node(node_id: str, db: AsyncSession = Depends(get_session)):
    """
    Calcule la conformité d'un node (district/province) en sommant ses facilities descendants.
    """
    # 1) récupérer toutes les facilities descendantes de node_id (via CTE recursive en DB)
    # Ici je suppose que tu as une méthode normMethods.db_list_descendant_facilities(node_id)
    facilities = await normMethods.db_list_descendant_facilities(node_id, db)  # [{"id": "..."}]

    if not facilities:
        raise HTTPException(404, "No descendant facilities found")

    required_list = []
    actual_list = []

    for facilityId in facilities:
        organization_unit_type_id = await normMethods.db_get_organization_unit_type_id(facilityId, db)
        required = await normMethods.db_get_norms(organization_unit_type_id, db)
        actual = await normMethods.db_get_actual_staff(facilityId, db)
        required_list.append(required)
        actual_list.append(actual)

    required_sum = normMethods.sum_dicts(required_list)
    actual_sum = normMethods.sum_dicts(actual_list)

    calc = normMethods.compute_facility(required_sum, actual_sum)

    required_total = sum(required_sum.values())
    actual_total = sum(actual_sum.values())
    missing_total = sum(calc["missing"].values())

    return NodeRollup(
        org_unit_id=node_id,
        level="aggregated",
        required_total=required_total,
        actual_total=actual_total,
        missing_total=missing_total,
        compliance_ratio=calc["compliance_ratio"]
    )


@apiRouter.get("/norms/{node_id}/tree")
async def check_norms_from_node(node_id: str,  db: AsyncSession = Depends(get_session)):
    return await  normMethods.build_norm_tree_report(node_id, db)


def _autofit(ws):
    for col in range(1, ws.max_column + 1):
        max_len = 0
        letter = get_column_letter(col)
        for row in range(1, ws.max_row + 1):
            v = ws.cell(row=row, column=col).value
            if v is None:
                continue
            max_len = max(max_len, len(str(v)))
        ws.column_dimensions[letter].width = min(max_len + 2, 60)


def _all_keys(stat: dict) -> list[str]:
    keys = set()
    if not stat:
        return []
    for k in ("required", "actual", "missing_total", "excess"):
        obj = stat.get(k) or {}
        keys.update(obj.keys())
    return sorted(keys)

def _write_orgunit_table(ws, start_row: int, org_unit: dict, classification_map: dict | None = None) -> int:
    """
    Ecrit:
    NORMES - orgUnit.name
    CATEGORIE | REQUIS | ACTIF | CARENCE | PLETORE
    """
    stat = org_unit.get("stat") or {}

    title = f"NORMES - {org_unit.get('name')}"
    ws.cell(row=start_row, column=1, value=title).font = Font(bold=True, size=12)
    ws.merge_cells(start_row=start_row, start_column=1, end_row=start_row, end_column=5)

    header_row = start_row + 1
    headers = ["CATEGORIE", "REQUIS", "ACTIF", "CARENCE", "PLETORE"]
    for i, h in enumerate(headers, start=1):
        cell = ws.cell(row=header_row, column=i, value=h)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    row = header_row + 1
    for cid in _all_keys(stat):
        name = cid
        if classification_map and cid in classification_map:
            name = classification_map[cid].get("name") or cid

        ws.cell(row=row, column=1, value=name)
        ws.cell(row=row, column=2, value=int((stat.get("required") or {}).get(cid, 0) or 0))
        ws.cell(row=row, column=3, value=int((stat.get("actual") or {}).get(cid, 0) or 0))
        ws.cell(row=row, column=4, value=int((stat.get("missing_total") or {}).get(cid, 0) or 0))
        ws.cell(row=row, column=5, value=int((stat.get("excess") or {}).get(cid, 0) or 0))
        row += 1

    return row + 2  # ligne suivante + espace

@apiRouter.get("/norms/{node_id}/tree/export")
async def export_norms_excel(node_id: str, db: AsyncSession = Depends(get_session)):
    report = await  normMethods.build_norm_tree_report(node_id, db)
    tree = report.get("tree") or []

    wb = Workbook()
    ws = wb.active
    ws.title = "Normes"

    # meta header
    node = report.get("node") or {}
    ws["A1"] = "Node"
    ws["B1"] = node.get("name")
    ws["A2"] = "Node ID"
    ws["B2"] = node.get("id")
    ws["A3"] = "Generated at"
    ws["B3"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    ws["A1"].font = ws["A2"].font = ws["A3"].font = Font(bold=True)

    r = 5

    # Si ton UI affiche seulement les racines -> même comportement
    classificationMap = await normMethods.db_get_classification_map(db)
    for org_unit in tree:
        r = _write_orgunit_table(ws, r,org_unit, classificationMap)

    _autofit(ws)

    # stream output
    bio = BytesIO()
    wb.save(bio)
    bio.seek(0)

    filename = f"norms_{node_id}.xlsx"
    return StreamingResponse(
        bio,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )