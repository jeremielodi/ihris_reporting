import pytest
import uuid
from helpers import load_mock

BASE = "/manage/reason_departures"
mock = load_mock("reason_departure")


@pytest.fixture(scope="module")
def state():
    return {}


@pytest.fixture(scope="module")
def unique_suffix():
    return uuid.uuid4().hex[:8]


@pytest.mark.anyio
async def test_01_get_all_reason_departures(api_context, auth_headers, state):
    r = await api_context.get(f"{BASE}/", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert isinstance(r.json(), list)


@pytest.mark.anyio
async def test_02_create_reason_departure(api_context, auth_headers, state, unique_suffix):
    """id is derived from name: reason_departure|<name>."""
    payload = mock["reason_departure"].copy()
    payload["name"] = f"{payload['name']}-{unique_suffix}"

    r = await api_context.post(f"{BASE}/", json=payload, headers=auth_headers)
    assert r.status_code in (200, 201), r.text

    created = r.json()
    state["reason_departure_id"] = created["id"]
    assert state["reason_departure_id"] == f"reason_departure|{payload['name']}"


@pytest.mark.anyio
async def test_03_get_reason_departure_by_id(api_context, auth_headers, state):
    r = await api_context.get(f"{BASE}/{state['reason_departure_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["id"] == state["reason_departure_id"]


@pytest.mark.anyio
async def test_04_update_reason_departure(api_context, auth_headers, state):
    update_payload = mock["reason_departure_update"].copy()

    r = await api_context.put(
        f"{BASE}/{state['reason_departure_id']}",
        json=update_payload,
        headers=auth_headers
    )
    assert r.status_code == 200, r.text
    assert r.json()["id"] == state["reason_departure_id"]
    assert r.json()["code"] == update_payload["code"]


@pytest.mark.anyio
async def test_05_delete_reason_departure(api_context, auth_headers, state):
    r = await api_context.delete(f"{BASE}/{state['reason_departure_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert "deleted" in (r.json().get("detail") or "").lower()


@pytest.mark.anyio
async def test_06_get_deleted_reason_departure_returns_404(api_context, auth_headers, state):
    r = await api_context.get(f"{BASE}/{state['reason_departure_id']}", headers=auth_headers)
    assert r.status_code == 404, r.text


@pytest.mark.anyio
async def test_07_get_reason_departure_404(api_context, auth_headers):
    r = await api_context.get(f"{BASE}/reason_departure|NOT_EXISTS", headers=auth_headers)
    assert r.status_code == 404, r.text
