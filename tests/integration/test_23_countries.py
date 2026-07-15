import pytest

BASE = "/manage/countries"


@pytest.fixture(scope="module")
def state():
    return {}


@pytest.mark.anyio
async def test_01_get_all_countries(api_context, auth_headers, state):
    """
    GET /manage/countries/
    Read-only reference table (ISO country list) - no create/update/delete
    endpoints exist for this resource, despite Create/Update schemas existing.
    """
    r = await api_context.get(f"{BASE}/", headers=auth_headers)
    assert r.status_code == 200, r.text

    items = r.json()
    assert isinstance(items, list)
    assert len(items) > 0

    state["country_id"] = items[0]["id"]


@pytest.mark.anyio
async def test_02_get_country_by_id(api_context, auth_headers, state):
    """
    GET /manage/countries/{id}
    """
    r = await api_context.get(f"{BASE}/{state['country_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["id"] == state["country_id"]


@pytest.mark.anyio
async def test_03_get_country_404(api_context, auth_headers):
    """
    GET /manage/countries/{id} with fake id -> 404.
    """
    r = await api_context.get(f"{BASE}/country|NOT_EXISTS", headers=auth_headers)
    assert r.status_code == 404, r.text
