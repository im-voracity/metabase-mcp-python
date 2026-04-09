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
    mcp_with_table_tools: FastMCP,
    mock_client: AsyncMock,
) -> None:
    mock_client.get_table_query_metadata.return_value = {"id": 1, "fields": []}
    result = await mcp_with_table_tools.call_tool(
        "get_table_query_metadata",
        {"table_id": 1},
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


@pytest.mark.asyncio
async def test_get_table_tool(mcp_with_table_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.get_table.return_value = {"id": 1, "name": "users"}
    result = await mcp_with_table_tools.call_tool("get_table", {"table_id": 1})
    data = json.loads(result.content[0].text)
    assert data["name"] == "users"


@pytest.mark.asyncio
async def test_update_table_tool(mcp_with_table_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.update_table.return_value = {"id": 1, "display_name": "Users"}
    result = await mcp_with_table_tools.call_tool(
        "update_table",
        {
            "table_id": 1,
            "display_name": "Users",
        },
    )
    data = json.loads(result.content[0].text)
    assert data["display_name"] == "Users"


@pytest.mark.asyncio
async def test_update_tables_tool(mcp_with_table_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.update_tables.return_value = {"status": "ok"}
    result = await mcp_with_table_tools.call_tool(
        "update_tables",
        {
            "ids": [1, 2],
            "description": "Updated",
        },
    )
    data = json.loads(result.content[0].text)
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_get_table_fks_tool(mcp_with_table_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.get_table_fks.return_value = [{"id": 1}]
    result = await mcp_with_table_tools.call_tool("get_table_fks", {"table_id": 1})
    data = json.loads(result.content[0].text)
    assert len(data) == 1


@pytest.mark.asyncio
async def test_get_table_related_tool(
    mcp_with_table_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.get_table_related.return_value = {"related": []}
    result = await mcp_with_table_tools.call_tool("get_table_related", {"table_id": 1})
    data = json.loads(result.content[0].text)
    assert "related" in data


@pytest.mark.asyncio
async def test_get_card_table_fks_tool(
    mcp_with_table_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.get_card_table_fks.return_value = []
    result = await mcp_with_table_tools.call_tool("get_card_table_fks", {"card_id": 1})
    data = json.loads(result.content[0].text)
    assert data == []


@pytest.mark.asyncio
async def test_get_card_table_query_metadata_tool(
    mcp_with_table_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.get_card_table_query_metadata.return_value = {"fields": []}
    result = await mcp_with_table_tools.call_tool("get_card_table_query_metadata", {"card_id": 1})
    data = json.loads(result.content[0].text)
    assert "fields" in data


@pytest.mark.asyncio
async def test_append_csv_to_table_tool(
    mcp_with_table_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.append_csv_to_table.return_value = {"status": "ok"}
    result = await mcp_with_table_tools.call_tool(
        "append_csv_to_table",
        {
            "table_id": 1,
            "filename": "data.csv",
            "file_content": "a,b\n1,2",
        },
    )
    data = json.loads(result.content[0].text)
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_replace_table_csv_tool(
    mcp_with_table_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.replace_table_csv.return_value = {"status": "ok"}
    result = await mcp_with_table_tools.call_tool(
        "replace_table_csv",
        {
            "table_id": 1,
            "csv_file": "a,b\n1,2",
        },
    )
    data = json.loads(result.content[0].text)
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_discard_table_field_values_tool(
    mcp_with_table_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.discard_table_field_values.return_value = {"status": "ok"}
    result = await mcp_with_table_tools.call_tool("discard_table_field_values", {"table_id": 1})
    data = json.loads(result.content[0].text)
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_reorder_table_fields_tool(
    mcp_with_table_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.reorder_table_fields.return_value = {"status": "ok"}
    result = await mcp_with_table_tools.call_tool(
        "reorder_table_fields",
        {
            "table_id": 1,
            "field_order": [3, 1, 2],
        },
    )
    data = json.loads(result.content[0].text)
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_rescan_table_field_values_tool(
    mcp_with_table_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.rescan_table_field_values.return_value = {"status": "ok"}
    result = await mcp_with_table_tools.call_tool("rescan_table_field_values", {"table_id": 1})
    data = json.loads(result.content[0].text)
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_sync_table_schema_tool(
    mcp_with_table_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.sync_table_schema.return_value = None
    result = await mcp_with_table_tools.call_tool("sync_table_schema", {"table_id": 1})
    data = json.loads(result.content[0].text)
    assert data["status"] == "schema_sync_triggered"


@pytest.mark.asyncio
async def test_get_field_id_tool(mcp_with_table_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.get_field_by_name.return_value = {"field_id": 10, "name": "email"}
    result = await mcp_with_table_tools.call_tool(
        "get_field_id",
        {
            "table_id": 1,
            "column_name": "email",
        },
    )
    data = json.loads(result.content[0].text)
    assert data["field_id"] == 10
