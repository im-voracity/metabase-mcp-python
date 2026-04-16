"""Tests for action tool registration and execution."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest
from fastmcp import FastMCP

from metabase_mcp.tools.action import register_action_tools


@pytest.fixture
def mcp_with_action_tools(mcp: FastMCP, mock_client: AsyncMock) -> FastMCP:
    register_action_tools(mcp, mock_client)
    return mcp


@pytest.mark.asyncio
async def test_list_actions_tool(
    mcp_with_action_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.get_actions.return_value = [{"id": 1, "name": "Insert Order", "type": "query"}]
    result = await mcp_with_action_tools.call_tool("list_actions", {})
    mock_client.get_actions.assert_awaited_once()
    data = json.loads(result.content[0].text)
    assert len(data) == 1
    assert data[0]["name"] == "Insert Order"


@pytest.mark.asyncio
async def test_get_action_tool(
    mcp_with_action_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.get_action.return_value = {"id": 1, "name": "Insert Order", "type": "query"}
    result = await mcp_with_action_tools.call_tool("get_action", {"action_id": 1})
    mock_client.get_action.assert_awaited_once_with(1)
    data = json.loads(result.content[0].text)
    assert data["name"] == "Insert Order"


@pytest.mark.asyncio
async def test_create_action_tool(
    mcp_with_action_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.create_action.return_value = {"id": 1, "name": "New Action", "type": "query"}
    result = await mcp_with_action_tools.call_tool(
        "create_action",
        {"name": "New Action", "model_id": 2, "type": "query", "database_id": 1},
    )
    mock_client.create_action.assert_awaited_once()
    call_args = mock_client.create_action.call_args[0][0]
    assert call_args["name"] == "New Action"
    assert call_args["model_id"] == 2
    assert call_args["database_id"] == 1
    data = json.loads(result.content[0].text)
    assert data["id"] == 1


@pytest.mark.asyncio
async def test_update_action_tool(
    mcp_with_action_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.update_action.return_value = {"id": 1, "name": "Updated"}
    result = await mcp_with_action_tools.call_tool(
        "update_action", {"action_id": 1, "name": "Updated"}
    )
    mock_client.update_action.assert_awaited_once_with(1, {"name": "Updated"})
    data = json.loads(result.content[0].text)
    assert data["name"] == "Updated"


@pytest.mark.asyncio
async def test_delete_action_tool(
    mcp_with_action_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.delete_action.return_value = None
    result = await mcp_with_action_tools.call_tool("delete_action", {"action_id": 1})
    mock_client.delete_action.assert_awaited_once_with(1)
    data = json.loads(result.content[0].text)
    assert data["status"] == "success"


@pytest.mark.asyncio
async def test_execute_action_tool(
    mcp_with_action_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.execute_action.return_value = {"rows_affected": 1}
    result = await mcp_with_action_tools.call_tool(
        "execute_action", {"action_id": 1, "parameters": {"name": "test"}}
    )
    mock_client.execute_action.assert_awaited_once_with(1, {"name": "test"})
    data = json.loads(result.content[0].text)
    assert data["rows_affected"] == 1
