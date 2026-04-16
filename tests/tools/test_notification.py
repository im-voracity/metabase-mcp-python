"""Tests for notification tool registration and execution."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest
from fastmcp import FastMCP

from metabase_mcp.tools.notification import register_notification_tools


@pytest.fixture
def mcp_with_notif_tools(mcp: FastMCP, mock_client: AsyncMock) -> FastMCP:
    register_notification_tools(mcp, mock_client)
    return mcp


@pytest.mark.asyncio
async def test_list_notifications_tool(
    mcp_with_notif_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.get_notifications.return_value = [{"id": 1, "payload_type": "notification/card"}]
    result = await mcp_with_notif_tools.call_tool("list_notifications", {})
    mock_client.get_notifications.assert_awaited_once()
    data = json.loads(result.content[0].text)
    assert len(data) == 1


@pytest.mark.asyncio
async def test_get_notification_tool(
    mcp_with_notif_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.get_notification.return_value = {"id": 1, "payload_type": "notification/card"}
    result = await mcp_with_notif_tools.call_tool("get_notification", {"notification_id": 1})
    mock_client.get_notification.assert_awaited_once_with(1)
    data = json.loads(result.content[0].text)
    assert data["id"] == 1


@pytest.mark.asyncio
async def test_list_alerts_tool(
    mcp_with_notif_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.get_alerts.return_value = []
    result = await mcp_with_notif_tools.call_tool("list_alerts", {})
    mock_client.get_alerts.assert_awaited_once()
    data = json.loads(result.content[0].text)
    assert data == []


@pytest.mark.asyncio
async def test_get_alert_tool(
    mcp_with_notif_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.get_alert.return_value = {"id": 1, "card": {"id": 5}}
    result = await mcp_with_notif_tools.call_tool("get_alert", {"alert_id": 1})
    mock_client.get_alert.assert_awaited_once_with(1)
    data = json.loads(result.content[0].text)
    assert data["id"] == 1


@pytest.mark.asyncio
async def test_create_notification_tool(
    mcp_with_notif_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.create_notification.return_value = {"id": 10, "payload_type": "notification/card"}
    result = await mcp_with_notif_tools.call_tool(
        "create_notification",
        {
            "payload_type": "notification/card",
            "payload": {"card_id": 5},
            "handlers": [{"channel_type": "channel/email"}],
        },
    )
    mock_client.create_notification.assert_awaited_once()
    data = json.loads(result.content[0].text)
    assert data["id"] == 10


@pytest.mark.asyncio
async def test_update_notification_tool(
    mcp_with_notif_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.update_notification.return_value = {"id": 1, "active": False}
    result = await mcp_with_notif_tools.call_tool(
        "update_notification",
        {"notification_id": 1, "updates": {"active": False}},
    )
    mock_client.update_notification.assert_awaited_once_with(1, {"active": False})
    data = json.loads(result.content[0].text)
    assert data["active"] is False


@pytest.mark.asyncio
async def test_send_notification_tool(
    mcp_with_notif_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.send_notification.return_value = None
    result = await mcp_with_notif_tools.call_tool(
        "send_notification", {"notification_id": 1}
    )
    mock_client.send_notification.assert_awaited_once_with(1)
    data = json.loads(result.content[0].text)
    assert data["status"] == "success"


@pytest.mark.asyncio
async def test_unsubscribe_notification_tool(
    mcp_with_notif_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.unsubscribe_notification.return_value = None
    result = await mcp_with_notif_tools.call_tool(
        "unsubscribe_notification", {"notification_id": 1}
    )
    mock_client.unsubscribe_notification.assert_awaited_once_with(1)
    data = json.loads(result.content[0].text)
    assert data["status"] == "success"
