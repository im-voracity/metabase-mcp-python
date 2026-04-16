"""MCP tools for Metabase notification and alert operations."""

from __future__ import annotations

import json
from typing import Annotated, Any

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import BeforeValidator, Field

from metabase_mcp.client import MetabaseClient
from metabase_mcp.validators import parse_if_string


def register_notification_tools(mcp: FastMCP, client: MetabaseClient) -> None:
    """Register all notification and alert-related MCP tools."""

    # ── Read tools ──────────────────────────────────────────────────────

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def list_notifications() -> str:
        """List all notifications - use this to see configured alerts and subscriptions"""
        result = await client.get_notifications()
        return json.dumps(result, indent=2)

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def get_notification(
        notification_id: Annotated[int, Field(description="The ID of the notification")],
    ) -> str:
        """Get detailed information about a specific notification including handlers and subscriptions"""
        result = await client.get_notification(notification_id)
        return json.dumps(result, indent=2)

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def list_alerts() -> str:
        """List all legacy alerts - use this to see configured card-based alerts (being replaced by notifications)"""
        result = await client.get_alerts()
        return json.dumps(result, indent=2)

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def get_alert(
        alert_id: Annotated[int, Field(description="The ID of the alert")],
    ) -> str:
        """Get detailed information about a specific legacy alert"""
        result = await client.get_alert(alert_id)
        return json.dumps(result, indent=2)

    # ── Write tools ─────────────────────────────────────────────────────

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False),
    )
    async def create_notification(
        payload_type: Annotated[
            str,
            Field(description="Notification type (e.g. 'notification/card')"),
        ],
        payload: Annotated[
            dict[str, Any],
            BeforeValidator(parse_if_string),
            Field(description="Notification payload as JSON (varies by type)"),
        ],
        handlers: Annotated[
            list[dict[str, Any]],
            BeforeValidator(parse_if_string),
            Field(description="Notification handlers (channels and templates) as JSON"),
        ],
        subscriptions: Annotated[
            list[dict[str, Any]] | None,
            BeforeValidator(parse_if_string),
            Field(description="Subscriptions list as JSON"),
        ] = None,
    ) -> str:
        """Create a new notification - use this to set up automated alerts on cards or dashboards"""
        notification_data: dict[str, Any] = {
            "payload_type": payload_type,
            "payload": payload,
            "handlers": handlers,
        }
        if subscriptions is not None:
            notification_data["subscriptions"] = subscriptions
        result = await client.create_notification(notification_data)
        return json.dumps(result, indent=2)

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False),
    )
    async def update_notification(
        notification_id: Annotated[int, Field(description="The ID of the notification to update")],
        updates: Annotated[
            dict[str, Any],
            BeforeValidator(parse_if_string),
            Field(description="Updates to apply as JSON (e.g. active, handlers, subscriptions)"),
        ],
    ) -> str:
        """Update a notification's settings - use this to modify handlers, subscriptions, or activate/deactivate"""
        result = await client.update_notification(notification_id, updates)
        return json.dumps(result, indent=2)

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False),
    )
    async def send_notification(
        notification_id: Annotated[int, Field(description="The ID of the notification to send")],
    ) -> str:
        """Manually trigger a notification to send now - use this to test or force-send a notification"""
        result = await client.send_notification(notification_id)
        return json.dumps(
            result if result else {"notification_id": notification_id, "action": "sent", "status": "success"},
            indent=2,
        )

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False),
    )
    async def unsubscribe_notification(
        notification_id: Annotated[int, Field(description="The ID of the notification to unsubscribe from")],
    ) -> str:
        """Unsubscribe the current user from a notification"""
        result = await client.unsubscribe_notification(notification_id)
        return json.dumps(
            result if result else {"notification_id": notification_id, "action": "unsubscribed", "status": "success"},
            indent=2,
        )
