"""Integration tests for action operations."""

from __future__ import annotations

import pytest

from metabase_mcp.client import MetabaseClient

pytestmark = pytest.mark.integration


@pytest.mark.asyncio(loop_scope="session")
async def test_list_actions(client: MetabaseClient) -> None:
    """List actions endpoint is accessible (may return empty if actions not enabled)."""
    actions = await client.get_actions()
    assert isinstance(actions, list)
