"""Integration tests for notification and alert operations."""

from __future__ import annotations

import pytest

from metabase_mcp.client import MetabaseClient

pytestmark = pytest.mark.integration


@pytest.mark.asyncio(loop_scope="session")
async def test_list_notifications(client: MetabaseClient) -> None:
    notifications = await client.get_notifications()
    assert isinstance(notifications, list)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_notification(client: MetabaseClient) -> None:
    notifications = await client.get_notifications()
    if not notifications:
        pytest.skip("No notifications available")
    notif = await client.get_notification(notifications[0]["id"])
    assert "id" in notif
    assert "payload_type" in notif


@pytest.mark.asyncio(loop_scope="session")
async def test_list_alerts(client: MetabaseClient) -> None:
    alerts = await client.get_alerts()
    assert isinstance(alerts, list)
