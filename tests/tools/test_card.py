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
    result = await mcp_with_card_tools.call_tool("create_card", {
        "name": "New Card",
        "dataset_query": {"type": "native", "native": {"query": "SELECT 1"}, "database": 1},
        "display": "table",
        "visualization_settings": {},
    })
    mock_client.create_card.assert_awaited_once()
    data = json.loads(result.content[0].text)
    assert data["name"] == "New Card"


@pytest.mark.asyncio
async def test_create_card_with_json_string_params(
    mcp_with_card_tools: FastMCP, mock_client: AsyncMock,
) -> None:
    """Test that JSON string parameters are parsed correctly (parse_if_string)."""
    mock_client.create_card.return_value = {"id": 11, "name": "Card"}
    result = await mcp_with_card_tools.call_tool("create_card", {
        "name": "Card",
        "dataset_query": '{"type": "native", "native": {"query": "SELECT 1"}, "database": 1}',
        "display": "table",
        "visualization_settings": "{}",
    })
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
