import pytest
import uuid
from helpers import load_mock

BASE = "/manage/identification_types"
mock = load_mock("identification_type")


@pytest.fixture(scope="module")
def state():
    """
    Shared state across tests in this module.
    Stores created identification_type_id for later tests.
    """
    return {}


@pytest.fixture(scope="module")
def unique_suffix():
    return uuid.uuid4().hex[:8]


@pytest.mark.anyio
async def test_01_create_identification_type(api_context, auth_headers, state, unique_suffix):
    """
    POST /manage/identification_types/
    Creates an identification type and stores its id for subsequent tests.
    """
    payload = mock["identification_type"].copy()
    payload["name"] = f"{payload['name']}-{unique_suffix}"

    r = await api_context.post(f"{BASE}/", json=payload, headers=auth_headers)
    assert r.status_code in (200, 201), r.text

    created = r.json()
    state["identification_type_id"] = created["id"]
    state["identification_type_name"] = created.get("name")

    assert state["identification_type_id"].startswith("identification_type|")


@pytest.mark.anyio
async def test_02_get_all_identification_types(api_context, auth_headers, state):
    """
    GET /manage/identification_types/
    Ensures created identification type exists in list.
    """
    r = await api_context.get(f"{BASE}/", headers=auth_headers)
    assert r.status_code == 200, r.text

    items = r.json()
    assert isinstance(items, list)
    assert any(x["id"] == state["identification_type_id"] for x in items)


@pytest.mark.anyio
async def test_03_get_identification_type_by_id(api_context, auth_headers, state):
    """
    GET /manage/identification_types/{id}
    Retrieves created identification type by id.
    """
    r = await api_context.get(
        f"{BASE}/{state['identification_type_id']}",
        headers=auth_headers
    )
    assert r.status_code == 200, r.text
    assert r.json()["id"] == state["identification_type_id"]


@pytest.mark.anyio
async def test_04_update_identification_type(api_context, auth_headers, state):
    """
    PUT /manage/identification_types/{id}
    Updates created identification type.
    NOTE: keep name stable (id was built from name at creation time).
    """
    update_payload = mock["identification_type_update"].copy()
    update_payload["name"] = state["identification_type_name"]

    r = await api_context.put(
        f"{BASE}/{state['identification_type_id']}",
        json=update_payload,
        headers=auth_headers
    )
    assert r.status_code == 200, r.text

    updated = r.json()
    assert updated["id"] == state["identification_type_id"]
    assert updated.get("code") == mock["identification_type_update"]["code"]


@pytest.mark.anyio
async def test_05_delete_identification_type(api_context, auth_headers, state):
    """
    DELETE /manage/identification_types/{id}
    Deletes created identification type.
    """
    r = await api_context.delete(
        f"{BASE}/{state['identification_type_id']}",
        headers=auth_headers
    )
    assert r.status_code == 200, r.text
    assert "deleted" in (r.json().get("detail") or "").lower()


@pytest.mark.anyio
async def test_06_get_deleted_identification_type_returns_404(api_context, auth_headers, state):
    """
    GET /manage/identification_types/{id} after delete -> 404
    """
    r = await api_context.get(
        f"{BASE}/{state['identification_type_id']}",
        headers=auth_headers
    )
    assert r.status_code == 404, r.text


@pytest.mark.anyio
async def test_07_get_identification_type_404(api_context, auth_headers):
    """
    GET /manage/identification_types/{id} with fake id -> 404
    """
    fake_id = "identification_type|NOT_EXISTS"
    r = await api_context.get(f"{BASE}/{fake_id}", headers=auth_headers)
    assert r.status_code == 404, r.text