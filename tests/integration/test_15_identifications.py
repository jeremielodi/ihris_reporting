import pytest
import uuid
from helpers import load_mock

IDENT_TYPES_BASE = "/manage/identification_types"
BASE = "/manage/identifications"
mock = load_mock("identification")


@pytest.fixture(scope="module")
def state():
    return {}


@pytest.fixture(scope="module")
def unique_suffix():
    return uuid.uuid4().hex[:8]


@pytest.fixture(scope="function")
async def ensure_identification(api_context, auth_headers, state, unique_suffix):
    """
    Creates dependencies once (identification_type + identification),
    but is function-scoped so it can safely depend on api_context.
    """
    if state.get("identification_id"):
        return state

    person_id = mock["identification"].get("person_id")
    if not person_id:
        pytest.fail("Mock identification.json must include identification.person_id")

    # 1) Create identification type
    type_payload = mock["identification_type"].copy()
    type_payload["name"] = f"{type_payload['name']}-{unique_suffix}"

    r = await api_context.post(f"{IDENT_TYPES_BASE}/", json=type_payload, headers=auth_headers)
    assert r.status_code in (200, 201), r.text
    state["type_id"] = r.json()["id"]

    # 2) Create identification
    ident_payload = mock["identification"].copy()
    ident_payload["type_id"] = state["type_id"]
    ident_payload["number"] = f"{ident_payload['number']}-{unique_suffix}"

    r = await api_context.post(f"{BASE}/", json=ident_payload, headers=auth_headers)
    assert r.status_code in (200, 201), r.text

    created = r.json()
    state["identification_id"] = created["id"]
    state["person_id"] = person_id

    return state


@pytest.mark.anyio
async def test_01_get_all_identifications(api_context, auth_headers, ensure_identification):
    r = await api_context.get(f"{BASE}/", headers=auth_headers)
    assert r.status_code == 200, r.text

    items = r.json()
    assert any(x["id"] == ensure_identification["identification_id"] for x in items)


@pytest.mark.anyio
async def test_02_get_identification_by_id(api_context, auth_headers, ensure_identification):
    ident_id = ensure_identification["identification_id"]

    r = await api_context.get(f"{BASE}/{ident_id}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["id"] == ident_id


@pytest.mark.anyio
async def test_03_get_identifications_by_person(api_context, auth_headers, ensure_identification):
    pid = ensure_identification["person_id"]
    ident_id = ensure_identification["identification_id"]

    r = await api_context.get(f"{BASE}/person/{pid}", headers=auth_headers)
    assert r.status_code == 200, r.text

    items = r.json()
    found = next((x for x in items if str(x.get("id")) == ident_id), None)
    assert found is not None
    assert "type_name" in found


@pytest.mark.anyio
async def test_04_update_identification(api_context, auth_headers, ensure_identification):
    ident_id = ensure_identification["identification_id"]
    update_payload = mock["identification_update"].copy()

    r = await api_context.put(f"{BASE}/{ident_id}", json=update_payload, headers=auth_headers)
    assert r.status_code == 200, r.text


@pytest.mark.anyio
async def test_05_delete_identification(api_context, auth_headers, ensure_identification):
    ident_id = ensure_identification["identification_id"]

    r = await api_context.delete(f"{BASE}/{ident_id}", headers=auth_headers)
    assert r.status_code == 200, r.text


@pytest.mark.anyio
async def test_06_get_deleted_identification_returns_404(api_context, auth_headers, ensure_identification):
    ident_id = ensure_identification["identification_id"]

    r = await api_context.get(f"{BASE}/{ident_id}", headers=auth_headers)
    assert r.status_code == 404, r.text