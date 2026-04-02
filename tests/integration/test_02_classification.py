import pytest
import uuid
from helpers import load_mock

BASE = "/manage/classifications"
mock = load_mock("classification")


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
async def test_01_create_classification(api_context, auth_headers, state, unique_suffix):
    """
    POST /manage/classifications/
    Creates a classification and stores its ID for subsequent tests.
    """
    payload = mock["classification"].copy()
    payload["name"] = f"{payload['name']}-{unique_suffix}"

    r = await api_context.post(f"{BASE}/", json=payload, headers=auth_headers)
    assert r.status_code in (200, 201), r.text

    created = r.json()
    state["classification_id"] = created["id"]
    state["classification_name"] = created["name"]

    assert created["id"] == f"classification|{state['classification_name']}" or created["id"].startswith("classification|")
    assert created["name"] == state["classification_name"]


@pytest.mark.anyio
async def test_02_get_all_classifications(api_context, auth_headers, state):
    """
    GET /manage/classifications
    Ensures the created classification exists in the list.
    """
    r = await api_context.get(BASE, headers=auth_headers)
    assert r.status_code == 200, r.text

    items = r.json()
    assert any(x["id"] == state["classification_id"] for x in items)


@pytest.mark.anyio
async def test_03_get_classification_by_id(api_context, auth_headers, state):
    """
    GET /manage/classifications/{id}
    Retrieves the created classification.
    """
    r = await api_context.get(f"{BASE}/{state['classification_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["id"] == state["classification_id"]


@pytest.mark.anyio
async def test_04_update_classification(api_context, auth_headers, state):
    """
    PUT /manage/classifications/{id}
    Updates the classification.
    Note: We keep the name stable (some systems derive IDs from name).
    """
    update_payload = mock["classification_update"].copy()
    update_payload["name"] = state["classification_name"]

    r = await api_context.put(
        f"{BASE}/{state['classification_id']}",
        json=update_payload,
        headers=auth_headers
    )
    assert r.status_code == 200, r.text
    assert r.json()["description"] == mock["classification_update"]["description"]


@pytest.mark.anyio
async def test_05_bulk_import_classifications(api_context, auth_headers, state):
    """
    POST /manage/classifications/import
    Bulk import classifications; stores one inserted ID (if returned) for optional checks.
    """
    payload = [x.copy() for x in mock["classification_bulk"]]

    # Ensure unique names to avoid collisions
    for item in payload:
        item["name"] = f"{item['name']}-{uuid.uuid4().hex[:6]}"

    r = await api_context.post(f"{BASE}/import", json=payload, headers=auth_headers)
    assert r.status_code == 201, r.text

    inserted = r.json()
    assert isinstance(inserted, list)
    assert len(inserted) >= 1

    # store one inserted id (optional)
    state["bulk_one_id"] = inserted[0]["id"]


@pytest.mark.anyio
async def test_06_delete_classification(api_context, auth_headers, state):
    """
    DELETE /manage/classifications/{id}
    Deletes the created classification.
    """
    r = await api_context.delete(f"{BASE}/{state['classification_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["detail"] == "Classification deleted successfully"


@pytest.mark.anyio
async def test_07_get_deleted_classification_returns_404(api_context, auth_headers, state):
    """
    GET /manage/classifications/{id} after delete should return 404.
    """
    r = await api_context.get(f"{BASE}/{state['classification_id']}", headers=auth_headers)
    assert r.status_code == 404, r.text
