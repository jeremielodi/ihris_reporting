import uuid
import pytest
from helpers import load_mock

BASE = "/manage/users"
mock = load_mock("user")


@pytest.fixture(scope="module")
def state():
    """
    Stores created setting id for this module tests.
    """
    return {}


@pytest.fixture(scope="module")
def unique_suffix():
    return uuid.uuid4().hex[:8]


@pytest.mark.anyio
async def test_01_get_users_list(api_context, auth_headers):
    """
    GET /manage/users/
    Just verifies the endpoint is reachable and returns a list.
    """
    r = await api_context.get(f"{BASE}/", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert isinstance(r.json(), list)


@pytest.mark.anyio
async def test_02_create_user(api_context, auth_headers, state):
    """
    POST /manage/users/
    Creates a user and stores user_id in state for later tests.
    """
    payload = mock["user_create"].copy()

    # Make username/email unique per run
    suffix = uuid.uuid4().hex[:8]
    payload["username"] = f"{payload['username']}_{suffix}"
    payload["email"] = payload["email"].replace("@", f"_{suffix}@")

    r = await api_context.post(f"{BASE}/", json=payload, headers=auth_headers)
    assert r.status_code in (200, 201), r.text

    created = r.json()
    assert "id" in created, created
    assert created["id"] == f"user|{payload['username']}"
    assert created.get("username") == payload["username"]

    # Save for next tests
    state["user_id"] = created["id"]
    state["username"] = payload["username"]
    state["password"] = payload["password"]
    state["facility_id"] = payload["facility_id"]


@pytest.mark.anyio
async def test_03_get_user_by_id(api_context, auth_headers, state):
    """
    GET /manage/users/{user_id}
    """
    r = await api_context.get(f"{BASE}/{state['user_id']}", headers=auth_headers)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["id"] == state["user_id"]
    assert data.get("username") == state["username"]


@pytest.mark.anyio
async def test_04_update_user(api_context, auth_headers, state):
    """
    PUT /manage/users/{user_id}
    Updates username/email and facility_id.
    """
    payload = mock["user_update"].copy()

    suffix = uuid.uuid4().hex[:8]
    payload["username"] = f"{payload['username']}_{suffix}"
    payload["email"] = payload["email"].replace("@", f"_{suffix}@")

    # HippoUserUpdate requires id
    payload["id"] = state["user_id"]

    r = await api_context.put(
        f"{BASE}/{state['user_id']}",
        json=payload,
        headers=auth_headers
    )
    assert r.status_code == 200, r.text

    updated = r.json()
    assert updated["id"] == state["user_id"]
    assert updated.get("username") == payload["username"]

    # Update state for password test (username changed, but password might not)
    state["username"] = payload["username"]

    # If you changed password in update, store it
    if payload.get("password"):
        state["password"] = payload["password"]


@pytest.mark.anyio
async def test_05_change_self_password(api_context, auth_headers, state):
    """
    POST /manage/users/changeSelfPassword
    This requires:
      - correct old_password (must match hashed password in DB)
      - new_password == confirm_password
      - user_id
    """
    payload = mock["user_change_password"].copy()
    payload["user_id"] = state["user_id"]

    # IMPORTANT:
    # old_password must be the current user's password in DB.
    # We stored it in state from create/update.
    payload["old_password"] = state["password"]

    r = await api_context.post(
        f"{BASE}/changeSelfPassword",
        json=payload,
        headers=auth_headers
    )
    assert r.status_code == 200, r.text

    # After change, keep new password in state (optional)
    state["password"] = payload["new_password"]


@pytest.mark.anyio
async def test_06_get_user_404(api_context, auth_headers):
    """
    GET /manage/users/{user_id} -> 404 for non existing user
    """
    r = await api_context.get(f"{BASE}/user|not_exists_123", headers=auth_headers)
    assert r.status_code == 404, r.text
    assert r.json().get("detail") == "User not found"