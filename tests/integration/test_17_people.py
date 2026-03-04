import pytest
import uuid
from helpers import load_mock

BASE = "/manage/people"  # <-- change if your API path is different
mock = load_mock("person")


@pytest.fixture(scope="module")
def state():
    """Shared module state (stores created person id)."""
    return {}


@pytest.fixture(scope="module")
def unique_suffix():
    return uuid.uuid4().hex[:8]


@pytest.fixture(scope="function")
async def ensure_person(api_context, auth_headers, state, unique_suffix):
    """
    Create a Person once per module, but fixture is function-scoped
    so it can depend on api_context safely.
    """
    if state.get("person_id"):
        return state

    payload = mock["person"].copy()

    # Make lastname unique to avoid collisions across runs
    payload["lastname"] = f"{payload['lastname']}-{unique_suffix}"

    # If your API generates id, don't send it.
    payload.pop("id", None)

    r = await api_context.post(f"{BASE}/", json=payload, headers=auth_headers)
    assert r.status_code in (200, 201), r.text

    created = r.json()

    # Expect id returned by API
    assert "id" in created, created
    state["person_id"] = created["id"]
    state["lastname"] = payload["lastname"]

    return state


@pytest.mark.anyio
async def test_01_list_people(api_context, auth_headers):
    """
    GET /people/
    """
    r = await api_context.get(f"{BASE}/", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert isinstance(r.json(), list)


@pytest.mark.anyio
async def test_02_create_person(api_context, auth_headers, ensure_person):
    """
    The creation is already done in ensure_person.
    This test only validates the id exists.
    """
    assert ensure_person["person_id"] is not None


@pytest.mark.anyio
async def test_03_get_person_by_id(api_context, auth_headers, ensure_person):
    """
    GET /people/{id}
    """
    pid = ensure_person["person_id"]

    r = await api_context.get(f"{BASE}/{pid}", headers=auth_headers)
    assert r.status_code == 200, r.text

    person = r.json()
    assert person["id"] == pid


@pytest.mark.anyio
async def test_04_update_person(api_context, auth_headers, ensure_person):
    """
    PUT /people/{id}
    """
    pid = ensure_person["person_id"]

    payload = mock["person_update"].copy()

    r = await api_context.put(
        f"{BASE}/{pid}",
        json=payload,
        headers=auth_headers
    )
    assert r.status_code == 200, r.text

    updated = r.json()
    assert updated["id"] == pid

    # Best-effort asserts (depends on what API returns)
    if "address" in payload:
        assert updated.get("address") == payload["address"]
    if "dependents" in payload:
        assert updated.get("dependents") == payload["dependents"]


# @pytest.mark.anyio
# async def test_05_delete_person(api_context, auth_headers, ensure_person):
#     """
#     DELETE /people/{id}
#     """
#     pid = ensure_person["person_id"]

#     r = await api_context.delete(f"{BASE}/{pid}", headers=auth_headers)
#     assert r.status_code == 200, r.text

#     data = r.json()
#     # Many of your endpoints return {"detail": "...deleted..."}
#     if isinstance(data, dict) and "detail" in data:
#         assert "deleted" in data["detail"].lower()


# @pytest.mark.anyio
# async def test_06_get_deleted_person_returns_404(api_context, auth_headers, ensure_person):
#     """
#     GET /people/{id} after delete -> 404
#     """
#     pid = ensure_person["person_id"]

#     r = await api_context.get(f"{BASE}/{pid}", headers=auth_headers)
#     assert r.status_code == 404, r.text


@pytest.mark.anyio
async def test_07_get_unknown_person_returns_404(api_context, auth_headers):
    """
    GET /people/{id} with random id -> 404
    """
    r = await api_context.get(f"{BASE}/person|DOES_NOT_EXIST", headers=auth_headers)
    assert r.status_code == 404, r.text