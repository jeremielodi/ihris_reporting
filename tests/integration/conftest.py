import os
import pytest
from httpx import AsyncClient
from helpers import load_mock

@pytest.fixture
def base_url():
    return os.getenv("BASE_URL", "http://localhost:8000")

@pytest.fixture
async def api_context(base_url):
    async with AsyncClient(base_url=base_url, timeout=30.0, follow_redirects=True) as client:
        yield client

@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest.fixture
def mock_loader():
    return load_mock

@pytest.fixture
async def auth_headers(api_context):
    # Default credentials (can be overridden by env vars)
    username = os.getenv("TEST_USERNAME", "ihris")
    password = os.getenv("TEST_PASSWORD", "admin")

    r = await api_context.post(
        "/users/reporting/login",
        json={"username": username, "password": password},
        headers={"Accept": "application/json"},
    )

    # If login fails, show body to debug
    assert r.status_code == 200, f"Login failed: {r.status_code} {r.text}"

    data = r.json()

    # Adjust key name if your API returns something else:
    # common: access_token / token
    token = data.get("access_token") or data.get("token")
    assert token, f"Token not found in login response: {data}"

    return {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
        # If your API uses x-access-token instead, use this line instead:
        # "x-access-token": token,
    }