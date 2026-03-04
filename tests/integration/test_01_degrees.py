import pytest
import uuid
from helpers import load_mock

BASE = "/manage/degrees"
mock = load_mock("degree")


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
async def test_01_create_degree(api_context, auth_headers, state, unique_suffix):
    """
    POST /manage/degrees/
    Creates a degree and stores its ID for subsequent tests.
    """
    payload = mock["degree"].copy()
    payload["name"] = f"{payload['name']}-{unique_suffix}"

    r = await api_context.post(f"{BASE}/", json=payload, headers=auth_headers)
    assert r.status_code in (200, 201), r.text

    created = r.json()
    state["degree_id"] = created["id"]
    state["degree_name"] = created["name"]

    assert state["degree_id"].startswith("degree|")
    assert created["name"] == state["degree_name"]


@pytest.mark.anyio
async def test_02_get_all_degrees(api_context, auth_headers, state):
    """
    GET /manage/degrees
    Ensures the created degree exists in the list.
    """
    r = await api_context.get(BASE, headers=auth_headers)
    assert r.status_code == 200, r.text

    items = r.json()
    assert any(x["id"] == state["degree_id"] for x in items)


@pytest.mark.anyio
async def test_03_get_degree_by_id(api_context, auth_headers, state):
    """
    GET /manage/degrees/{id}
    Retrieves the created degree.
    """
    r = await api_context.get(f"{BASE}/{state['degree_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["id"] == state["degree_id"]


@pytest.mark.anyio
async def test_04_update_degree(api_context, auth_headers, state):
    """
    PUT /manage/degrees/{id}
    Updates the degree.
    NOTE: Keep the name stable if your system derives ID from name.
    """
    update_payload = mock["degree_update"].copy()
    update_payload["name"] = state["degree_name"]

    r = await api_context.put(
        f"{BASE}/{state['degree_id']}",
        json=update_payload,
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text


@pytest.mark.anyio
async def test_05_delete_degree(api_context, auth_headers, state):
    """
    DELETE /manage/degrees/{id}
    Deletes the created degree.
    """
    r = await api_context.delete(f"{BASE}/{state['degree_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text


@pytest.mark.anyio
async def test_06_get_deleted_degree_returns_404(api_context, auth_headers, state):
    """
    GET /manage/degrees/{id} after delete should return 404.
    """
    r = await api_context.get(f"{BASE}/{state['degree_id']}", headers=auth_headers)
    assert r.status_code == 404, r.text