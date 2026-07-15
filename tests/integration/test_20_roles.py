import pytest
import uuid
from helpers import load_mock

BASE = "/manage/roles"
mock = load_mock("role")


@pytest.fixture(scope="module")
def state():
    return {}


@pytest.fixture(scope="module")
def unique_suffix():
    return uuid.uuid4().hex[:8]


@pytest.mark.anyio
async def test_01_get_all_roles(api_context, auth_headers, state):
    """
    GET /manage/roles/
    """
    r = await api_context.get(f"{BASE}/", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert isinstance(r.json(), list)


@pytest.mark.anyio
async def test_02_create_role(api_context, auth_headers, state, unique_suffix):
    """
    POST /manage/roles/
    id is server-generated (role|<N>), not derived from name.
    """
    payload = mock["role"].copy()
    payload["name"] = f"{payload['name']}-{unique_suffix}"

    r = await api_context.post(f"{BASE}/", json=payload, headers=auth_headers)
    assert r.status_code in (200, 201), r.text

    created = r.json()
    state["role_id"] = created["id"]
    state["role_name"] = created["name"]

    assert state["role_id"].startswith("role|")
    assert created["name"] == payload["name"]


@pytest.mark.anyio
async def test_03_create_role_duplicate_name_returns_409(api_context, auth_headers, state):
    """
    POST /manage/roles/ with an existing name -> 409.
    """
    payload = mock["role"].copy()
    payload["name"] = state["role_name"]

    r = await api_context.post(f"{BASE}/", json=payload, headers=auth_headers)
    assert r.status_code == 409, r.text


@pytest.mark.anyio
async def test_04_get_role_by_id(api_context, auth_headers, state):
    """
    GET /manage/roles/{id}
    """
    r = await api_context.get(f"{BASE}/{state['role_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["id"] == state["role_id"]


@pytest.mark.anyio
async def test_05_update_role(api_context, auth_headers, state, unique_suffix):
    """
    PUT /manage/roles/{id}
    """
    update_payload = mock["role_update"].copy()
    update_payload["name"] = f"{update_payload['name']}-{unique_suffix}"

    r = await api_context.put(
        f"{BASE}/{state['role_id']}",
        json=update_payload,
        headers=auth_headers
    )
    assert r.status_code == 200, r.text
    assert r.json()["id"] == state["role_id"]
    assert r.json()["name"] == update_payload["name"]


@pytest.mark.anyio
async def test_06_delete_role(api_context, auth_headers, state):
    """
    DELETE /manage/roles/{id}
    """
    r = await api_context.delete(f"{BASE}/{state['role_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert "deleted" in (r.json().get("detail") or "").lower()


@pytest.mark.anyio
async def test_07_get_deleted_role_returns_404(api_context, auth_headers, state):
    """
    GET /manage/roles/{id} after delete -> 404.
    """
    r = await api_context.get(f"{BASE}/{state['role_id']}", headers=auth_headers)
    assert r.status_code == 404, r.text


@pytest.mark.anyio
async def test_08_get_role_404(api_context, auth_headers):
    """
    GET /manage/roles/{id} with fake id -> 404.
    """
    r = await api_context.get(f"{BASE}/role|NOT_EXISTS", headers=auth_headers)
    assert r.status_code == 404, r.text
