"""Tests for MetabaseClient using respx to mock httpx."""

from __future__ import annotations

import contextlib

import httpx
import pytest
import respx
from httpx import Response

from metabase_mcp.client import MetabaseClient
from metabase_mcp.config import MetabaseConfig
from metabase_mcp.exceptions import (
    MetabaseAPIError,
    MetabaseAuthError,
    MetabaseNotFoundError,
)


@pytest.fixture
def api_key_config(monkeypatch: pytest.MonkeyPatch) -> MetabaseConfig:
    monkeypatch.delenv("METABASE_URL", raising=False)
    monkeypatch.delenv("METABASE_API_KEY", raising=False)
    return MetabaseConfig(url="http://localhost:3000", api_key="mb_test_key", _env_file=None)  # type: ignore[call-arg]


@pytest.fixture
def credential_config(monkeypatch: pytest.MonkeyPatch) -> MetabaseConfig:
    monkeypatch.delenv("METABASE_URL", raising=False)
    monkeypatch.delenv("METABASE_API_KEY", raising=False)
    monkeypatch.delenv("METABASE_USERNAME", raising=False)
    monkeypatch.delenv("METABASE_PASSWORD", raising=False)
    return MetabaseConfig(  # type: ignore[call-arg]
        url="http://localhost:3000",
        username="user@test.com",
        password="secret",
        _env_file=None,
    )


@respx.mock
@pytest.mark.asyncio
async def test_get_databases_with_api_key(api_key_config: MetabaseConfig) -> None:
    route = respx.get("http://localhost:3000/api/database").mock(
        return_value=Response(200, json={"data": [{"id": 1, "name": "DB"}]})
    )
    async with MetabaseClient(api_key_config) as client:
        result = await client.get_databases()
    assert result == {"data": [{"id": 1, "name": "DB"}]}
    assert route.called
    assert route.calls[0].request.headers["x-api-key"] == "mb_test_key"


def test_session_auth_sets_header(credential_config: MetabaseConfig) -> None:
    """Verify MetabaseAuth sets X-Metabase-Session header after login."""
    import time

    from metabase_mcp.client import MetabaseAuth

    auth = MetabaseAuth(credential_config)
    auth._session_token = "session-token-123"
    auth._token_obtained_at = time.monotonic()  # Token is fresh

    request = httpx.Request("GET", "http://localhost:3000/api/database")
    flow = auth.auth_flow(request)
    modified_request = next(flow)
    assert modified_request.headers["x-metabase-session"] == "session-token-123"


def test_session_auth_acquires_token_when_expired(
    credential_config: MetabaseConfig,
) -> None:
    """Verify MetabaseAuth acquires a new token when the current one is expired."""
    from metabase_mcp.client import MetabaseAuth

    auth = MetabaseAuth(credential_config)
    # No token set → _is_token_expired() returns True

    request = httpx.Request("GET", "http://localhost:3000/api/database")
    flow = auth.auth_flow(request)

    # First yield: login request
    login_request = next(flow)
    assert login_request.url == "http://localhost:3000/api/session"

    # Send successful login response
    login_response = Response(200, json={"id": "new-session-token"})
    actual_request = flow.send(login_response)
    assert actual_request.headers["x-metabase-session"] == "new-session-token"


def test_session_auth_clears_token_on_401(
    credential_config: MetabaseConfig,
) -> None:
    """Verify MetabaseAuth clears the session token when a 401 is received."""
    import time

    from metabase_mcp.client import MetabaseAuth

    auth = MetabaseAuth(credential_config)
    auth._session_token = "old-token"
    auth._token_obtained_at = time.monotonic()

    request = httpx.Request("GET", "http://localhost:3000/api/database")
    flow = auth.auth_flow(request)

    # First yield: the actual request with session header
    actual_request = next(flow)
    assert actual_request.headers["x-metabase-session"] == "old-token"

    # Send 401 response → token should be cleared
    with contextlib.suppress(StopIteration):
        flow.send(Response(401, text="Unauthorized"))

    assert auth._session_token is None
    assert auth._token_obtained_at == 0.0


def test_session_auth_raises_on_login_failure(
    credential_config: MetabaseConfig,
) -> None:
    """Verify MetabaseAuth raises MetabaseAuthError when login fails."""
    from metabase_mcp.client import MetabaseAuth

    auth = MetabaseAuth(credential_config)

    request = httpx.Request("GET", "http://localhost:3000/api/database")
    flow = auth.auth_flow(request)

    # First yield: login request
    login_request = next(flow)
    assert login_request.url == "http://localhost:3000/api/session"

    # Send failed login response
    with pytest.raises(MetabaseAuthError, match="Failed to authenticate"):
        flow.send(Response(401, text="Bad credentials"))


def test_session_auth_refreshes_before_expiry(
    credential_config: MetabaseConfig,
) -> None:
    """Verify token is refreshed when approaching TTL (90% margin)."""
    import time

    from metabase_mcp.client import MetabaseAuth

    auth = MetabaseAuth(credential_config)
    auth._session_token = "stale-token"
    # Set obtained_at far in the past to simulate expiration
    auth._token_obtained_at = time.monotonic() - (
        MetabaseAuth.TOKEN_TTL_SECONDS * MetabaseAuth.TOKEN_REFRESH_MARGIN + 1
    )

    request = httpx.Request("GET", "http://localhost:3000/api/database")
    flow = auth.auth_flow(request)

    # Should yield login request (not use stale token)
    login_request = next(flow)
    assert login_request.url == "http://localhost:3000/api/session"

    # Complete login
    actual_request = flow.send(Response(200, json={"id": "refreshed-token"}))
    assert actual_request.headers["x-metabase-session"] == "refreshed-token"


def test_api_key_auth_sets_header(api_key_config: MetabaseConfig) -> None:
    """Verify MetabaseAuth sets X-API-Key header."""
    from metabase_mcp.client import MetabaseAuth

    auth = MetabaseAuth(api_key_config)
    request = httpx.Request("GET", "http://localhost:3000/api/database")
    flow = auth.auth_flow(request)
    modified_request = next(flow)
    assert modified_request.headers["x-api-key"] == "mb_test_key"


@respx.mock
@pytest.mark.asyncio
async def test_get_dashboard(api_key_config: MetabaseConfig) -> None:
    payload = {"id": 1, "name": "Sales", "dashcards": []}
    respx.get("http://localhost:3000/api/dashboard/1").mock(
        return_value=Response(200, json=payload)
    )
    async with MetabaseClient(api_key_config) as client:
        result = await client.get_dashboard(1)
    assert result["name"] == "Sales"


@respx.mock
@pytest.mark.asyncio
async def test_create_dashboard(api_key_config: MetabaseConfig) -> None:
    payload = {"id": 2, "name": "New Dashboard"}
    respx.post("http://localhost:3000/api/dashboard").mock(
        return_value=Response(200, json=payload)
    )
    async with MetabaseClient(api_key_config) as client:
        result = await client.create_dashboard({"name": "New Dashboard"})
    assert result["id"] == 2


@respx.mock
@pytest.mark.asyncio
async def test_update_card(api_key_config: MetabaseConfig) -> None:
    respx.put("http://localhost:3000/api/card/5").mock(
        return_value=Response(200, json={"id": 5, "name": "Updated"})
    )
    async with MetabaseClient(api_key_config) as client:
        result = await client.update_card(5, {"name": "Updated"})
    assert result["name"] == "Updated"


@respx.mock
@pytest.mark.asyncio
async def test_delete_card_hard(api_key_config: MetabaseConfig) -> None:
    respx.delete("http://localhost:3000/api/card/3").mock(
        return_value=Response(204)
    )
    async with MetabaseClient(api_key_config) as client:
        result = await client.delete_card(3, hard_delete=True)
    assert result is None


@respx.mock
@pytest.mark.asyncio
async def test_delete_card_soft_archives(api_key_config: MetabaseConfig) -> None:
    respx.put("http://localhost:3000/api/card/3").mock(
        return_value=Response(200, json={"id": 3, "archived": True})
    )
    async with MetabaseClient(api_key_config) as client:
        result = await client.delete_card(3)
    assert result["archived"] is True


@respx.mock
@pytest.mark.asyncio
async def test_execute_query(api_key_config: MetabaseConfig) -> None:
    query_result = {"data": {"rows": [[42]], "cols": [{"name": "answer"}]}}
    respx.post("http://localhost:3000/api/dataset").mock(
        return_value=Response(200, json=query_result)
    )
    async with MetabaseClient(api_key_config) as client:
        result = await client.execute_query(1, "SELECT 42 AS answer")
    assert result["data"]["rows"][0][0] == 42


@respx.mock
@pytest.mark.asyncio
async def test_error_401_raises_auth_error(api_key_config: MetabaseConfig) -> None:
    respx.get("http://localhost:3000/api/database").mock(
        return_value=Response(401, text="Unauthorized")
    )
    async with MetabaseClient(api_key_config) as client:
        with pytest.raises(MetabaseAuthError) as exc_info:
            await client.get_databases()
    assert "Unauthorized" not in str(exc_info.value)
    assert "HTTP 401" in str(exc_info.value)


@respx.mock
@pytest.mark.asyncio
async def test_error_403_raises_auth_error(api_key_config: MetabaseConfig) -> None:
    respx.get("http://localhost:3000/api/dashboard").mock(
        return_value=Response(403, text="Forbidden")
    )
    async with MetabaseClient(api_key_config) as client:
        with pytest.raises(MetabaseAuthError) as exc_info:
            await client.get_dashboards()
    assert "Forbidden" not in str(exc_info.value)
    assert "HTTP 403" in str(exc_info.value)


@respx.mock
@pytest.mark.asyncio
async def test_error_404_raises_not_found(api_key_config: MetabaseConfig) -> None:
    respx.get("http://localhost:3000/api/dashboard/999").mock(
        return_value=Response(404, text="Not found")
    )
    async with MetabaseClient(api_key_config) as client:
        with pytest.raises(MetabaseNotFoundError):
            await client.get_dashboard(999)


@respx.mock
@pytest.mark.asyncio
async def test_error_500_does_not_leak_response_body(api_key_config: MetabaseConfig) -> None:
    sensitive_body = '{"message":"User admin@corp.com lacks permission"}'
    respx.get("http://localhost:3000/api/database").mock(
        return_value=Response(500, text=sensitive_body)
    )
    async with MetabaseClient(api_key_config) as client:
        with pytest.raises(MetabaseAPIError) as exc_info:
            await client.get_databases()
    assert "admin@corp.com" not in str(exc_info.value)
    assert "HTTP 500" in str(exc_info.value)


@respx.mock
@pytest.mark.asyncio
async def test_empty_response_returns_none(api_key_config: MetabaseConfig) -> None:
    respx.delete("http://localhost:3000/api/card/1").mock(
        return_value=Response(204)
    )
    async with MetabaseClient(api_key_config) as client:
        result = await client.delete_card(1, hard_delete=True)
    assert result is None


@respx.mock
@pytest.mark.asyncio
async def test_get_collections(api_key_config: MetabaseConfig) -> None:
    respx.get("http://localhost:3000/api/collection").mock(
        return_value=Response(200, json=[{"id": 1, "name": "Root"}])
    )
    async with MetabaseClient(api_key_config) as client:
        result = await client.get_collections()
    assert isinstance(result, list)
    assert result[0]["name"] == "Root"


@respx.mock
@pytest.mark.asyncio
async def test_execute_card(api_key_config: MetabaseConfig) -> None:
    respx.post("http://localhost:3000/api/card/1/query").mock(
        return_value=Response(200, json={"data": {"rows": [[1]]}})
    )
    async with MetabaseClient(api_key_config) as client:
        result = await client.execute_card(1)
    assert result["data"]["rows"] == [[1]]


@respx.mock
@pytest.mark.asyncio
async def test_url_encodes_string_path_params(api_key_config: MetabaseConfig) -> None:
    """Verify that string parameters in URL paths are properly encoded."""
    route = respx.get(
        "http://localhost:3000/api/card/1/params/my%20key/search/foo%2Fbar"
    ).mock(return_value=Response(200, json={"values": []}))
    async with MetabaseClient(api_key_config) as client:
        await client.search_card_param_values(1, "my key", "foo/bar")
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_url_encodes_schema_param(api_key_config: MetabaseConfig) -> None:
    """Verify that schema name with special chars is encoded in path."""
    route = respx.get(
        "http://localhost:3000/api/database/1/schema/public%2Ftest"
    ).mock(return_value=Response(200, json=[]))
    async with MetabaseClient(api_key_config) as client:
        await client.get_database_schema(1, "public/test")
    assert route.called
