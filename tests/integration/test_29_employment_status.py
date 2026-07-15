import pytest
import uuid
from helpers import load_mock

BASE = "/manage/employment_status"
mock = load_mock("employment_status")


@pytest.fixture(scope="module")
def state():
    return {}


@pytest.fixture(scope="module")
def unique_suffix():
    return uuid.uuid4().hex[:8]


@pytest.mark.anyio
async def test_01_get_all_employment_status(api_context, auth_headers, state):
    r = await api_context.get(f"{BASE}/", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert isinstance(r.json(), list)


@pytest.mark.anyio
async def test_02_create_employment_status(api_context, auth_headers, state, unique_suffix):
    """id is derived from name: employment_status|<name>."""
    payload = mock["employment_status"].copy()
    payload["name"] = f"{payload['name']}-{unique_suffix}"

    r = await api_context.post(f"{BASE}/", json=payload, headers=auth_headers)
    assert r.status_code in (200, 201), r.text

    created = r.json()
    state["employment_status_id"] = created["id"]
    assert state["employment_status_id"] == f"employment_status|{payload['name']}"


@pytest.mark.anyio
async def test_03_get_employment_status_by_id(api_context, auth_headers, state):
    r = await api_context.get(f"{BASE}/{state['employment_status_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["id"] == state["employment_status_id"]


@pytest.mark.anyio
async def test_04_update_employment_status(api_context, auth_headers, state):
    update_payload = mock["employment_status_update"].copy()

    r = await api_context.put(
        f"{BASE}/{state['employment_status_id']}",
        json=update_payload,
        headers=auth_headers
    )
    assert r.status_code == 200, r.text
    assert r.json()["id"] == state["employment_status_id"]
    assert r.json()["code"] == update_payload["code"]


@pytest.mark.anyio
async def test_05_delete_employment_status(api_context, auth_headers, state):
    r = await api_context.delete(f"{BASE}/{state['employment_status_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert "deleted" in (r.json().get("detail") or "").lower()


@pytest.mark.anyio
async def test_06_get_deleted_employment_status_returns_404(api_context, auth_headers, state):
    r = await api_context.get(f"{BASE}/{state['employment_status_id']}", headers=auth_headers)
    assert r.status_code == 404, r.text


@pytest.mark.anyio
async def test_07_get_employment_status_404(api_context, auth_headers):
    r = await api_context.get(f"{BASE}/employment_status|NOT_EXISTS", headers=auth_headers)
    assert r.status_code == 404, r.text
