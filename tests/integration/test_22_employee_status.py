import pytest
import uuid
from helpers import load_mock

BASE = "/manage/employee_status"
mock = load_mock("employee_status")


@pytest.fixture(scope="module")
def state():
    return {}


@pytest.fixture(scope="module")
def unique_suffix():
    return uuid.uuid4().hex[:8]


@pytest.mark.anyio
async def test_01_get_all_employee_status(api_context, auth_headers, state):
    """
    GET /manage/employee_status/
    """
    r = await api_context.get(f"{BASE}/", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert isinstance(r.json(), list)


@pytest.mark.anyio
async def test_02_create_employee_status(api_context, auth_headers, state, unique_suffix):
    """
    POST /manage/employee_status/
    Unlike most reference tables, the id is NOT server-generated here - the
    client must supply a unique `id` directly (see create_employee_status).
    """
    payload = mock["employee_status"].copy()
    payload["id"] = f"employee_status|test-{unique_suffix}"
    payload["name"] = f"{payload['name']}-{unique_suffix}"

    r = await api_context.post(f"{BASE}/", json=payload, headers=auth_headers)
    assert r.status_code in (200, 201), r.text

    created = r.json()
    state["employee_status_id"] = created["id"]
    assert created["id"] == payload["id"]
    assert created["name"] == payload["name"]


@pytest.mark.anyio
async def test_03_create_employee_status_duplicate_id_returns_400(api_context, auth_headers, state):
    """
    POST /manage/employee_status/ with an existing id -> 400.
    """
    payload = mock["employee_status"].copy()
    payload["id"] = state["employee_status_id"]

    r = await api_context.post(f"{BASE}/", json=payload, headers=auth_headers)
    assert r.status_code == 400, r.text


@pytest.mark.anyio
async def test_04_get_employee_status_by_id(api_context, auth_headers, state):
    """
    GET /manage/employee_status/{id}
    """
    r = await api_context.get(f"{BASE}/{state['employee_status_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["id"] == state["employee_status_id"]


@pytest.mark.anyio
async def test_05_update_employee_status(api_context, auth_headers, state, unique_suffix):
    """
    PUT /manage/employee_status/{id}
    """
    update_payload = mock["employee_status_update"].copy()
    update_payload["name"] = f"{update_payload['name']}-{unique_suffix}"

    r = await api_context.put(
        f"{BASE}/{state['employee_status_id']}",
        json=update_payload,
        headers=auth_headers
    )
    assert r.status_code == 200, r.text
    assert r.json()["id"] == state["employee_status_id"]
    assert r.json()["name"] == update_payload["name"]


@pytest.mark.anyio
async def test_06_delete_employee_status(api_context, auth_headers, state):
    """
    DELETE /manage/employee_status/{id} -> 204 No Content.
    """
    r = await api_context.delete(f"{BASE}/{state['employee_status_id']}", headers=auth_headers)
    assert r.status_code == 204, r.text


@pytest.mark.anyio
async def test_07_get_deleted_employee_status_returns_404(api_context, auth_headers, state):
    """
    GET /manage/employee_status/{id} after delete -> 404.
    """
    r = await api_context.get(f"{BASE}/{state['employee_status_id']}", headers=auth_headers)
    assert r.status_code == 404, r.text


@pytest.mark.anyio
async def test_08_get_employee_status_404(api_context, auth_headers):
    """
    GET /manage/employee_status/{id} with fake id -> 404.
    """
    r = await api_context.get(f"{BASE}/employee_status|NOT_EXISTS", headers=auth_headers)
    assert r.status_code == 404, r.text
