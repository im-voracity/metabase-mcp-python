"""Tests for field tool registration and execution."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest
from fastmcp import FastMCP

from metabase_mcp.tools.field import register_field_tools


@pytest.fixture
def mcp_with_field_tools(mcp: FastMCP, mock_client: AsyncMock) -> FastMCP:
    register_field_tools(mcp, mock_client)
    return mcp


# ── Read tools ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_field_tool(
    mcp_with_field_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.get_field.return_value = {
        "id": 1,
        "name": "CATEGORY",
        "display_name": "Category",
        "base_type": "type/Text",
    }
    result = await mcp_with_field_tools.call_tool("get_field", {"field_id": 1})
    mock_client.get_field.assert_awaited_once_with(1)
    data = json.loads(result.content[0].text)
    assert data["name"] == "CATEGORY"


@pytest.mark.asyncio
async def test_get_field_values_tool(
    mcp_with_field_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.get_field_values.return_value = {
        "field_id": 1,
        "values": [["Gadget"], ["Widget"]],
        "has_more_values": False,
    }
    result = await mcp_with_field_tools.call_tool("get_field_values", {"field_id": 1})
    mock_client.get_field_values.assert_awaited_once_with(1)
    data = json.loads(result.content[0].text)
    assert len(data["values"]) == 2


@pytest.mark.asyncio
async def test_get_field_summary_tool(
    mcp_with_field_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.get_field_summary.return_value = [["count", 2495], ["distincts", 102]]
    result = await mcp_with_field_tools.call_tool("get_field_summary", {"field_id": 1})
    mock_client.get_field_summary.assert_awaited_once_with(1)
    data = json.loads(result.content[0].text)
    assert data[0] == ["count", 2495]


@pytest.mark.asyncio
async def test_search_field_values_tool(
    mcp_with_field_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.search_field_values.return_value = [["Gadget", 1], ["Gizmo", 2]]
    result = await mcp_with_field_tools.call_tool(
        "search_field_values", {"field_id": 1, "search_field_id": 2}
    )
    mock_client.search_field_values.assert_awaited_once_with(1, 2)
    data = json.loads(result.content[0].text)
    assert len(data) == 2


# ── Write tools ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_field_tool(
    mcp_with_field_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.update_field.return_value = {
        "id": 1,
        "display_name": "New Name",
        "description": "New desc",
    }
    result = await mcp_with_field_tools.call_tool(
        "update_field",
        {"field_id": 1, "display_name": "New Name", "description": "New desc"},
    )
    mock_client.update_field.assert_awaited_once_with(
        1, {"display_name": "New Name", "description": "New desc"}
    )
    data = json.loads(result.content[0].text)
    assert data["display_name"] == "New Name"


@pytest.mark.asyncio
async def test_rescan_field_values_tool(
    mcp_with_field_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.rescan_field_values.return_value = None
    result = await mcp_with_field_tools.call_tool(
        "rescan_field_values", {"field_id": 1}
    )
    mock_client.rescan_field_values.assert_awaited_once_with(1)
    data = json.loads(result.content[0].text)
    assert data["status"] == "success"
    assert data["action"] == "rescan_triggered"


@pytest.mark.asyncio
async def test_discard_field_values_tool(
    mcp_with_field_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.discard_field_values.return_value = None
    result = await mcp_with_field_tools.call_tool(
        "discard_field_values", {"field_id": 1}
    )
    mock_client.discard_field_values.assert_awaited_once_with(1)
    data = json.loads(result.content[0].text)
    assert data["status"] == "success"
    assert data["action"] == "values_discarded"
