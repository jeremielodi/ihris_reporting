import pytest
import uuid
from helpers import load_mock

BASE = "/manage/cadres"   # adjust if your OpenAPI prefix is different
mock = load_mock("cadre")


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
async def test_01_create_cadre(api_context, auth_headers, state, unique_suffix):
    """
    POST /manage/cadres/
    Creates a cadre and stores its ID for subsequent tests.
    """
    payload = mock["cadre"].copy()
    payload["name"] = f"{payload['name']}-{unique_suffix}"

    r = await api_context.post(f"{BASE}/", json=payload, headers=auth_headers)
    assert r.status_code in (200, 201), r.text

    created = r.json()
    state["cadre_id"] = created["id"]
    state["cadre_name"] = created.get("name")

    assert state["cadre_id"].startswith("cadre|")


@pytest.mark.anyio
async def test_02_get_all_cadres(api_context, auth_headers, state):
    """
    GET /manage/cadres
    Ensures the created cadre exists in the list.
    """
    r = await api_context.get(BASE, headers=auth_headers)
    assert r.status_code == 200, r.text

    items = r.json()
    assert any(x["id"] == state["cadre_id"] for x in items)


@pytest.mark.anyio
async def test_03_get_cadre_by_id(api_context, auth_headers, state):
    """
    GET /manage/cadres/{id}
    Retrieves the created cadre.
    """
    r = await api_context.get(f"{BASE}/{state['cadre_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["id"] == state["cadre_id"]


@pytest.mark.anyio
async def test_04_update_cadre(api_context, auth_headers, state):
    """
    PUT /manage/cadres/{id}
    Updates the cadre.
    """
    update_payload = mock["cadre_update"].copy()

    # Keep the name stable (some systems derive ID from name)
    if state.get("cadre_name"):
        update_payload["name"] = state["cadre_name"]

    r = await api_context.put(
        f"{BASE}/{state['cadre_id']}",
        json=update_payload,
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    assert r.json().get("description") == mock["cadre_update"]["description"]


@pytest.mark.anyio
async def test_05_bulk_import_cadres(api_context, auth_headers, state):
    """
    POST /manage/cadres/import
    Bulk import cadres; ensures at least one record is inserted.
    """
    payload = [x.copy() for x in mock["cadre_bulk"]]

    # Make names unique to avoid collisions across test runs
    for item in payload:
        item["name"] = f"{item['name']}-{uuid.uuid4().hex[:6]}"

    r = await api_context.post(f"{BASE}/import", json=payload, headers=auth_headers)
    assert r.status_code == 201, r.text

    inserted = r.json()
    assert isinstance(inserted, list)
    assert len(inserted) >= 1

    # Optional: store one imported ID for later checks if needed
    state["bulk_one_id"] = inserted[0]["id"]


@pytest.mark.anyio
async def test_06_delete_cadre(api_context, auth_headers, state):
    """
    DELETE /manage/cadres/{id}
    Deletes the created cadre.
    """
    r = await api_context.delete(f"{BASE}/{state['cadre_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["detail"] == "Cadre deleted successfully"


@pytest.mark.anyio
async def test_07_get_deleted_cadre_returns_404(api_context, auth_headers, state):
    """
    GET /manage/cadres/{id} after delete should return 404.
    """
    r = await api_context.get(f"{BASE}/{state['cadre_id']}", headers=auth_headers)
    assert r.status_code == 404, r.text