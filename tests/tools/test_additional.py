"""Tests for additional tool registration and execution."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest
from fastmcp import FastMCP

from metabase_mcp.tools.additional import register_additional_tools


@pytest.fixture
def mcp_with_additional_tools(mcp: FastMCP, mock_client: AsyncMock) -> FastMCP:
    register_additional_tools(mcp, mock_client)
    return mcp


@pytest.mark.asyncio
async def test_list_collections_tool(
    mcp_with_additional_tools: FastMCP,
    mock_client: AsyncMock,
) -> None:
    mock_client.get_collections.return_value = [{"id": 1, "name": "Root"}]
    result = await mcp_with_additional_tools.call_tool("list_collections", {})
    mock_client.get_collections.assert_awaited_once()
    data = json.loads(result.content[0].text)
    assert data[0]["name"] == "Root"


@pytest.mark.asyncio
async def test_search_content_tool(
    mcp_with_additional_tools: FastMCP,
    mock_client: AsyncMock,
) -> None:
    mock_client.api_call.return_value = {"data": [{"name": "Sales"}]}
    result = await mcp_with_additional_tools.call_tool("search_content", {"q": "Sales"})
    mock_client.api_call.assert_awaited_once()
    data = json.loads(result.content[0].text)
    assert "data" in data


@pytest.mark.asyncio
async def test_list_users_tool(mcp_with_additional_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.get_users.return_value = [{"id": 1, "email": "admin@test.com"}]
    result = await mcp_with_additional_tools.call_tool("list_users", {})
    mock_client.get_users.assert_awaited_once()
    data = json.loads(result.content[0].text)
    assert data[0]["email"] == "admin@test.com"


@pytest.mark.asyncio
async def test_get_collection_items_tool(
    mcp_with_additional_tools: FastMCP,
    mock_client: AsyncMock,
) -> None:
    mock_client.api_call.return_value = [{"id": 1, "model": "card"}]
    result = await mcp_with_additional_tools.call_tool("get_collection_items", {"collection_id": 1})
    data = json.loads(result.content[0].text)
    assert data[0]["model"] == "card"


@pytest.mark.asyncio
async def test_move_to_collection_tool(
    mcp_with_additional_tools: FastMCP,
    mock_client: AsyncMock,
) -> None:
    mock_client.api_call.return_value = {"id": 5, "collection_id": 3}
    result = await mcp_with_additional_tools.call_tool(
        "move_to_collection",
        {
            "item_type": "card",
            "item_id": 5,
            "collection_id": 3,
        },
    )
    data = json.loads(result.content[0].text)
    assert data["collection_id"] == 3


@pytest.mark.asyncio
async def test_search_content_with_filters(
    mcp_with_additional_tools: FastMCP,
    mock_client: AsyncMock,
) -> None:
    mock_client.api_call.return_value = {"data": []}
    result = await mcp_with_additional_tools.call_tool(
        "search_content",
        {
            "q": "revenue",
            "type": "card",
            "archived": True,
            "table_db_id": 1,
            "limit": 5,
        },
    )
    data = json.loads(result.content[0].text)
    assert "data" in data
    # Verify query string was built with filters
    call_args = mock_client.api_call.call_args[0]
    url = call_args[1]
    assert "type=card" in url
    assert "limit=5" in url


@pytest.mark.asyncio
async def test_create_collection_tool(
    mcp_with_additional_tools: FastMCP,
    mock_client: AsyncMock,
) -> None:
    mock_client.create_collection.return_value = {"id": 10, "name": "New Col"}
    result = await mcp_with_additional_tools.call_tool(
        "create_collection",
        {
            "name": "New Col",
            "description": "A test collection",
        },
    )
    data = json.loads(result.content[0].text)
    assert data["name"] == "New Col"


@pytest.mark.asyncio
async def test_update_collection_tool(
    mcp_with_additional_tools: FastMCP,
    mock_client: AsyncMock,
) -> None:
    mock_client.update_collection.return_value = {"id": 1, "name": "Renamed"}
    result = await mcp_with_additional_tools.call_tool(
        "update_collection",
        {
            "collection_id": 1,
            "name": "Renamed",
        },
    )
    data = json.loads(result.content[0].text)
    assert data["name"] == "Renamed"


@pytest.mark.asyncio
async def test_delete_collection_tool(
    mcp_with_additional_tools: FastMCP,
    mock_client: AsyncMock,
) -> None:
    mock_client.delete_collection.return_value = None
    result = await mcp_with_additional_tools.call_tool("delete_collection", {"collection_id": 1})
    data = json.loads(result.content[0].text)
    assert data["action"] == "deleted"


@pytest.mark.asyncio
async def test_get_metabase_playground_link_tool(
    mcp_with_additional_tools: FastMCP,
    mock_client: AsyncMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("METABASE_URL", "http://localhost:3000")
    result = await mcp_with_additional_tools.call_tool(
        "get_metabase_playground_link",
        {
            "query": "SELECT 1",
        },
    )
    data = json.loads(result.content[0].text)
    assert "playground_url" in data
    assert data["playground_url"].startswith("http://localhost:3000/question#")
