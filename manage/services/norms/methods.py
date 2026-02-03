from __future__ import annotations

from sqlalchemy import text
from typing import Any, Dict, List, Optional, Tuple
import copy

from sqlalchemy.ext.asyncio import AsyncSession
from manage.services.organization_units import methods as orgUnitMethods

# --- à remplacer par tes requêtes DB ---
async def db_list_facilities(db) -> list[dict]:
    """
    return [{"id": "...", "name": "...", "parent": "..."}]
    """
    ...

    result = await db.execute(text("""
        SELECT ou.id, ou.name, ou.parent
        FROM organization_unit ou
        LEFT JOIN organization_unit child ON child.parent = ou.id
        WHERE child.id IS NULL
        AND ou.level = 'facility';                                    
    """))

    rows = result.mappings().all()
    return rows

async def db_get_organization_unit_type_id(facility_id: str, db) -> str:
    result = await db.execute(text("""
        SELECT o.type
        FROM organization_unit o
        WHERE o.id = :id
    """), {"id": facility_id})

    row = result.first()
    typeId =  'CS_RURAL'
    if row is not None :
        if row[0] is not None :
            typeId = row[0]
    
    return typeId


async def db_get_norms(organization_unit_type_id: str, db) -> dict[str, int]:
    result = await db.execute(text("""
        SELECT nr.classification_id, nr.required, cl.name
        FROM public.norm_requirement nr
        JOIN hippo_classification cl ON cl.id = nr.classification_id
        WHERE nr.organization_unit_type_id = :organization_unit_type_id
        ORDER BY nr.classification_id ASC
    """), {"organization_unit_type_id": organization_unit_type_id})

    rows = result.mappings().all()
    return {r["classification_id"]: r["required"] for r in rows}


async def db_get_actual_staff(facility_id: str, db) -> dict[str, int]:
    result = await db.execute(text("""
        SELECT t1.classification_id , COUNT(t1.classification_id) as qty
        FROM z_employment_status_view t1
        WHERE t1.facility_id = :id AND t1.classification_id IS NOT NULL
        GROUP BY t1.classification_id
    """), {"id": facility_id})

    rows = result.mappings().all()
    return {r["classification_id"]: r["qty"] for r in rows}


async def db_get_children(parent_id: str, db) -> list[dict]:
    result = await db.execute(text("""
        SELECT id, name, level, parent
        FROM organization_unit
        WHERE parent = :parent_id
    """), {"parent_id": parent_id})

    return result.mappings().all()

async def db_list_descendant_facilities(node_id: str, db) -> list[str]:
    result = await db.execute(text("""
        WITH RECURSIVE tree AS (
            SELECT id, parent, level
            FROM organization_unit
            WHERE id = :id

            UNION ALL

            SELECT c.id, c.parent, c.level
            FROM organization_unit c
            JOIN tree t ON c.parent = t.id
        )
        SELECT id
        FROM tree
        WHERE level = 'facility'
    """), {"id": node_id})

    return [r["id"] for r in result.mappings().all()]

def compute_facility(required: dict[str, int], actual: dict[str, int]) -> dict:
    missing = {}
    excess = {}

    required_total = 0
    covered_total = 0  # sum(min(actual, required))
    actualList = {}

    for classification_id, req in required.items():
        act = int(actual.get(classification_id, 0))
        missing[classification_id] = max(req - act, 0)
        excess[classification_id] = max(act - req, 0)
        
        required_total += req
        covered_total += min(act, req)

    compliance_ratio = (covered_total / required_total) if required_total > 0 else 1.0

    return {
        "missing": missing,
        "excess": excess,
        "actual": actual,
        "required": required,
        "compliance_ratio": compliance_ratio,
    }


def sum_dicts(dicts: list[dict[str, int]]) -> dict[str, int]:
    out: dict[str, int] = {}
    for d in dicts:
        for k, v in d.items():
            out[k] = out.get(k, 0) + int(v)
    return out


def _to_float(v: Any) -> float:
    try:
        return float(v or 0)
    except Exception:
        return 0.0


def _add_dict_in_place(target: Dict[str, float], src: Optional[Dict[str, Any]]) -> None:
    """Somme src dans target, clé par clé (ex: classification|4)."""
    if not src:
        return
    for k, v in src.items():
        target[k] = target.get(k, 0.0) + _to_float(v)


def _ensure_stat_shape(stat: Optional[dict]) -> dict:
    stat = stat or {}
    return {
        "profile": stat.get("profile"),
        "required": dict(stat.get("required") or {}),
        "actual": dict(stat.get("actual") or {}),
        "missing_total": dict(stat.get("missing_total") or {}),
        "excess": dict(stat.get("excess") or {}),
        "compliance_ratio": stat.get("compliance_ratio"),
    }


def _compute_ratio(required: Dict[str, float], actual: Dict[str, float]) -> float:
    """ratio = sum(min(actual, required)) / sum(required)"""
    required_total = 0.0
    covered_total = 0.0
    for k, req in required.items():
        r = _to_float(req)
        a = _to_float(actual.get(k, 0))
        required_total += r
        covered_total += min(a, r)
    return (covered_total / required_total) if required_total > 0 else 1.0


def _merge_parent_with_children(parent_stat: Optional[dict], children_stats: List[dict]) -> dict:
    """
    Fusionne stat parent + somme stat enfants sans perdre les classifications du parent.
    """
    base = _ensure_stat_shape(parent_stat)

    required: Dict[str, float] = {k: _to_float(v) for k, v in base["required"].items()}
    actual: Dict[str, float] = {k: _to_float(v) for k, v in base["actual"].items()}
    missing_total: Dict[str, float] = {k: _to_float(v) for k, v in base["missing_total"].items()}
    excess: Dict[str, float] = {k: _to_float(v) for k, v in base["excess"].items()}

    for st in children_stats:
        stn = _ensure_stat_shape(st)
        _add_dict_in_place(required, stn["required"])
        _add_dict_in_place(actual, stn["actual"])
        _add_dict_in_place(missing_total, stn["missing_total"])
        _add_dict_in_place(excess, stn["excess"])

    ratio = _compute_ratio(required, actual)

    return {
        "profile": base["profile"] or "AGGREGATED",
        "required": required,
        "actual": actual,
        "missing_total": missing_total,
        "excess": excess,
        "compliance_ratio": ratio,
    }


def build_nested_tree_and_rollup_stats(
    flat_nodes: List[dict],
    *,
    items_key: str = "items",
    keep_original_order: bool = True
) -> List[dict]:
    """
    1) Construit node[items_key] = [children...]
    2) Calcule les stats des parents en partant des feuilles (post-order traversal).
       - Conserve les stats déjà existantes du parent (parent-only keys)
       - Ajoute les stats des enfants
       - Recalcule compliance_ratio

    Retourne une liste de racines (forest).
    """
    nodes = copy.deepcopy(flat_nodes)

    # Index
    by_id: Dict[str, dict] = {}
    for n in nodes:
        nid = n["id"]
        n.setdefault(items_key, [])
        by_id[nid] = n

    # Link parent->children
    roots: List[dict] = []
    for n in nodes:
        pid = n.get("parent")
        if pid and pid in by_id:
            by_id[pid].setdefault(items_key, []).append(n)
        else:
            roots.append(n)

    # Optionnel: conserver l'ordre d'entrée pour les enfants
    if keep_original_order:
        order = {n["id"]: i for i, n in enumerate(nodes)}

        def _sort_children(node: dict) -> None:
            node[items_key].sort(key=lambda c: order.get(c["id"], 10**18))
            for c in node[items_key]:
                _sort_children(c)

        for r in roots:
            _sort_children(r)

    # Post-order traversal: calc stats children -> parent
    def dfs(node: dict) -> dict:
        children = node.get(items_key, [])
        child_stats: List[dict] = []

        for ch in children:
            st = dfs(ch)  # calc child first
            if st is not None:
                child_stats.append(st)

        # feuille: si stat absent, init minimal (tu peux changer la règle)
        if not children:
            if node.get("stat") is None:
                node["stat"] = {
                    "profile": "LEAF",
                    "required": {},
                    "actual": {},
                    "missing_total": {},
                    "excess": {},
                    "compliance_ratio": 1.0,
                }
            else:
                # normaliser actual si None -> {}
                stn = _ensure_stat_shape(node["stat"])
                stn["actual"] = stn["actual"] or {}
                node["stat"] = stn
            return node["stat"]

        # parent: merge son stat + stats enfants
        node["stat"] = _merge_parent_with_children(node.get("stat"), child_stats)
        return node["stat"]

    for r in roots:
        dfs(r)

    return roots



async def build_norm_tree_report(node_id: str, db: AsyncSession) -> dict:
    facility_ids = await db_list_descendant_facilities(node_id, db)

    if len(facility_ids) == 0:
        facility = await orgUnitMethods.get_OrganisationUnit(node_id, db)
        facility_ids = [facility]

    required_list = []
    actual_list = []
    facility_summaries = {}

    for fid in facility_ids:
        profile = await db_get_organization_unit_type_id(fid, db)
        required = await db_get_norms(profile, db)
        actual = await db_get_actual_staff(fid, db)

        required_list.append(required)
        actual_list.append(actual)

        fac_calc = compute_facility(required, actual)
        facility_summaries[fid] = {
            "profile": profile,
            "compliance_ratio": fac_calc["compliance_ratio"],
            "missing_total": fac_calc["missing"],
            "actual": fac_calc["actual"],
            "required": fac_calc["required"],
            "excess": fac_calc["excess"],
        }

    required_sum = sum_dicts(required_list)
    actual_sum = sum_dicts(actual_list)
    node_calc = compute_facility(required_sum, actual_sum)

    orgUnitTree = await orgUnitMethods.get_OrganisationUnitTree(node_id, db)

    listOrgUpdated = []
    for orgUnit in orgUnitTree:
        facilityStat = facility_summaries.get(orgUnit["id"])
        orgUpdated = {
            "id": orgUnit["id"],
            "name": orgUnit["name"],
            "parent": orgUnit["parent"],
            "level": orgUnit["level"],
        }
        if facilityStat is not None:
            orgUpdated["stat"] = facilityStat
        listOrgUpdated.append(orgUpdated)

    return {
        "node": await orgUnitMethods.get_OrganisationUnit(node_id, db),
        "compliance_ratio": node_calc["compliance_ratio"],
        "excess": node_calc["excess"],
        "required": node_calc["required"],
        "missing": node_calc["missing"],
        "tree": build_nested_tree_and_rollup_stats(listOrgUpdated),
    }

async def db_get_classification_map(db: AsyncSession) -> dict:
    result = await db.execute(text("""
        SELECT id, name
        FROM hippo_classification
    """))
    rows = result.mappings().all()
    return {r["id"]: {"id": r["id"], "name": r["name"]} for r in rows}