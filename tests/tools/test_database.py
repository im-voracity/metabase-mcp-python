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
    result = await mcp_with_db_tools.call_tool(
        "execute_query",
        {
            "database_id": 1,
            "query": "SELECT 42",
        },
    )
    mock_client.execute_query.assert_awaited_once()
    data = json.loads(result.content[0].text)
    assert data["data"]["rows"][0][0] == 42


@pytest.mark.asyncio
async def test_get_database_metadata_tool(
    mcp_with_db_tools: FastMCP,
    mock_client: AsyncMock,
) -> None:
    mock_client.get_database_metadata.return_value = {"tables": []}
    result = await mcp_with_db_tools.call_tool(
        "get_database_metadata",
        {"database_id": 1},
    )
    mock_client.get_database_metadata.assert_awaited_once_with(1)
    data = json.loads(result.content[0].text)
    assert "tables" in data


@pytest.mark.asyncio
async def test_create_database_tool(mcp_with_db_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.create_database.return_value = {"id": 2, "name": "New DB"}
    result = await mcp_with_db_tools.call_tool(
        "create_database",
        {
            "engine": "postgres",
            "name": "New DB",
            "details": {"host": "localhost", "port": 5432},
        },
    )
    data = json.loads(result.content[0].text)
    assert data["name"] == "New DB"


@pytest.mark.asyncio
async def test_update_database_tool(mcp_with_db_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.update_database.return_value = {"id": 1, "name": "Renamed"}
    result = await mcp_with_db_tools.call_tool(
        "update_database",
        {
            "database_id": 1,
            "name": "Renamed",
        },
    )
    data = json.loads(result.content[0].text)
    assert data["name"] == "Renamed"


@pytest.mark.asyncio
async def test_delete_database_tool(mcp_with_db_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.delete_database.return_value = None
    result = await mcp_with_db_tools.call_tool("delete_database", {"database_id": 1})
    data = json.loads(result.content[0].text)
    assert data["action"] == "deleted"


@pytest.mark.asyncio
async def test_validate_database_tool(mcp_with_db_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.validate_database.return_value = {"valid": True}
    result = await mcp_with_db_tools.call_tool(
        "validate_database",
        {
            "engine": "postgres",
            "details": {"host": "localhost"},
        },
    )
    data = json.loads(result.content[0].text)
    assert data["valid"] is True


@pytest.mark.asyncio
async def test_add_sample_database_tool(mcp_with_db_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.add_sample_database.return_value = {"id": 99}
    result = await mcp_with_db_tools.call_tool("add_sample_database", {})
    data = json.loads(result.content[0].text)
    assert data["id"] == 99


@pytest.mark.asyncio
async def test_check_database_health_tool(
    mcp_with_db_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.check_database_health.return_value = {"status": "ok"}
    result = await mcp_with_db_tools.call_tool("check_database_health", {"database_id": 1})
    data = json.loads(result.content[0].text)
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_list_database_schemas_tool(
    mcp_with_db_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.get_database_schemas.return_value = ["public", "analytics"]
    result = await mcp_with_db_tools.call_tool("list_database_schemas", {"database_id": 1})
    data = json.loads(result.content[0].text)
    assert "public" in data


@pytest.mark.asyncio
async def test_get_database_schema_tool(mcp_with_db_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.get_database_schema.return_value = [{"name": "users"}]
    result = await mcp_with_db_tools.call_tool(
        "get_database_schema",
        {
            "database_id": 1,
            "schema_name": "public",
        },
    )
    data = json.loads(result.content[0].text)
    assert data[0]["name"] == "users"


@pytest.mark.asyncio
async def test_sync_database_schema_tool(
    mcp_with_db_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.sync_database_schema.return_value = None
    result = await mcp_with_db_tools.call_tool("sync_database_schema", {"database_id": 1})
    data = json.loads(result.content[0].text)
    assert data["action"] == "schema_sync_triggered"
