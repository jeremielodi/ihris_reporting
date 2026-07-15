import pytest
import uuid
from helpers import load_mock

BASE = "/manage/educational_majors"
mock = load_mock("educational_major")


@pytest.fixture(scope="module")
def state():
    return {}


@pytest.fixture(scope="module")
def unique_suffix():
    return uuid.uuid4().hex[:8]


@pytest.mark.anyio
async def test_01_get_all_educational_majors(api_context, auth_headers, state):
    r = await api_context.get(f"{BASE}/", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert isinstance(r.json(), list)


@pytest.mark.anyio
async def test_02_create_educational_major(api_context, auth_headers, state, unique_suffix):
    """id is derived from name: educational_major|<name>."""
    payload = mock["educational_major"].copy()
    payload["name"] = f"{payload['name']}-{unique_suffix}"

    r = await api_context.post(f"{BASE}/", json=payload, headers=auth_headers)
    assert r.status_code in (200, 201), r.text

    created = r.json()
    state["educational_major_id"] = created["id"]
    assert state["educational_major_id"] == f"educational_major|{payload['name']}"


@pytest.mark.anyio
async def test_03_get_educational_major_by_id(api_context, auth_headers, state):
    r = await api_context.get(f"{BASE}/{state['educational_major_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["id"] == state["educational_major_id"]


@pytest.mark.anyio
async def test_04_update_educational_major(api_context, auth_headers, state):
    update_payload = mock["educational_major_update"].copy()

    r = await api_context.put(
        f"{BASE}/{state['educational_major_id']}",
        json=update_payload,
        headers=auth_headers
    )
    assert r.status_code == 200, r.text
    assert r.json()["id"] == state["educational_major_id"]
    assert r.json()["code"] == update_payload["code"]


@pytest.mark.anyio
async def test_05_delete_educational_major(api_context, auth_headers, state):
    r = await api_context.delete(f"{BASE}/{state['educational_major_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert "deleted" in (r.json().get("detail") or "").lower()


@pytest.mark.anyio
async def test_06_get_deleted_educational_major_returns_404(api_context, auth_headers, state):
    r = await api_context.get(f"{BASE}/{state['educational_major_id']}", headers=auth_headers)
    assert r.status_code == 404, r.text


@pytest.mark.anyio
async def test_07_get_educational_major_404(api_context, auth_headers):
    r = await api_context.get(f"{BASE}/educational_major|NOT_EXISTS", headers=auth_headers)
    assert r.status_code == 404, r.text
