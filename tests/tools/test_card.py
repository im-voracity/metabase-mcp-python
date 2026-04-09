"""Tests for card tool registration and execution."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest
from fastmcp import FastMCP

from metabase_mcp.tools.card import register_card_tools


@pytest.fixture
def mcp_with_card_tools(mcp: FastMCP, mock_client: AsyncMock) -> FastMCP:
    register_card_tools(mcp, mock_client)
    return mcp


@pytest.mark.asyncio
async def test_list_cards_tool(mcp_with_card_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.get_cards.return_value = [{"id": 1, "name": "Q1"}]
    result = await mcp_with_card_tools.call_tool("list_cards", {})
    mock_client.get_cards.assert_awaited_once()
    data = json.loads(result.content[0].text)
    assert len(data) == 1


@pytest.mark.asyncio
async def test_get_card_tool(mcp_with_card_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.get_card.return_value = {"id": 5, "name": "Sales Q"}
    result = await mcp_with_card_tools.call_tool("get_card", {"card_id": 5})
    mock_client.get_card.assert_awaited_once_with(5)
    data = json.loads(result.content[0].text)
    assert data["name"] == "Sales Q"


@pytest.mark.asyncio
async def test_create_card_tool(mcp_with_card_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.create_card.return_value = {"id": 10, "name": "New Card"}
    result = await mcp_with_card_tools.call_tool(
        "create_card",
        {
            "name": "New Card",
            "dataset_query": {"type": "native", "native": {"query": "SELECT 1"}, "database": 1},
            "display": "table",
            "visualization_settings": {},
        },
    )
    mock_client.create_card.assert_awaited_once()
    data = json.loads(result.content[0].text)
    assert data["name"] == "New Card"


@pytest.mark.asyncio
async def test_create_card_with_json_string_params(
    mcp_with_card_tools: FastMCP,
    mock_client: AsyncMock,
) -> None:
    """Test that JSON string parameters are parsed correctly (parse_if_string)."""
    mock_client.create_card.return_value = {"id": 11, "name": "Card"}
    result = await mcp_with_card_tools.call_tool(
        "create_card",
        {
            "name": "Card",
            "dataset_query": '{"type": "native", "native": {"query": "SELECT 1"}, "database": 1}',
            "display": "table",
            "visualization_settings": "{}",
        },
    )
    mock_client.create_card.assert_awaited_once()
    data = json.loads(result.content[0].text)
    assert data["id"] == 11


@pytest.mark.asyncio
async def test_execute_card_tool(mcp_with_card_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.execute_card.return_value = {"data": {"rows": [[42]]}}
    result = await mcp_with_card_tools.call_tool("execute_card", {"card_id": 1})
    mock_client.execute_card.assert_awaited_once()
    data = json.loads(result.content[0].text)
    assert data["data"]["rows"][0][0] == 42


@pytest.mark.asyncio
async def test_update_card_tool(mcp_with_card_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.update_card.return_value = {"id": 5, "name": "Updated"}
    result = await mcp_with_card_tools.call_tool(
        "update_card",
        {
            "card_id": 5,
            "updates": {"name": "Updated"},
        },
    )
    data = json.loads(result.content[0].text)
    assert data["name"] == "Updated"


@pytest.mark.asyncio
async def test_delete_card_tool(mcp_with_card_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.delete_card.return_value = None
    result = await mcp_with_card_tools.call_tool("delete_card", {"card_id": 1})
    data = json.loads(result.content[0].text)
    assert data["action"] == "archived"
    assert data["status"] == "success"


@pytest.mark.asyncio
async def test_delete_card_hard_tool(mcp_with_card_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.delete_card.return_value = None
    result = await mcp_with_card_tools.call_tool("delete_card", {"card_id": 1, "hard_delete": True})
    data = json.loads(result.content[0].text)
    assert data["action"] == "deleted"


@pytest.mark.asyncio
async def test_copy_card_tool(mcp_with_card_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.copy_card.return_value = {"id": 11, "name": "Copy"}
    result = await mcp_with_card_tools.call_tool("copy_card", {"card_id": 5})
    data = json.loads(result.content[0].text)
    assert data["name"] == "Copy"


@pytest.mark.asyncio
async def test_export_card_result_tool(
    mcp_with_card_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.execute_card_query_with_format.return_value = {"data": "csv content"}
    result = await mcp_with_card_tools.call_tool(
        "export_card_result",
        {
            "card_id": 1,
            "export_format": "csv",
        },
    )
    data = json.loads(result.content[0].text)
    assert data["data"] == "csv content"


@pytest.mark.asyncio
async def test_get_card_dashboards_tool(
    mcp_with_card_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.get_card_dashboards.return_value = [{"id": 1}]
    result = await mcp_with_card_tools.call_tool("get_card_dashboards", {"card_id": 5})
    data = json.loads(result.content[0].text)
    assert len(data) == 1


@pytest.mark.asyncio
async def test_list_embeddable_cards_tool(
    mcp_with_card_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.get_embeddable_cards.return_value = []
    result = await mcp_with_card_tools.call_tool("list_embeddable_cards", {})
    data = json.loads(result.content[0].text)
    assert data == []


@pytest.mark.asyncio
async def test_list_public_cards_tool(mcp_with_card_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.get_public_cards.return_value = []
    result = await mcp_with_card_tools.call_tool("list_public_cards", {})
    data = json.loads(result.content[0].text)
    assert data == []


@pytest.mark.asyncio
async def test_create_card_public_link_tool(
    mcp_with_card_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.create_card_public_link.return_value = {"uuid": "abc"}
    result = await mcp_with_card_tools.call_tool("create_card_public_link", {"card_id": 1})
    data = json.loads(result.content[0].text)
    assert data["uuid"] == "abc"


@pytest.mark.asyncio
async def test_delete_card_public_link_tool(
    mcp_with_card_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.delete_card_public_link.return_value = {"success": True}
    result = await mcp_with_card_tools.call_tool("delete_card_public_link", {"card_id": 1})
    data = json.loads(result.content[0].text)
    assert data["success"] is True


@pytest.mark.asyncio
async def test_move_cards_tool(mcp_with_card_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.move_cards.return_value = {"status": "ok"}
    result = await mcp_with_card_tools.call_tool(
        "move_cards",
        {
            "card_ids": [1, 2],
            "collection_id": 5,
        },
    )
    data = json.loads(result.content[0].text)
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_move_cards_to_collection_tool(
    mcp_with_card_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.move_cards_to_collection.return_value = {"status": "ok"}
    result = await mcp_with_card_tools.call_tool(
        "move_cards_to_collection",
        {
            "card_ids": [1],
            "collection_id": 3,
        },
    )
    data = json.loads(result.content[0].text)
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_execute_pivot_card_query_tool(
    mcp_with_card_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.execute_pivot_card_query.return_value = {"data": {"rows": []}}
    result = await mcp_with_card_tools.call_tool("execute_pivot_card_query", {"card_id": 1})
    data = json.loads(result.content[0].text)
    assert "data" in data


@pytest.mark.asyncio
async def test_get_card_param_values_tool(
    mcp_with_card_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.get_card_param_values.return_value = {"values": [["A"], ["B"]]}
    result = await mcp_with_card_tools.call_tool(
        "get_card_param_values",
        {
            "card_id": 1,
            "param_key": "category",
        },
    )
    data = json.loads(result.content[0].text)
    assert len(data["values"]) == 2


@pytest.mark.asyncio
async def test_search_card_param_values_tool(
    mcp_with_card_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.search_card_param_values.return_value = {"values": [["foo"]]}
    result = await mcp_with_card_tools.call_tool(
        "search_card_param_values",
        {
            "card_id": 1,
            "param_key": "name",
            "query": "foo",
        },
    )
    data = json.loads(result.content[0].text)
    assert data["values"] == [["foo"]]


@pytest.mark.asyncio
async def test_get_card_param_remapping_tool(
    mcp_with_card_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.get_card_param_remapping.return_value = {"remapped": "display_val"}
    result = await mcp_with_card_tools.call_tool(
        "get_card_param_remapping",
        {
            "card_id": 1,
            "param_key": "id",
            "value": "42",
        },
    )
    data = json.loads(result.content[0].text)
    assert data["remapped"] == "display_val"


@pytest.mark.asyncio
async def test_get_card_query_metadata_tool(
    mcp_with_card_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.get_card_query_metadata.return_value = {"columns": []}
    result = await mcp_with_card_tools.call_tool("get_card_query_metadata", {"card_id": 1})
    data = json.loads(result.content[0].text)
    assert "columns" in data


@pytest.mark.asyncio
async def test_get_card_series_tool(mcp_with_card_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.get_card_series.return_value = [{"id": 2}]
    result = await mcp_with_card_tools.call_tool("get_card_series", {"card_id": 1})
    data = json.loads(result.content[0].text)
    assert len(data) == 1
