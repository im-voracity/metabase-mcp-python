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
    mcp_with_additional_tools: FastMCP, mock_client: AsyncMock,
) -> None:
    mock_client.get_collections.return_value = [{"id": 1, "name": "Root"}]
    result = await mcp_with_additional_tools.call_tool("list_collections", {})
    mock_client.get_collections.assert_awaited_once()
    data = json.loads(result.content[0].text)
    assert data[0]["name"] == "Root"


@pytest.mark.asyncio
async def test_search_content_tool(
    mcp_with_additional_tools: FastMCP, mock_client: AsyncMock,
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
