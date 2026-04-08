"""Tests for table tool registration and execution."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest
from fastmcp import FastMCP

from metabase_mcp.tools.table import register_table_tools


@pytest.fixture
def mcp_with_table_tools(mcp: FastMCP, mock_client: AsyncMock) -> FastMCP:
    register_table_tools(mcp, mock_client)
    return mcp


@pytest.mark.asyncio
async def test_list_tables_tool(mcp_with_table_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.get_tables.return_value = [{"id": 1, "name": "users"}]
    result = await mcp_with_table_tools.call_tool("list_tables", {})
    mock_client.get_tables.assert_awaited_once()
    data = json.loads(result.content[0].text)
    assert data[0]["name"] == "users"


@pytest.mark.asyncio
async def test_get_table_query_metadata_tool(
    mcp_with_table_tools: FastMCP, mock_client: AsyncMock,
) -> None:
    mock_client.get_table_query_metadata.return_value = {"id": 1, "fields": []}
    result = await mcp_with_table_tools.call_tool(
        "get_table_query_metadata", {"table_id": 1},
    )
    mock_client.get_table_query_metadata.assert_awaited_once()
    data = json.loads(result.content[0].text)
    assert "fields" in data


@pytest.mark.asyncio
async def test_get_table_data_tool(mcp_with_table_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.get_table_data.return_value = {"data": {"rows": [[1, "alice"]]}}
    result = await mcp_with_table_tools.call_tool("get_table_data", {"table_id": 1})
    mock_client.get_table_data.assert_awaited_once()
    data = json.loads(result.content[0].text)
    assert data["data"]["rows"][0] == [1, "alice"]
