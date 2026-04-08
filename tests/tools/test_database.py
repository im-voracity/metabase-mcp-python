"""Tests for database tool registration and execution."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest
from fastmcp import FastMCP

from metabase_mcp.tools.database import register_database_tools


@pytest.fixture
def mcp_with_db_tools(mcp: FastMCP, mock_client: AsyncMock) -> FastMCP:
    register_database_tools(mcp, mock_client)
    return mcp


@pytest.mark.asyncio
async def test_list_databases_tool(mcp_with_db_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.get_databases.return_value = [{"id": 1, "name": "DB"}]
    result = await mcp_with_db_tools.call_tool("list_databases", {})
    mock_client.get_databases.assert_awaited_once()
    data = json.loads(result.content[0].text)
    assert data == [{"id": 1, "name": "DB"}]


@pytest.mark.asyncio
async def test_get_database_tool(mcp_with_db_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.get_database.return_value = {"id": 1, "name": "PG"}
    result = await mcp_with_db_tools.call_tool("get_database", {"database_id": 1})
    mock_client.get_database.assert_awaited_once_with(1)
    data = json.loads(result.content[0].text)
    assert data["name"] == "PG"


@pytest.mark.asyncio
async def test_execute_query_tool(mcp_with_db_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.execute_query.return_value = {"data": {"rows": [[42]]}}
    result = await mcp_with_db_tools.call_tool("execute_query", {
        "database_id": 1,
        "query": "SELECT 42",
    })
    mock_client.execute_query.assert_awaited_once()
    data = json.loads(result.content[0].text)
    assert data["data"]["rows"][0][0] == 42


@pytest.mark.asyncio
async def test_get_database_metadata_tool(
    mcp_with_db_tools: FastMCP, mock_client: AsyncMock,
) -> None:
    mock_client.get_database_metadata.return_value = {"tables": []}
    result = await mcp_with_db_tools.call_tool(
        "get_database_metadata", {"database_id": 1},
    )
    mock_client.get_database_metadata.assert_awaited_once_with(1)
    data = json.loads(result.content[0].text)
    assert "tables" in data
