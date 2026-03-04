import pytest
import uuid
from helpers import load_mock

BASE = "/manage/settings"
UPLOAD = "/manage/settings/logo/upload"

mock = load_mock("setting")


@pytest.fixture(scope="module")
def state():
    """
    Stores created setting id for this module tests.
    """
    return {}


@pytest.fixture(scope="module")
def unique_suffix():
    return uuid.uuid4().hex[:8]


@pytest.fixture(scope="function")
async def ensure_created_setting(api_context, auth_headers, state, unique_suffix):
    """
    Ensure we have a fresh setting created via POST /settings/.
    Function scope to safely depend on api_context.
    """
    if state.get("setting_id"):
        return state

    payload = mock["setting_create"].copy()

    # Make app_name unique across runs
    payload["app_name"] = f"{payload['app_name']}-{unique_suffix}"

    r = await api_context.post(f"{BASE}/", json=payload, headers=auth_headers)
    assert r.status_code in (200, 201), r.text

    created = r.json()
    assert "id" in created, created

    state["setting_id"] = created["id"]
    state["app_name"] = payload["app_name"]
    return state


@pytest.mark.anyio
async def test_01_create_setting(api_context, auth_headers, state):
    """
    POST /manage/settings/

    Creates a new setting and stores its id in `state`
    so other tests can reuse it.
    """
    payload = mock["setting_create"].copy()

    # Make app_name unique across runs
    payload["app_name"] = f"{payload['app_name']}-{uuid.uuid4().hex[:8]}"

    r = await api_context.post(f"{BASE}/", json=payload, headers=auth_headers)
    assert r.status_code in (200, 201), r.text

    created = r.json()

    # DB-generated id (usually int). Store it for next tests.
    assert "id" in created, created
    state["setting_id"] = created["id"]

    # Basic response checks
    assert created["app_name"] == payload["app_name"]
    assert created["app_version"] == payload["app_version"]

@pytest.mark.anyio
async def test_02_get_all_settings(api_context, auth_headers, ensure_created_setting):
    """
    GET /settings/
    Requires auth
    """
    r = await api_context.get(f"{BASE}/", headers=auth_headers)
    assert r.status_code == 200, r.text

    items = r.json()
    assert isinstance(items, list)

    sid = ensure_created_setting["setting_id"]
    assert any(str(x["id"]) == str(sid) for x in items)


@pytest.mark.anyio
async def test_03_get_setting_by_id(api_context, auth_headers, ensure_created_setting):
    """
    GET /settings/{id}
    """
    sid = ensure_created_setting["setting_id"]

    r = await api_context.get(f"{BASE}/{sid}", headers=auth_headers)
    assert r.status_code == 200, r.text

    data = r.json()
    assert str(data["id"]) == str(sid)


@pytest.mark.anyio
async def test_04_update_setting(api_context, auth_headers, ensure_created_setting):
    """
    PUT /settings/{id}
    """
    sid = ensure_created_setting["setting_id"]
    payload = mock["setting_update"].copy()

    r = await api_context.put(f"{BASE}/{sid}", json=payload, headers=auth_headers)
    assert r.status_code == 200, r.text

    updated = r.json()
    assert str(updated["id"]) == str(sid)

    # Best-effort asserts
    for k, v in payload.items():
        if v is not None:
            assert updated.get(k) == v


@pytest.mark.anyio
async def test_05_upload_logo(api_context, auth_headers, ensure_created_setting):
    """
    POST /settings/logo/upload/{appId}
    """
    sid = ensure_created_setting["setting_id"]

    # tiny valid PNG bytes
    png_bytes = (
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR"
        b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00"
        b"\x1f\x15\xc4\x89"
        b"\x00\x00\x00\x0bIDATx\x9cc`\x00\x00\x00\x02\x00\x01"
        b"\xe2!\xbc3"
        b"\x00\x00\x00\x00IEND\xaeB`\x82"
    )

    files = {"file": ("logo.png", png_bytes, "image/png")}

    r = await api_context.post(f"{UPLOAD}/{sid}", files=files, headers=auth_headers)
    assert r.status_code == 200, r.text

    data = r.json()
    assert "filename" in data
    assert "url" in data
    assert data["url"].startswith("/uploads/")


@pytest.mark.anyio
async def test_06_upload_logo_rejects_non_image(api_context, auth_headers, ensure_created_setting):
    """
    POST /settings/logo/upload/{appId} rejects non-image
    """
    sid = ensure_created_setting["setting_id"]

    files = {"file": ("not_image.txt", b"hello", "text/plain")}

    r = await api_context.post(f"{UPLOAD}/{sid}", files=files, headers=auth_headers)
    assert r.status_code == 400, r.text


@pytest.mark.anyio
async def test_07_get_unknown_setting_returns_404(api_context, auth_headers):
    """
    GET /settings/{id} unknown -> 404
    """
    r = await api_context.get(f"{BASE}/999999999", headers=auth_headers)
    assert r.status_code == 404, r.text