import pytest
import uuid
from helpers import load_mock

BASE = "/manage/institution_types"
mock = load_mock("institution_type")


@pytest.fixture(scope="module")
def state():
    """
    Shared state across tests in this module.
    Stores created institution_type_id for later tests.
    """
    return {}


@pytest.fixture(scope="module")
def unique_suffix():
    return uuid.uuid4().hex[:8]


@pytest.mark.anyio
async def test_01_create_institution_type(api_context, auth_headers, state, unique_suffix):
    """
    POST /manage/institution_types/
    Creates an institution type and stores its id for subsequent tests.
    """
    payload = mock["institution_type"].copy()
    payload["name"] = f"{payload['name']}-{unique_suffix}"

    r = await api_context.post(f"{BASE}/", json=payload, headers=auth_headers)
    assert r.status_code in (200, 201), r.text

    created = r.json()
    state["institution_type_id"] = created["id"]
    state["institution_type_name"] = created.get("name")

    assert state["institution_type_id"].startswith("institution_type|")


@pytest.mark.anyio
async def test_02_get_all_institution_types(api_context, auth_headers, state):
    """
    GET /manage/institution_types/
    Ensures created institution type exists in list.
    """
    r = await api_context.get(f"{BASE}/", headers=auth_headers)
    assert r.status_code == 200, r.text

    items = r.json()
    assert isinstance(items, list)
    assert any(x["id"] == state["institution_type_id"] for x in items)


@pytest.mark.anyio
async def test_03_get_institution_type_by_id(api_context, auth_headers, state):
    """
    GET /manage/institution_types/{id}
    Retrieves created institution type by id.
    """
    r = await api_context.get(f"{BASE}/{state['institution_type_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["id"] == state["institution_type_id"]


@pytest.mark.anyio
async def test_04_update_institution_type(api_context, auth_headers, state):
    """
    PUT /manage/institution_types/{id}
    Updates created institution type.
    NOTE: keep name stable (id was built from name at creation time).
    """
    update_payload = mock["institution_type_update"].copy()
    update_payload["name"] = state["institution_type_name"]

    r = await api_context.put(
        f"{BASE}/{state['institution_type_id']}",
        json=update_payload,
        headers=auth_headers
    )
    assert r.status_code == 200, r.text

    updated = r.json()
    assert updated["id"] == state["institution_type_id"]
    assert updated.get("code") == mock["institution_type_update"]["code"]


@pytest.mark.anyio
async def test_05_delete_institution_type(api_context, auth_headers, state):
    """
    DELETE /manage/institution_types/{id}
    Deletes created institution type.
    """
    r = await api_context.delete(f"{BASE}/{state['institution_type_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text

    data = r.json()
    assert "deleted" in (data.get("detail") or "").lower()


@pytest.mark.anyio
async def test_06_get_deleted_institution_type_returns_404(api_context, auth_headers, state):
    """
    GET /manage/institution_types/{id} after delete -> 404
    """
    r = await api_context.get(f"{BASE}/{state['institution_type_id']}", headers=auth_headers)
    assert r.status_code == 404, r.text


@pytest.mark.anyio
async def test_07_get_institution_type_404(api_context, auth_headers):
    """
    GET /manage/institution_types/{id} with fake id -> 404
    """
    fake_id = "institution_type|NOT_EXISTS"
    r = await api_context.get(f"{BASE}/{fake_id}", headers=auth_headers)
    assert r.status_code == 404, r.text