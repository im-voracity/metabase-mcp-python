"""Tests for bookmark tool registration and execution."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest
from fastmcp import FastMCP

from metabase_mcp.tools.bookmark import register_bookmark_tools


@pytest.fixture
def mcp_with_bookmark_tools(mcp: FastMCP, mock_client: AsyncMock) -> FastMCP:
    register_bookmark_tools(mcp, mock_client)
    return mcp


@pytest.mark.asyncio
async def test_list_bookmarks_tool(
    mcp_with_bookmark_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.get_bookmarks.return_value = [
        {"id": 1, "type": "card", "item_id": 5, "name": "My Card"}
    ]
    result = await mcp_with_bookmark_tools.call_tool("list_bookmarks", {})
    mock_client.get_bookmarks.assert_awaited_once()
    data = json.loads(result.content[0].text)
    assert len(data) == 1
    assert data[0]["type"] == "card"


@pytest.mark.asyncio
async def test_create_bookmark_tool(
    mcp_with_bookmark_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.create_bookmark.return_value = {"id": 1, "type": "card", "item_id": 5}
    result = await mcp_with_bookmark_tools.call_tool(
        "create_bookmark", {"model": "card", "model_id": 5}
    )
    mock_client.create_bookmark.assert_awaited_once_with("card", 5)
    data = json.loads(result.content[0].text)
    assert data["type"] == "card"


@pytest.mark.asyncio
async def test_delete_bookmark_tool(
    mcp_with_bookmark_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.delete_bookmark.return_value = None
    result = await mcp_with_bookmark_tools.call_tool(
        "delete_bookmark", {"model": "dashboard", "model_id": 3}
    )
    mock_client.delete_bookmark.assert_awaited_once_with("dashboard", 3)
    data = json.loads(result.content[0].text)
    assert data["status"] == "success"


@pytest.mark.asyncio
async def test_reorder_bookmarks_tool(
    mcp_with_bookmark_tools: FastMCP, mock_client: AsyncMock
) -> None:
    orderings = [
        {"type": "card", "item_id": 5},
        {"type": "dashboard", "item_id": 3},
    ]
    mock_client.reorder_bookmarks.return_value = None
    result = await mcp_with_bookmark_tools.call_tool(
        "reorder_bookmarks", {"orderings": orderings}
    )
    mock_client.reorder_bookmarks.assert_awaited_once_with(orderings)
    data = json.loads(result.content[0].text)
    assert data["status"] == "success"
