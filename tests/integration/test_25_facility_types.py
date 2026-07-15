import pytest
import uuid
from helpers import load_mock

BASE = "/manage/facility_types"
mock = load_mock("facility_type")


@pytest.fixture(scope="module")
def state():
    return {}


@pytest.fixture(scope="module")
def unique_suffix():
    return uuid.uuid4().hex[:8]


@pytest.mark.anyio
async def test_01_get_all_facility_types(api_context, auth_headers, state):
    r = await api_context.get(f"{BASE}/", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert isinstance(r.json(), list)


@pytest.mark.anyio
async def test_02_create_facility_type(api_context, auth_headers, state, unique_suffix):
    """id is derived from name: facility_type|<name>."""
    payload = mock["facility_type"].copy()
    payload["name"] = f"{payload['name']}-{unique_suffix}"

    r = await api_context.post(f"{BASE}/", json=payload, headers=auth_headers)
    assert r.status_code in (200, 201), r.text

    created = r.json()
    state["facility_type_id"] = created["id"]
    assert state["facility_type_id"] == f"facility_type|{payload['name']}"


@pytest.mark.anyio
async def test_03_get_facility_type_by_id(api_context, auth_headers, state):
    r = await api_context.get(f"{BASE}/{state['facility_type_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["id"] == state["facility_type_id"]


@pytest.mark.anyio
async def test_04_update_facility_type(api_context, auth_headers, state):
    update_payload = mock["facility_type_update"].copy()

    r = await api_context.put(
        f"{BASE}/{state['facility_type_id']}",
        json=update_payload,
        headers=auth_headers
    )
    assert r.status_code == 200, r.text
    assert r.json()["id"] == state["facility_type_id"]
    assert r.json()["code"] == update_payload["code"]


@pytest.mark.anyio
async def test_05_delete_facility_type(api_context, auth_headers, state):
    r = await api_context.delete(f"{BASE}/{state['facility_type_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert "deleted" in (r.json().get("detail") or "").lower()


@pytest.mark.anyio
async def test_06_get_deleted_facility_type_returns_404(api_context, auth_headers, state):
    r = await api_context.get(f"{BASE}/{state['facility_type_id']}", headers=auth_headers)
    assert r.status_code == 404, r.text


@pytest.mark.anyio
async def test_07_get_facility_type_404(api_context, auth_headers):
    r = await api_context.get(f"{BASE}/facility_type|NOT_EXISTS", headers=auth_headers)
    assert r.status_code == 404, r.text
