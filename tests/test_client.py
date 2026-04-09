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
    MetabaseError,
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
    respx.post("http://localhost:3000/api/dashboard").mock(return_value=Response(200, json=payload))
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
    respx.delete("http://localhost:3000/api/card/3").mock(return_value=Response(204))
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
    respx.delete("http://localhost:3000/api/card/1").mock(return_value=Response(204))
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
async def test_request_timeout_raises_metabase_error(api_key_config: MetabaseConfig) -> None:
    """Verify TimeoutException is wrapped in MetabaseError."""
    respx.get("http://localhost:3000/api/database").mock(
        side_effect=httpx.TimeoutException("timed out")
    )
    async with MetabaseClient(api_key_config) as client:
        with pytest.raises(MetabaseError, match="Request timed out"):
            await client.get_databases()


@respx.mock
@pytest.mark.asyncio
async def test_request_http_error_raises_metabase_error(api_key_config: MetabaseConfig) -> None:
    """Verify generic HTTPError is wrapped in MetabaseError."""
    respx.get("http://localhost:3000/api/database").mock(
        side_effect=httpx.HTTPError("connection reset")
    )
    async with MetabaseClient(api_key_config) as client:
        with pytest.raises(MetabaseError, match="HTTP error"):
            await client.get_databases()


@respx.mock
@pytest.mark.asyncio
async def test_get_field_by_name_found(api_key_config: MetabaseConfig) -> None:
    """Verify get_field_by_name returns field info when found."""
    metadata = {
        "fields": [
            {"id": 10, "name": "user_id", "display_name": "User ID", "base_type": "type/Integer"},
            {"id": 11, "name": "email", "display_name": "Email", "base_type": "type/Text"},
        ]
    }
    respx.get("http://localhost:3000/api/table/1/query_metadata").mock(
        return_value=Response(200, json=metadata)
    )
    async with MetabaseClient(api_key_config) as client:
        result = await client.get_field_by_name(1, "email")
    assert result["field_id"] == 11
    assert result["name"] == "email"


@respx.mock
@pytest.mark.asyncio
async def test_get_field_by_name_case_insensitive(api_key_config: MetabaseConfig) -> None:
    """Verify get_field_by_name matches case-insensitively."""
    metadata = {
        "fields": [
            {"id": 10, "name": "USER_ID", "display_name": "User ID", "base_type": "type/Integer"}
        ]
    }
    respx.get("http://localhost:3000/api/table/1/query_metadata").mock(
        return_value=Response(200, json=metadata)
    )
    async with MetabaseClient(api_key_config) as client:
        result = await client.get_field_by_name(1, "user_id")
    assert result["field_id"] == 10


@respx.mock
@pytest.mark.asyncio
async def test_get_field_by_name_not_found(api_key_config: MetabaseConfig) -> None:
    """Verify get_field_by_name raises MetabaseError when field not found."""
    metadata = {"fields": [{"id": 10, "name": "user_id"}]}
    respx.get("http://localhost:3000/api/table/1/query_metadata").mock(
        return_value=Response(200, json=metadata)
    )
    async with MetabaseClient(api_key_config) as client:
        with pytest.raises(MetabaseError, match="not found"):
            await client.get_field_by_name(1, "nonexistent")


@respx.mock
@pytest.mark.asyncio
async def test_get_field_by_name_truncates_long_list(api_key_config: MetabaseConfig) -> None:
    """Verify error message truncates field list when >20 fields."""
    fields = [{"id": i, "name": f"field_{i}"} for i in range(25)]
    metadata = {"fields": fields}
    respx.get("http://localhost:3000/api/table/1/query_metadata").mock(
        return_value=Response(200, json=metadata)
    )
    async with MetabaseClient(api_key_config) as client:
        with pytest.raises(MetabaseError, match=r"\.\.\."):
            await client.get_field_by_name(1, "nonexistent")


@respx.mock
@pytest.mark.asyncio
async def test_add_card_to_dashboard(api_key_config: MetabaseConfig) -> None:
    """Verify add_card_to_dashboard builds correct payload."""
    respx.get("http://localhost:3000/api/dashboard/1").mock(
        return_value=Response(200, json={"id": 1, "dashcards": [], "tabs": []})
    )
    respx.put("http://localhost:3000/api/dashboard/1").mock(
        return_value=Response(200, json={"id": 1, "dashcards": [{"id": -1, "card_id": 5}]})
    )
    async with MetabaseClient(api_key_config) as client:
        result = await client.add_card_to_dashboard(1, {"card_id": 5})
    assert result["dashcards"][0]["card_id"] == 5


@respx.mock
@pytest.mark.asyncio
async def test_update_dashcard_not_found(api_key_config: MetabaseConfig) -> None:
    """Verify update_dashcard raises error when dashcard not found."""
    respx.get("http://localhost:3000/api/dashboard/1").mock(
        return_value=Response(200, json={"id": 1, "dashcards": [{"id": 10}]})
    )
    async with MetabaseClient(api_key_config) as client:
        with pytest.raises(MetabaseError, match="not found"):
            await client.update_dashcard(1, 999, {"size_x": 6})


@respx.mock
@pytest.mark.asyncio
async def test_remove_cards_from_dashboard(api_key_config: MetabaseConfig) -> None:
    """Verify remove_cards_from_dashboard filters out specified dashcard IDs."""
    respx.get("http://localhost:3000/api/dashboard/1").mock(
        return_value=Response(
            200,
            json={
                "id": 1,
                "dashcards": [{"id": 10}, {"id": 20}, {"id": 30}],
            },
        )
    )
    route = respx.put("http://localhost:3000/api/dashboard/1").mock(
        return_value=Response(200, json={"id": 1, "dashcards": [{"id": 10}]})
    )
    async with MetabaseClient(api_key_config) as client:
        await client.remove_cards_from_dashboard(1, [20, 30])
    sent = route.calls[0].request.content
    import json as _json

    body = _json.loads(sent)
    # Only dashcard 10 should remain
    assert len([dc for dc in body["dashcards"] if dc["id"] not in [20, 30]]) == 1


@respx.mock
@pytest.mark.asyncio
async def test_delete_dashboard_soft(api_key_config: MetabaseConfig) -> None:
    """Verify soft delete archives the dashboard."""
    route = respx.put("http://localhost:3000/api/dashboard/1").mock(
        return_value=Response(200, json={"id": 1, "archived": True})
    )
    async with MetabaseClient(api_key_config) as client:
        result = await client.delete_dashboard(1)
    assert result["archived"] is True
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_delete_dashboard_hard(api_key_config: MetabaseConfig) -> None:
    """Verify hard delete sends DELETE request."""
    route = respx.delete("http://localhost:3000/api/dashboard/1").mock(return_value=Response(204))
    async with MetabaseClient(api_key_config) as client:
        result = await client.delete_dashboard(1, hard_delete=True)
    assert result is None
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_copy_dashboard(api_key_config: MetabaseConfig) -> None:
    respx.post("http://localhost:3000/api/dashboard/1/copy").mock(
        return_value=Response(200, json={"id": 2, "name": "Copy"})
    )
    async with MetabaseClient(api_key_config) as client:
        result = await client.copy_dashboard(1, {"name": "Copy"})
    assert result["name"] == "Copy"


@respx.mock
@pytest.mark.asyncio
async def test_get_collections_archived(api_key_config: MetabaseConfig) -> None:
    route = respx.get("http://localhost:3000/api/collection").mock(
        return_value=Response(200, json=[])
    )
    async with MetabaseClient(api_key_config) as client:
        await client.get_collections(archived=True)
    assert "archived=true" in str(route.calls[0].request.url)


@respx.mock
@pytest.mark.asyncio
async def test_create_collection(api_key_config: MetabaseConfig) -> None:
    respx.post("http://localhost:3000/api/collection").mock(
        return_value=Response(200, json={"id": 5, "name": "New"})
    )
    async with MetabaseClient(api_key_config) as client:
        result = await client.create_collection({"name": "New"})
    assert result["name"] == "New"


@respx.mock
@pytest.mark.asyncio
async def test_get_users(api_key_config: MetabaseConfig) -> None:
    respx.get("http://localhost:3000/api/user").mock(return_value=Response(200, json=[{"id": 1}]))
    async with MetabaseClient(api_key_config) as client:
        result = await client.get_users()
    assert len(result) == 1


@respx.mock
@pytest.mark.asyncio
async def test_execute_query_with_params(api_key_config: MetabaseConfig) -> None:
    route = respx.post("http://localhost:3000/api/dataset").mock(
        return_value=Response(200, json={"data": {"rows": []}})
    )
    async with MetabaseClient(api_key_config) as client:
        await client.execute_query(1, "SELECT ?", [42])
    import json as _json

    body = _json.loads(route.calls[0].request.content)
    assert body["parameters"] == [42]


@respx.mock
@pytest.mark.asyncio
async def test_append_csv_to_table(api_key_config: MetabaseConfig) -> None:
    route = respx.post("http://localhost:3000/api/table/1/append-csv").mock(
        return_value=Response(200, json={"status": "ok"})
    )
    async with MetabaseClient(api_key_config) as client:
        result = await client.append_csv_to_table(1, "data.csv", "a,b\n1,2")
    assert result["status"] == "ok"
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_replace_table_csv(api_key_config: MetabaseConfig) -> None:
    route = respx.post("http://localhost:3000/api/table/1/replace-csv").mock(
        return_value=Response(200, json={"status": "ok"})
    )
    async with MetabaseClient(api_key_config) as client:
        result = await client.replace_table_csv(1, "a,b\n1,2")
    assert result["status"] == "ok"
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_api_call_with_data(api_key_config: MetabaseConfig) -> None:
    route = respx.post("http://localhost:3000/api/custom/endpoint").mock(
        return_value=Response(200, json={"ok": True})
    )
    async with MetabaseClient(api_key_config) as client:
        result = await client.api_call("POST", "/api/custom/endpoint", {"key": "val"})
    assert result["ok"] is True
    import json as _json

    body = _json.loads(route.calls[0].request.content)
    assert body["key"] == "val"


@respx.mock
@pytest.mark.asyncio
async def test_api_call_without_data(api_key_config: MetabaseConfig) -> None:
    respx.get("http://localhost:3000/api/custom/endpoint").mock(
        return_value=Response(200, json={"ok": True})
    )
    async with MetabaseClient(api_key_config) as client:
        result = await client.api_call("GET", "/api/custom/endpoint")
    assert result["ok"] is True


@respx.mock
@pytest.mark.asyncio
async def test_url_encodes_string_path_params(api_key_config: MetabaseConfig) -> None:
    """Verify that string parameters in URL paths are properly encoded."""
    route = respx.get("http://localhost:3000/api/card/1/params/my%20key/search/foo%2Fbar").mock(
        return_value=Response(200, json={"values": []})
    )
    async with MetabaseClient(api_key_config) as client:
        await client.search_card_param_values(1, "my key", "foo/bar")
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_url_encodes_schema_param(api_key_config: MetabaseConfig) -> None:
    """Verify that schema name with special chars is encoded in path."""
    route = respx.get("http://localhost:3000/api/database/1/schema/public%2Ftest").mock(
        return_value=Response(200, json=[])
    )
    async with MetabaseClient(api_key_config) as client:
        await client.get_database_schema(1, "public/test")
    assert route.called
