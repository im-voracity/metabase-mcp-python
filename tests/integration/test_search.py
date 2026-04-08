"""Integration tests for search operations."""

from __future__ import annotations

import pytest

from metabase_mcp.client import MetabaseClient

pytestmark = pytest.mark.integration


@pytest.mark.asyncio(loop_scope="session")
async def test_search_content(client: MetabaseClient) -> None:
    """Test searching across Metabase content."""
    result = await client.api_call("GET", "/api/search", data=None)
    # search without params returns all items
    assert result is not None


@pytest.mark.asyncio(loop_scope="session")
async def test_search_with_query(client: MetabaseClient) -> None:
    """Test searching with a specific query string."""
    params = "?q=Sample"
    result = await client.api_call("GET", f"/api/search{params}")
    assert result is not None
