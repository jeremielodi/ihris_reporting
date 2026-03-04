import pytest
import uuid
from helpers import load_mock

BASE = "/manage/organization_levels"
mock = load_mock("organization_level")


@pytest.fixture(scope="module")
def state():
    """
    Shared state across tests in this module.
    Stores IDs created during tests so later tests can reuse them.
    """
    return {}


@pytest.mark.anyio
async def test_01_create_organization_level(api_context, auth_headers, state):
    """
    POST /manage/organization_levels/
    Creates an organization level and stores its ID for later tests.
    """
    payload = mock["organization_level"].copy()

    # Make data unique across runs to avoid collisions
    payload["name"] = f"{payload['name']}-{uuid.uuid4().hex[:6]}"
    payload["level"] = int(payload["level"]) + int(uuid.uuid4().int % 1000)

    r = await api_context.post(f'{BASE}/', json=payload, headers=auth_headers)
    assert r.status_code in (200, 201), r.text

    created = r.json()
    print(created)
    state["org_level_id"] = created["id"]
    state["org_level_name"] = created["name"]
    state["org_level_level"] = created["level"]

    assert state["org_level_id"] is not None


@pytest.mark.anyio
async def test_02_get_all_organization_levels(api_context, auth_headers, state):
    """
    GET /manage/organization_levels
    Ensures the created record exists in the list.
    """
    r = await api_context.get(BASE, headers=auth_headers)
    assert r.status_code == 200, r.text

    rows = r.json()
    assert isinstance(rows, list)
    assert any(x["id"] == state["org_level_id"] for x in rows)


@pytest.mark.anyio
async def test_03_get_organization_level_by_id(api_context, auth_headers, state):
    """
    GET /manage/organization_levels/{id}
    Retrieves the created record.
    """
    r = await api_context.get(f"{BASE}/{state['org_level_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text

    row = r.json()
    assert row["id"] == state["org_level_id"]


@pytest.mark.anyio
async def test_04_update_organization_level(api_context, auth_headers, state):
    """
    PUT /manage/organization_levels/{id}
    Updates the created record (partial update).
    """
    update_payload = mock["organization_level_update"].copy()

    # Keep it unique, but stable enough to validate
    update_payload["name"] = f"{update_payload['name']}-{uuid.uuid4().hex[:4]}"
    update_payload["level"] = int(update_payload["level"]) + int(uuid.uuid4().int % 1000)

    r = await api_context.put(
        f"{BASE}/{state['org_level_id']}",
        json=update_payload,
        headers=auth_headers
    )
    assert r.status_code == 200, r.text

    updated = r.json()
    assert updated["id"] == state["org_level_id"]
    assert updated["name"] == update_payload["name"]
    assert updated["level"] == update_payload["level"]


@pytest.mark.anyio
async def test_05_delete_organization_level(api_context, auth_headers, state):
    """
    DELETE /manage/organization_levels/{id}
    Deletes the created record.
    """
    r = await api_context.delete(f"{BASE}/{state['org_level_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text

    data = r.json()
    assert "deleted" in (data.get("detail") or "").lower()


@pytest.mark.anyio
async def test_06_get_deleted_organization_level_returns_404(api_context, auth_headers, state):
    """
    GET /manage/organization_levels/{id} after delete -> 404.
    """
    r = await api_context.get(f"{BASE}/{state['org_level_id']}", headers=auth_headers)
    assert r.status_code == 404, r.text


@pytest.mark.anyio
async def test_07_get_organization_level_404(api_context, auth_headers):
    
    """
    GET /manage/organization_levels/{id} with fake id -> 404.
    """
    fake_id = "org_level|NOT_EXISTS"
    r = await api_context.get(f"{BASE}/{fake_id}", headers=auth_headers)
    assert r.status_code == 404, r.text


@pytest.mark.anyio
async def test_08_get_organization_level_404(api_context, auth_headers):
    """
    GET /manage/organization_levels/{id} with fake id -> 404
    """
    fake_id = "org_level|NOT_EXISTS"
    r = await api_context.get(f"{BASE}/{fake_id}", headers=auth_headers)
    assert r.status_code == 404, r.text

    # Endpoint returns: "Organization level not found"
    detail = (r.json().get("detail") or "").lower()
    assert "not found" in detail