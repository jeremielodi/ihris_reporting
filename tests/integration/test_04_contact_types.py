import pytest
import uuid
from helpers import load_mock

BASE = "/manage/contact_types"
mock = load_mock("contact_type")


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
async def test_01_create_contact_type(api_context, auth_headers, state, unique_suffix):
    """
    POST /manage/contact_types/
    Creates a contact type and stores its ID for subsequent tests.
    """
    payload = mock["contact_type"].copy()
    payload["name"] = f"{payload['name']}-{unique_suffix}"

    r = await api_context.post(f"{BASE}/", json=payload, headers=auth_headers)
    assert r.status_code in (200, 201), r.text

    created = r.json()
    state["contact_type_id"] = created["id"]
    state["contact_type_name"] = created.get("name")

    assert state["contact_type_id"].startswith("contact_type|")


@pytest.mark.anyio
async def test_02_get_all_contact_types(api_context, auth_headers, state):
    """
    GET /manage/contact_types
    Ensures the created contact type exists in the list.
    """
    r = await api_context.get(BASE, headers=auth_headers)
    assert r.status_code == 200, r.text

    items = r.json()
    assert any(x["id"] == state["contact_type_id"] for x in items)


@pytest.mark.anyio
async def test_03_get_contact_type_by_id(api_context, auth_headers, state):
    """
    GET /manage/contact_types/{id}
    Retrieves the created contact type.
    """
    r = await api_context.get(f"{BASE}/{state['contact_type_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["id"] == state["contact_type_id"]


@pytest.mark.anyio
async def test_04_update_contact_type(api_context, auth_headers, state):
    """
    PUT /manage/contact_types/{id}
    Updates the contact type (only non-null fields).
    NOTE: If your API derives ID from name, keep name stable.
    Here we DO update the name because your update endpoint allows it.
    """
    update_payload = mock["contact_type_update"].copy()

    # If you want to keep ID stable, comment the next line and keep old name:
    update_payload["name"] = update_payload["name"] + "-" + uuid.uuid4().hex[:4]

    r = await api_context.put(
        f"{BASE}/{state['contact_type_id']}",
        json=update_payload,
        headers=auth_headers
    )
    assert r.status_code == 200, r.text

    updated = r.json()
    assert updated["id"] == state["contact_type_id"]
    assert updated["name"] == update_payload["name"]


@pytest.mark.anyio
async def test_05_delete_contact_type(api_context, auth_headers, state):
    """
    DELETE /manage/contact_types/{id}
    Deletes the created contact type.
    """
    r = await api_context.delete(f"{BASE}/{state['contact_type_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["detail"] == "Contact type deleted successfully"


@pytest.mark.anyio
async def test_06_get_deleted_contact_type_returns_404(api_context, auth_headers, state):
    """
    GET /manage/contact_types/{id} after delete should return 404.
    """
    r = await api_context.get(f"{BASE}/{state['contact_type_id']}", headers=auth_headers)
    assert r.status_code == 404, r.text