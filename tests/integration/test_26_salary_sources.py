import pytest
import uuid
from helpers import load_mock

BASE = "/manage/salary_sources"
mock = load_mock("salary_source")


@pytest.fixture(scope="module")
def state():
    return {}


@pytest.fixture(scope="module")
def unique_suffix():
    return uuid.uuid4().hex[:8]


@pytest.mark.anyio
async def test_01_get_all_salary_sources(api_context, auth_headers, state):
    r = await api_context.get(f"{BASE}/", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert isinstance(r.json(), list)


@pytest.mark.anyio
async def test_02_create_salary_source(api_context, auth_headers, state, unique_suffix):
    """id is derived from name: salary_source|<name>."""
    payload = mock["salary_source"].copy()
    payload["name"] = f"{payload['name']}-{unique_suffix}"

    r = await api_context.post(f"{BASE}/", json=payload, headers=auth_headers)
    assert r.status_code in (200, 201), r.text

    created = r.json()
    state["salary_source_id"] = created["id"]
    assert state["salary_source_id"] == f"salary_source|{payload['name']}"


@pytest.mark.anyio
async def test_03_get_salary_source_by_id(api_context, auth_headers, state):
    r = await api_context.get(f"{BASE}/{state['salary_source_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["id"] == state["salary_source_id"]


@pytest.mark.anyio
async def test_04_update_salary_source(api_context, auth_headers, state):
    update_payload = mock["salary_source_update"].copy()

    r = await api_context.put(
        f"{BASE}/{state['salary_source_id']}",
        json=update_payload,
        headers=auth_headers
    )
    assert r.status_code == 200, r.text
    assert r.json()["id"] == state["salary_source_id"]
    assert r.json()["description"] == update_payload["description"]


@pytest.mark.anyio
async def test_05_delete_salary_source(api_context, auth_headers, state):
    r = await api_context.delete(f"{BASE}/{state['salary_source_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert "deleted" in (r.json().get("detail") or "").lower()


@pytest.mark.anyio
async def test_06_get_deleted_salary_source_returns_404(api_context, auth_headers, state):
    r = await api_context.get(f"{BASE}/{state['salary_source_id']}", headers=auth_headers)
    assert r.status_code == 404, r.text


@pytest.mark.anyio
async def test_07_get_salary_source_404(api_context, auth_headers):
    r = await api_context.get(f"{BASE}/salary_source|NOT_EXISTS", headers=auth_headers)
    assert r.status_code == 404, r.text
