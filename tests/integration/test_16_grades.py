import pytest
import uuid
from helpers import load_mock

BASE = "/manage/grades"
mock = load_mock("grade")


@pytest.fixture(scope="module")
def state():
    """Shared state across tests"""
    return {}


@pytest.fixture(scope="module")
def unique_suffix():
    return uuid.uuid4().hex[:8]


@pytest.fixture(scope="function")
async def ensure_grade(api_context, auth_headers, state, unique_suffix):
    """
    Create one grade if it does not already exist.
    """
    if state.get("grade_id"):
        return state

    payload = mock["grade"].copy()
    payload["name"] = f"{payload['name']}-{unique_suffix}"

    r = await api_context.post(f"{BASE}/", json=payload, headers=auth_headers)
    assert r.status_code in (200, 201), r.text

    created = r.json()

    state["grade_id"] = created["id"]
    state["grade_name"] = payload["name"]

    return state


@pytest.mark.anyio
async def test_01_get_all_grades(api_context, auth_headers, ensure_grade):
    """
    GET /grades/
    """
    r = await api_context.get(f"{BASE}/", headers=auth_headers)
    assert r.status_code == 200, r.text

    items = r.json()
    assert isinstance(items, list)

    assert any(x["id"] == ensure_grade["grade_id"] for x in items)


@pytest.mark.anyio
async def test_02_get_grade_by_id(api_context, auth_headers, ensure_grade):
    """
    GET /grades/{id}
    """
    grade_id = ensure_grade["grade_id"]

    r = await api_context.get(f"{BASE}/{grade_id}", headers=auth_headers)
    assert r.status_code == 200, r.text

    grade = r.json()

    assert grade["id"] == grade_id


@pytest.mark.anyio
async def test_03_update_grade(api_context, auth_headers, ensure_grade):
    """
    PUT /grades/{id}
    """
    grade_id = ensure_grade["grade_id"]

    payload = mock["grade_update"].copy()

    r = await api_context.put(
        f"{BASE}/{grade_id}",
        json=payload,
        headers=auth_headers
    )

    assert r.status_code == 200, r.text

    updated = r.json()

    assert updated["id"] == grade_id


@pytest.mark.anyio
async def test_04_bulk_import_grades(api_context, auth_headers, unique_suffix):
    """
    POST /grades/import
    """
    payload = []

    for g in mock["grades_bulk"]:
        item = g.copy()
        item["name"] = f"{item['name']}-{unique_suffix}"
        payload.append(item)

    r = await api_context.post(
        f"{BASE}/import",
        json=payload,
        headers=auth_headers
    )

    assert r.status_code in (200, 201), r.text

    inserted = r.json()

    assert isinstance(inserted, list)
    assert len(inserted) >= 1


@pytest.mark.anyio
async def test_05_delete_grade(api_context, auth_headers, ensure_grade):
    """
    DELETE /grades/{id}
    """
    grade_id = ensure_grade["grade_id"]

    r = await api_context.delete(
        f"{BASE}/{grade_id}",
        headers=auth_headers
    )

    assert r.status_code == 200, r.text
    assert "deleted" in r.json()["detail"].lower()


@pytest.mark.anyio
async def test_06_get_deleted_grade_returns_404(api_context, auth_headers, ensure_grade):
    """
    GET /grades/{id} after delete
    """
    grade_id = ensure_grade["grade_id"]

    r = await api_context.get(
        f"{BASE}/{grade_id}",
        headers=auth_headers
    )

    assert r.status_code == 404


@pytest.mark.anyio
async def test_07_get_unknown_grade_returns_404(api_context, auth_headers):
    """
    GET /grades/{id} with unknown id
    """
    r = await api_context.get(
        f"{BASE}/salary_grade|DOES_NOT_EXIST",
        headers=auth_headers
    )

    assert r.status_code == 404