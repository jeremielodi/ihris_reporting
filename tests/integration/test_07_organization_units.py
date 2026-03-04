import pytest
import uuid
from helpers import load_mock

BASE = "/manage/organization_units"
mock = load_mock("org_unit")


@pytest.fixture(scope="module")
def state():
    """
    Shared state across tests in this module.
    Stores IDs created during tests so later tests can reuse them.
    """
    return {}


@pytest.fixture(scope="module")
def unique_suffix():
    """Stable random suffix for this module run."""
    return uuid.uuid4().hex[:8]


@pytest.mark.anyio
async def test_01_create_org_unit(api_context, auth_headers, state, unique_suffix):
    """
    POST /organization_units
    Creates an org unit and stores its id for subsequent tests.
    """
    payload = mock["org_unit"].copy()
    payload["name"] = f"{payload['name']}-{unique_suffix}"

    # The API requires name, and uses level to generate ID: orgUnit|<level>xxxxxx
    r = await api_context.post(BASE, json=payload, headers=auth_headers)
    assert r.status_code in (200, 201), r.text

    created = r.json()
    state["org_id"] = created["id"]
    state["org_name"] = created.get("name")
    state["org_level"] = created.get("level")
    state["org_parent"] = created.get("parent")

    assert state["org_id"].startswith("orgUnit|"), f"Unexpected ID format: {state['org_id']}"


@pytest.mark.anyio
async def test_02_get_all_org_units(api_context, auth_headers, state):
    """
    GET /organization_units
    Ensures created org unit exists in list.
    """
    r = await api_context.get(BASE, headers=auth_headers)
    assert r.status_code == 200, r.text

    items = r.json()
    assert any(x["id"] == state["org_id"] for x in items)


@pytest.mark.anyio
async def test_03_get_org_unit_by_id(api_context, auth_headers, state):
    """
    GET /organization_units/{id}
    Retrieves created org unit.
    """
    r = await api_context.get(f"{BASE}/{state['org_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["id"] == state["org_id"]


@pytest.mark.anyio
async def test_04_update_org_unit(api_context, auth_headers, state, unique_suffix):
    """
    PUT /organization_units/{org_id}
    Updates created org unit.
    """
    update_payload = mock["org_unit_update"].copy()

    # Update schema requires: id and name
    update_payload["id"] = state["org_id"]
    update_payload["name"] = f"{update_payload['name']}-{unique_suffix}"

    r = await api_context.put(
        f"{BASE}/{state['org_id']}",
        json=update_payload,
        headers=auth_headers
    )
    assert r.status_code == 200, r.text

    updated = r.json()
    assert updated["id"] == state["org_id"]
    state["org_name"] = updated.get("name")


@pytest.mark.anyio
async def test_05_get_children(api_context, auth_headers, state):
    """
    GET /organization_units/children/{parentId}
    Our created org unit has parent=None, so children list depends on DB state.
    Here we just check the endpoint works and returns a list.
    """
    parent_id = state["org_id"]
    r = await api_context.get(f"{BASE}/children/{parent_id}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert isinstance(r.json(), list)


@pytest.mark.anyio
async def test_06_get_tree(api_context, auth_headers, state):
    """
    GET /organization_units/tree/{parentId}
    Tree should at least include the root node itself.
    """
    r = await api_context.get(f"{BASE}/tree/{state['org_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text

    rows = r.json()
    assert isinstance(rows, list)
    assert len(rows) >= 1  # should include the start node


@pytest.mark.anyio
async def test_07_get_path(api_context, auth_headers, state):
    """
    GET /organization_units/path/{parentId}
    Path to root should return at least one row (the node).
    """
    r = await api_context.get(f"{BASE}/path/{state['org_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text

    rows = r.json()
    assert isinstance(rows, list)
    assert len(rows) >= 1


@pytest.mark.anyio
async def test_08_export_xlsx(api_context, auth_headers):
    """
    GET /organization_units/export/xlsx/
    Validates we receive an .xlsx stream.
    """
    r = await api_context.get(f"{BASE}/export/xlsx/", headers=auth_headers)
    assert r.status_code == 200, r.text

    # Content-Type for xlsx
    content_type = r.headers.get("content-type", "")
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in content_type

    # Should have attachment filename
    cd = r.headers.get("content-disposition", "")
    assert "attachment" in cd.lower()
    assert ".xlsx" in cd.lower()


@pytest.mark.anyio
async def test_09_import_org_units_json(api_context, auth_headers, unique_suffix):
    """
    POST /organization_units/import/json
    Imports org units from a JSON array.
    """
    payload = [x.copy() for x in mock["org_unit_import_json"]]

    # Ensure uniqueness across runs
    for item in payload:
        item["name"] = f"{item['name']}-{unique_suffix}-{uuid.uuid4().hex[:4]}"

    r = await api_context.post(f"{BASE}/import/json", json=payload, headers=auth_headers)
    assert r.status_code == 200, r.text

    data = r.json()
    assert data["message"] == "Import completed"
    assert data["imported_count"] >= 1


@pytest.mark.anyio
async def test_10_get_org_unit_404(api_context, auth_headers):
    """
    GET /organization_units/{id} with non-existing id should return 404.
    """
    fake_id = "orgUnit|9XXXXXXXXX"
    r = await api_context.get(f"{BASE}/{fake_id}", headers=auth_headers)
    assert r.status_code == 404