import pytest
import uuid
from helpers import load_mock

BASE = "/manage/marital_status"
mock = load_mock("marital_status")


@pytest.fixture(scope="module")
def state():
    """
    Shared state across tests in this module.
    Stores created marital_status_id so later tests can reuse it.
    """
    return {}


@pytest.fixture(scope="module")
def unique_suffix():
    return uuid.uuid4().hex[:8]


@pytest.mark.anyio
async def test_01_get_all_marital_status_public(api_context, auth_headers, state):
    """
    GET /manage/marital_status/
    The route itself has no auth dependency, but everything under /manage
    is wrapped with router-level auth as defense-in-depth (see main.py),
    so a valid token is still required.
    """
    r = await api_context.get(f"{BASE}/", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert isinstance(r.json(), list)


@pytest.mark.anyio
async def test_02_create_marital_status(api_context, auth_headers, state, unique_suffix):
    """
    POST /manage/marital_status/
    Requires auth. Creates an item and stores its id.
    """
    payload = mock["marital_status"].copy()
    payload["name"] = f"{payload['name']}-{unique_suffix}"

    r = await api_context.post(f"{BASE}/", json=payload, headers=auth_headers)
    assert r.status_code in (200, 201), r.text

    created = r.json()
    state["marital_status_id"] = created["id"]
    state["marital_status_name"] = created["name"]

    assert state["marital_status_id"].startswith("marital_status|")


@pytest.mark.anyio
async def test_03_get_marital_status_by_id(api_context, auth_headers, state):
    """
    GET /manage/marital_status/{id}
    Requires auth.
    """
    r = await api_context.get(f"{BASE}/{state['marital_status_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["id"] == state["marital_status_id"]


@pytest.mark.anyio
async def test_04_update_marital_status(api_context, auth_headers, state):
    """
    PUT /manage/marital_status/{id}
    Requires auth. Updates the record.
    NOTE: changing name does NOT update the ID in this implementation.
    """
    update_payload = mock["marital_status_update"].copy()
    update_payload["name"] = f"{update_payload['name']}-{uuid.uuid4().hex[:4]}"

    r = await api_context.put(
        f"{BASE}/{state['marital_status_id']}",
        json=update_payload,
        headers=auth_headers
    )
    assert r.status_code == 200, r.text
    assert r.json()["id"] == state["marital_status_id"]
    assert r.json()["name"] == update_payload["name"]


@pytest.mark.anyio
async def test_05_delete_marital_status(api_context, auth_headers, state):
    """
    DELETE /manage/marital_status/{id}
    Requires auth.
    """
    r = await api_context.delete(f"{BASE}/{state['marital_status_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert "deleted" in (r.json().get("detail") or "").lower()


@pytest.mark.anyio
async def test_06_get_deleted_marital_status_returns_404(api_context, auth_headers, state):
    """
    GET /manage/marital_status/{id} after delete -> 404.
    """
    r = await api_context.get(f"{BASE}/{state['marital_status_id']}", headers=auth_headers)
    assert r.status_code == 404, r.text


@pytest.mark.anyio
async def test_07_get_marital_status_404(api_context, auth_headers):
    """
    GET /manage/marital_status/{id} with fake id -> 404.
    """
    fake_id = "marital_status|NOT_EXISTS"
    r = await api_context.get(f"{BASE}/{fake_id}", headers=auth_headers)
    assert r.status_code == 404, r.text