import pytest
import uuid
from helpers import load_mock

BASE = "/manage/contacts"
mock = load_mock("contact")


@pytest.fixture(scope="module")
def state():
    """
    Shared state across tests in this module.
    Stores IDs created during tests so later tests can reuse them.
    """
    return {}


@pytest.fixture(scope="module")
def unique_person_id():
    """
    Generate one stable person_id for all tests in this module.
    If your system expects a real person, replace this with a real created person ID.
    """
    return f"person|{uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="module")
def unique_contact_type():
    """
    Contact type id/string used by HippoContactCreate.contact_type.
    If your API requires an existing contact type record, make sure it exists first.
    """
    # If your contact types are like: contact_type|personal
    # keep it simple and stable:
    return "contact_type|personal"


@pytest.mark.anyio
async def test_01_create_contact(api_context, auth_headers, state, unique_person_id, unique_contact_type):
    """
    POST /manage/contacts/
    Creates a contact and stores its UUID for subsequent tests.
    """
    payload = mock["contact"].copy()

    # Required fields by schema
    payload["person_id"] = unique_person_id
    payload["contact_type"] = unique_contact_type

    r = await api_context.post(f"{BASE}/", json=payload, headers=auth_headers)
    assert r.status_code in (200, 201), r.text

    created = r.json()
    state["contact_id"] = created["id"]       # UUID string
    state["person_id"] = created["person_id"] # should match unique_person_id

    assert state["contact_id"] is not None
    assert created["person_id"] == unique_person_id
    assert created["contact_type"] == unique_contact_type


@pytest.mark.anyio
async def test_02_get_all_contacts(api_context, auth_headers, state):
    """
    GET /manage/contacts
    Ensures the created contact exists in the list.
    """
    r = await api_context.get(BASE, headers=auth_headers)
    assert r.status_code == 200, r.text

    items = r.json()
    assert any(x["id"] == state["contact_id"] for x in items)


@pytest.mark.anyio
async def test_03_get_contact_by_id(api_context, auth_headers, state):
    """
    GET /manage/contacts/{contact_id}
    Retrieves the created contact.
    """
    r = await api_context.get(f"{BASE}/{state['contact_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["id"] == state["contact_id"]


@pytest.mark.anyio
async def test_04_get_contacts_by_person_id(api_context, auth_headers, state):
    """
    GET /manage/contacts/person/{persion_id}
    Retrieves contacts linked to the same person_id used during creation.
    """
    # Endpoint uses "persion_id" in path in your code (typo), but that's fine.
    r = await api_context.get(f"{BASE}/person/{state['person_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text

    items = r.json()
    assert isinstance(items, list)
    assert any(x["id"] == state["contact_id"] for x in items)


@pytest.mark.anyio
async def test_05_update_contact(api_context, auth_headers, state):
    """
    PUT /manage/contacts/{contact_id}
    Updates the contact (only non-null fields).
    """
    update_payload = mock["contact_update"].copy()

    r = await api_context.put(
        f"{BASE}/{state['contact_id']}",
        json=update_payload,
        headers=auth_headers
    )
    assert r.status_code == 200, r.text

    updated = r.json()
    assert updated["id"] == state["contact_id"]
    assert updated.get("notes") == mock["contact_update"]["notes"]
    assert updated.get("address") == mock["contact_update"]["address"]


@pytest.mark.anyio
async def test_06_delete_contact(api_context, auth_headers, state):
    """
    DELETE /manage/contacts/{contact_id}
    Deletes the created contact.
    """
    r = await api_context.delete(f"{BASE}/{state['contact_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["detail"] == "Contact deleted successfully"


@pytest.mark.anyio
async def test_07_get_deleted_contact_returns_404(api_context, auth_headers, state):
    """
    GET /manage/contacts/{contact_id} after delete should return 404.
    """
    r = await api_context.get(f"{BASE}/{state['contact_id']}", headers=auth_headers)
    assert r.status_code == 404, r.text