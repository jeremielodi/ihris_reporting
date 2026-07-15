import pytest
import uuid
from helpers import load_mock

BASE = "/manage/document_types"
mock = load_mock("document_type")


@pytest.fixture(scope="module")
def state():
    return {}


@pytest.fixture(scope="module")
def unique_suffix():
    return uuid.uuid4().hex[:8]


@pytest.mark.anyio
async def test_01_get_all_document_types(api_context, auth_headers, state):
    r = await api_context.get(f"{BASE}/", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert isinstance(r.json(), list)


@pytest.mark.anyio
async def test_02_create_document_type(api_context, auth_headers, state, unique_suffix):
    """id is derived from name via make_id(): documenttype|<normalized_name>."""
    payload = mock["document_type"].copy()
    payload["name"] = f"{payload['name']}-{unique_suffix}"

    r = await api_context.post(f"{BASE}/", json=payload, headers=auth_headers)
    assert r.status_code in (200, 201), r.text

    created = r.json()
    state["document_type_id"] = created["id"]
    assert state["document_type_id"].startswith("documenttype|")
    assert created["name"] == payload["name"]


@pytest.mark.anyio
async def test_03_get_document_type_by_id(api_context, auth_headers, state):
    r = await api_context.get(f"{BASE}/{state['document_type_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["id"] == state["document_type_id"]


@pytest.mark.anyio
async def test_04_update_document_type(api_context, auth_headers, state, unique_suffix):
    update_payload = mock["document_type_update"].copy()
    update_payload["name"] = f"{update_payload['name']}-{unique_suffix}"

    r = await api_context.put(
        f"{BASE}/{state['document_type_id']}",
        json=update_payload,
        headers=auth_headers
    )
    assert r.status_code == 200, r.text
    assert r.json()["id"] == state["document_type_id"]
    assert r.json()["name"] == update_payload["name"]


@pytest.mark.anyio
async def test_05_delete_document_type(api_context, auth_headers, state):
    r = await api_context.delete(f"{BASE}/{state['document_type_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert "deleted" in (r.json().get("detail") or "").lower()


@pytest.mark.anyio
async def test_06_get_deleted_document_type_returns_404(api_context, auth_headers, state):
    r = await api_context.get(f"{BASE}/{state['document_type_id']}", headers=auth_headers)
    assert r.status_code == 404, r.text


@pytest.mark.anyio
async def test_07_get_document_type_404(api_context, auth_headers):
    r = await api_context.get(f"{BASE}/documenttype|NOT_EXISTS", headers=auth_headers)
    assert r.status_code == 404, r.text
