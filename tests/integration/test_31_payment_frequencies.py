import pytest
import uuid
from helpers import load_mock

BASE = "/manage/payment_frequencies"
mock = load_mock("payment_frequency")


@pytest.fixture(scope="module")
def state():
    return {}


@pytest.fixture(scope="module")
def unique_suffix():
    return uuid.uuid4().hex[:8]


@pytest.mark.anyio
async def test_01_get_all_payment_frequencies(api_context, auth_headers, state):
    r = await api_context.get(f"{BASE}/", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert isinstance(r.json(), list)


@pytest.mark.anyio
async def test_02_create_payment_frequency(api_context, auth_headers, state, unique_suffix):
    """id is derived from name: payment_frequency|<name>."""
    payload = mock["payment_frequency"].copy()
    payload["name"] = f"{payload['name']}-{unique_suffix}"

    r = await api_context.post(f"{BASE}/", json=payload, headers=auth_headers)
    assert r.status_code in (200, 201), r.text

    created = r.json()
    state["payment_frequency_id"] = created["id"]
    assert state["payment_frequency_id"] == f"payment_frequency|{payload['name']}"


@pytest.mark.anyio
async def test_03_get_payment_frequency_by_id(api_context, auth_headers, state):
    r = await api_context.get(f"{BASE}/{state['payment_frequency_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["id"] == state["payment_frequency_id"]


@pytest.mark.anyio
async def test_04_update_payment_frequency(api_context, auth_headers, state):
    update_payload = mock["payment_frequency_update"].copy()

    r = await api_context.put(
        f"{BASE}/{state['payment_frequency_id']}",
        json=update_payload,
        headers=auth_headers
    )
    assert r.status_code == 200, r.text
    assert r.json()["id"] == state["payment_frequency_id"]
    assert r.json()["code"] == update_payload["code"]


@pytest.mark.anyio
async def test_05_delete_payment_frequency(api_context, auth_headers, state):
    r = await api_context.delete(f"{BASE}/{state['payment_frequency_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert "deleted" in (r.json().get("detail") or "").lower()


@pytest.mark.anyio
async def test_06_get_deleted_payment_frequency_returns_404(api_context, auth_headers, state):
    r = await api_context.get(f"{BASE}/{state['payment_frequency_id']}", headers=auth_headers)
    assert r.status_code == 404, r.text


@pytest.mark.anyio
async def test_07_get_payment_frequency_404(api_context, auth_headers):
    r = await api_context.get(f"{BASE}/payment_frequency|NOT_EXISTS", headers=auth_headers)
    assert r.status_code == 404, r.text
