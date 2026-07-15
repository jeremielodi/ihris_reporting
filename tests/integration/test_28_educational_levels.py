import pytest
import uuid
from helpers import load_mock

BASE = "/manage/educational_levels"
mock = load_mock("educational_level")


@pytest.fixture(scope="module")
def state():
    return {}


@pytest.fixture(scope="module")
def unique_suffix():
    return uuid.uuid4().hex[:8]


@pytest.mark.anyio
async def test_01_get_all_educational_levels(api_context, auth_headers, state):
    """
    GET /manage/educational_levels/
    This module was previously unreachable: manage/routes.py imported both
    manage.services.educational_level.level and
    manage.services.organization_level.level under the same local name
    ("level"), so the second import silently shadowed the first and only
    organization_level's router ever got mounted. Fixed by aliasing the
    imports; this test guards against the regression.
    """
    r = await api_context.get(f"{BASE}/", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert isinstance(r.json(), list)


@pytest.mark.anyio
async def test_02_create_educational_level(api_context, auth_headers, state, unique_suffix):
    """id is derived from name: educational_level|<name>."""
    payload = mock["educational_level"].copy()
    payload["name"] = f"{payload['name']}-{unique_suffix}"

    r = await api_context.post(f"{BASE}/", json=payload, headers=auth_headers)
    assert r.status_code in (200, 201), r.text

    created = r.json()
    state["educational_level_id"] = created["id"]
    assert state["educational_level_id"] == f"educational_level|{payload['name']}"


@pytest.mark.anyio
async def test_03_get_educational_level_by_id(api_context, auth_headers, state):
    r = await api_context.get(f"{BASE}/{state['educational_level_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["id"] == state["educational_level_id"]


@pytest.mark.anyio
async def test_04_update_educational_level(api_context, auth_headers, state):
    update_payload = mock["educational_level_update"].copy()

    r = await api_context.put(
        f"{BASE}/{state['educational_level_id']}",
        json=update_payload,
        headers=auth_headers
    )
    assert r.status_code == 200, r.text
    assert r.json()["id"] == state["educational_level_id"]
    assert r.json()["code"] == update_payload["code"]


@pytest.mark.anyio
async def test_05_delete_educational_level(api_context, auth_headers, state):
    r = await api_context.delete(f"{BASE}/{state['educational_level_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert "deleted" in (r.json().get("detail") or "").lower()


@pytest.mark.anyio
async def test_06_get_deleted_educational_level_returns_404(api_context, auth_headers, state):
    r = await api_context.get(f"{BASE}/{state['educational_level_id']}", headers=auth_headers)
    assert r.status_code == 404, r.text


@pytest.mark.anyio
async def test_07_get_educational_level_404(api_context, auth_headers):
    r = await api_context.get(f"{BASE}/educational_level|NOT_EXISTS", headers=auth_headers)
    assert r.status_code == 404, r.text
