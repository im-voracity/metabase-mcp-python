"""Tests for dashboard tool registration and execution."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest
from fastmcp import FastMCP

from metabase_mcp.tools.dashboard import register_dashboard_tools


@pytest.fixture
def mcp_with_dash_tools(mcp: FastMCP, mock_client: AsyncMock) -> FastMCP:
    register_dashboard_tools(mcp, mock_client)
    return mcp


@pytest.mark.asyncio
async def test_list_dashboards_tool(mcp_with_dash_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.get_dashboards.return_value = [{"id": 1, "name": "Sales"}]
    result = await mcp_with_dash_tools.call_tool("list_dashboards", {})
    mock_client.get_dashboards.assert_awaited_once()
    data = json.loads(result.content[0].text)
    assert data[0]["name"] == "Sales"


@pytest.mark.asyncio
async def test_get_dashboard_tool(mcp_with_dash_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.get_dashboard.return_value = {"id": 1, "name": "Sales", "dashcards": []}
    result = await mcp_with_dash_tools.call_tool("get_dashboard", {"dashboard_id": 1})
    mock_client.get_dashboard.assert_awaited_once_with(1)
    data = json.loads(result.content[0].text)
    assert data["name"] == "Sales"


@pytest.mark.asyncio
async def test_create_dashboard_tool(mcp_with_dash_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.create_dashboard.return_value = {"id": 2, "name": "New Dash"}
    result = await mcp_with_dash_tools.call_tool("create_dashboard", {
        "name": "New Dash",
    })
    mock_client.create_dashboard.assert_awaited_once()
    data = json.loads(result.content[0].text)
    assert data["name"] == "New Dash"


@pytest.mark.asyncio
async def test_update_dashboard_tool(mcp_with_dash_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.update_dashboard.return_value = {"id": 1, "name": "Updated"}
    result = await mcp_with_dash_tools.call_tool("update_dashboard", {
        "dashboard_id": 1,
        "name": "Updated",
    })
    mock_client.update_dashboard.assert_awaited_once()
    data = json.loads(result.content[0].text)
    assert data["name"] == "Updated"


@pytest.mark.asyncio
async def test_delete_dashboard_tool(mcp_with_dash_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.delete_dashboard.return_value = None
    await mcp_with_dash_tools.call_tool("delete_dashboard", {
        "dashboard_id": 1,
    })
    mock_client.delete_dashboard.assert_awaited_once()
