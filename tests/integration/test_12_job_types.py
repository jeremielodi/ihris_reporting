import pytest
import uuid
from helpers import load_mock

BASE = "/manage/job_types"
mock = load_mock("job_type")


@pytest.fixture(scope="module")
def state():
    """
    Shared state across tests in this module.
    Stores created job_type_id for later tests.
    """
    return {}


@pytest.fixture(scope="module")
def unique_suffix():
    """Stable random suffix for this module run."""
    return uuid.uuid4().hex[:8]


@pytest.mark.anyio
async def test_01_create_job_type(api_context, auth_headers, state, unique_suffix):
    """
    POST /manage/job_types/
    Creates a job type and stores its id for subsequent tests.
    """
    payload = mock["job_type"].copy()
    payload["name"] = f"{payload['name']}-{unique_suffix}"

    r = await api_context.post(f"{BASE}/", json=payload, headers=auth_headers)
    assert r.status_code in (200, 201), r.text

    created = r.json()
    state["job_type_id"] = created["id"]
    state["job_type_name"] = created.get("name")

    assert state["job_type_id"].startswith("job_type|")


@pytest.mark.anyio
async def test_02_get_all_job_types(api_context, auth_headers, state):
    """
    GET /manage/job_types
    Ensures created job type exists in list.
    """
    r = await api_context.get(BASE, headers=auth_headers)
    assert r.status_code == 200, r.text

    items = r.json()
    assert isinstance(items, list)
    assert any(x["id"] == state["job_type_id"] for x in items)


@pytest.mark.anyio
async def test_03_get_job_type_by_id(api_context, auth_headers, state):
    """
    GET /manage/job_types/{id}
    Retrieves created job type by id.
    """
    r = await api_context.get(f"{BASE}/{state['job_type_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["id"] == state["job_type_id"]


@pytest.mark.anyio
async def test_04_update_job_type(api_context, auth_headers, state):
    """
    PUT /manage/job_types/{id}
    Updates created job type.
    NOTE: Keep name stable (ID was built from name at create time).
    """
    update_payload = mock["job_type_update"].copy()
    update_payload["name"] = state["job_type_name"]

    r = await api_context.put(
        f"{BASE}/{state['job_type_id']}",
        json=update_payload,
        headers=auth_headers
    )
    assert r.status_code == 200, r.text

    updated = r.json()
    assert updated["id"] == state["job_type_id"]
    assert updated.get("code") == mock["job_type_update"]["code"]
    assert updated.get("description") == mock["job_type_update"]["description"]


@pytest.mark.anyio
async def test_05_bulk_import_job_types(api_context, auth_headers, state, unique_suffix):
    """
    POST /manage/job_types/import
    Bulk import job types. Ensures at least one record is inserted.
    """
    payload = [x.copy() for x in mock["job_type_bulk"]]

    # Make names unique to avoid collisions across runs
    for item in payload:
        item["name"] = f"{item['name']}-{unique_suffix}-{uuid.uuid4().hex[:4]}"

    r = await api_context.post(f"{BASE}/import", json=payload, headers=auth_headers)
    assert r.status_code == 201, r.text

    inserted = r.json()
    assert isinstance(inserted, list)
    assert len(inserted) >= 1

    # Optional: store one inserted id for later inspection
    state["bulk_one_id"] = inserted[0]["id"]


@pytest.mark.anyio
async def test_06_delete_job_type(api_context, auth_headers, state):
    """
    DELETE /manage/job_types/{id}
    Deletes created job type.
    """
    r = await api_context.delete(f"{BASE}/{state['job_type_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert "deleted" in (r.json().get("detail") or "").lower()


@pytest.mark.anyio
async def test_07_get_deleted_job_type_returns_404(api_context, auth_headers, state):
    """
    GET /manage/job_types/{id} after delete -> 404
    """
    r = await api_context.get(f"{BASE}/{state['job_type_id']}", headers=auth_headers)
    assert r.status_code == 404, r.text


@pytest.mark.anyio
async def test_08_get_job_type_404(api_context, auth_headers):
    """
    GET /manage/job_types/{id} with fake id -> 404
    """
    fake_id = "job_type|NOT_EXISTS"
    r = await api_context.get(f"{BASE}/{fake_id}", headers=auth_headers)
    assert r.status_code == 404, r.text