import pytest
import uuid
from helpers import load_mock

BASE = "/manage/job_titles"
mock = load_mock("job_title")


@pytest.fixture(scope="module")
def state():
    """
    Shared state across tests in this module.
    Stores created job_title_id for later tests.
    """
    return {}


@pytest.fixture(scope="module")
def unique_suffix():
    return uuid.uuid4().hex[:8]


@pytest.mark.anyio
async def test_01_create_job_title(api_context, auth_headers, state, unique_suffix):
    """
    POST /manage/job_titles/
    Creates a job title and stores its id for later tests.
    """
    payload = mock["job_title"].copy()
    payload["name"] = f"{payload['name']}-{unique_suffix}"

    r = await api_context.post(f"{BASE}/", json=payload, headers=auth_headers)
    assert r.status_code in (200, 201), r.text

    created = r.json()
    state["job_title_id"] = created["id"]
    state["job_title_name"] = created.get("name")

    assert state["job_title_id"].startswith("job_title|")


@pytest.mark.anyio
async def test_02_get_all_job_titles(api_context, auth_headers, state):
    """
    GET /manage/job_titles
    Ensures created job title exists in list.
    """
    r = await api_context.get(BASE, headers=auth_headers)
    assert r.status_code == 200, r.text

    items = r.json()
    assert isinstance(items, list)
    assert any(x["id"] == state["job_title_id"] for x in items)


@pytest.mark.anyio
async def test_03_get_job_title_by_id(api_context, auth_headers, state):
    """
    GET /manage/job_titles/{id}
    Retrieves created job title by id.
    """
    r = await api_context.get(f"{BASE}/{state['job_title_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["id"] == state["job_title_id"]


@pytest.mark.anyio
async def test_04_update_job_title(api_context, auth_headers, state):
    """
    PUT /manage/job_titles/{id}
    Updates created job title.
    NOTE: Keep the name stable (id is based on name at creation).
    """
    update_payload = mock["job_title_update"].copy()

    # Ensure name stays stable (avoid confusing id/name mismatch)
    update_payload["name"] = state["job_title_name"]

    r = await api_context.put(
        f"{BASE}/{state['job_title_id']}",
        json=update_payload,
        headers=auth_headers
    )
    assert r.status_code == 200, r.text

    updated = r.json()
    assert updated["id"] == state["job_title_id"]


@pytest.mark.anyio
async def test_05_delete_job_title(api_context, auth_headers, state):
    """
    DELETE /manage/job_titles/{id}
    Deletes created job title.
    """
    r = await api_context.delete(f"{BASE}/{state['job_title_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert "deleted" in (r.json().get("detail") or "").lower()


@pytest.mark.anyio
async def test_06_get_deleted_job_title_returns_404(api_context, auth_headers, state):
    """
    GET /manage/job_titles/{id} after delete -> 404
    """
    r = await api_context.get(f"{BASE}/{state['job_title_id']}", headers=auth_headers)
    assert r.status_code == 404, r.text


@pytest.mark.anyio
async def test_07_get_job_title_404(api_context, auth_headers):
    """
    GET /manage/job_titles/{id} with fake id -> 404
    """
    fake_id = "job_title|NOT_EXISTS"
    r = await api_context.get(f"{BASE}/{fake_id}", headers=auth_headers)
    assert r.status_code == 404, r.text