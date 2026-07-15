import pytest
import uuid
from helpers import load_mock

BASE = "/manage/facilities"
mock = load_mock("facility")


@pytest.fixture(scope="module")
def state():
    return {}


@pytest.fixture(scope="module")
def unique_suffix():
    return uuid.uuid4().hex[:8]


@pytest.mark.anyio
async def test_01_get_all_facilities(api_context, auth_headers, state):
    """
    GET /manage/facilities/
    """
    r = await api_context.get(f"{BASE}/", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert isinstance(r.json(), list)


@pytest.mark.anyio
async def test_02_create_facility(api_context, auth_headers, state, unique_suffix):
    """
    POST /manage/facilities/
    id is derived from name: facility|<name>.
    """
    payload = mock["facility"].copy()
    payload["name"] = f"{payload['name']}-{unique_suffix}"

    r = await api_context.post(f"{BASE}/", json=payload, headers=auth_headers)
    assert r.status_code in (200, 201), r.text

    created = r.json()
    state["facility_id"] = created["id"]
    assert state["facility_id"] == f"facility|{payload['name']}"


@pytest.mark.anyio
async def test_03_get_facility_by_id(api_context, auth_headers, state):
    """
    GET /manage/facilities/{id}
    """
    r = await api_context.get(f"{BASE}/{state['facility_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["id"] == state["facility_id"]


@pytest.mark.anyio
async def test_04_update_facility(api_context, auth_headers, state):
    """
    PUT /manage/facilities/{id}
    HippoFacilityUpdate requires facility_type.
    """
    update_payload = mock["facility_update"].copy()

    r = await api_context.put(
        f"{BASE}/{state['facility_id']}",
        json=update_payload,
        headers=auth_headers
    )
    assert r.status_code == 200, r.text
    assert r.json()["id"] == state["facility_id"]
    assert r.json()["facility_type"] == update_payload["facility_type"]


@pytest.mark.anyio
async def test_05_delete_facility(api_context, auth_headers, state):
    """
    DELETE /manage/facilities/{id}
    """
    r = await api_context.delete(f"{BASE}/{state['facility_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert "deleted" in (r.json().get("detail") or "").lower()


@pytest.mark.anyio
async def test_06_get_deleted_facility_returns_404(api_context, auth_headers, state):
    """
    GET /manage/facilities/{id} after delete -> 404.
    """
    r = await api_context.get(f"{BASE}/{state['facility_id']}", headers=auth_headers)
    assert r.status_code == 404, r.text


@pytest.mark.anyio
async def test_07_get_facility_404(api_context, auth_headers):
    """
    GET /manage/facilities/{id} with fake id -> 404.
    """
    r = await api_context.get(f"{BASE}/facility|NOT_EXISTS", headers=auth_headers)
    assert r.status_code == 404, r.text
