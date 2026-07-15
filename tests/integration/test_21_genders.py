import pytest

BASE = "/manage/genders"


@pytest.fixture(scope="module")
def state():
    return {}


@pytest.mark.anyio
async def test_01_get_all_genders(api_context, auth_headers, state):
    """
    GET /manage/genders/
    Read-only reference table (Male/Female seed data) - no create/update/delete
    endpoints exist for this resource.
    """
    r = await api_context.get(f"{BASE}/", headers=auth_headers)
    assert r.status_code == 200, r.text

    items = r.json()
    assert isinstance(items, list)
    assert len(items) > 0

    state["gender_id"] = items[0]["id"]


@pytest.mark.anyio
async def test_02_get_gender_by_id(api_context, auth_headers, state):
    """
    GET /manage/genders/{id}
    """
    r = await api_context.get(f"{BASE}/{state['gender_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["id"] == state["gender_id"]


@pytest.mark.anyio
async def test_03_get_gender_404(api_context, auth_headers):
    """
    GET /manage/genders/{id} with fake id -> 404.
    """
    r = await api_context.get(f"{BASE}/gender|NOT_EXISTS", headers=auth_headers)
    assert r.status_code == 404, r.text
