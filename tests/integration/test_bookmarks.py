"""Integration tests for bookmark operations."""

from __future__ import annotations

import pytest

from metabase_mcp.client import MetabaseClient

pytestmark = pytest.mark.integration


@pytest.mark.asyncio(loop_scope="session")
async def test_list_bookmarks(client: MetabaseClient) -> None:
    bookmarks = await client.get_bookmarks()
    assert isinstance(bookmarks, list)


@pytest.mark.asyncio(loop_scope="session")
async def test_bookmark_crud_cycle(client: MetabaseClient) -> None:
    """Create, verify, and delete a bookmark on the Sample Database dashboard."""
    # Use dashboard ID 1 (auto-generated Sample Database dashboard)
    bookmarks_before = await client.get_bookmarks()

    # Create bookmark
    result = await client.create_bookmark("dashboard", 1)
    assert "id" in result

    # Verify it appears in the list
    bookmarks_after = await client.get_bookmarks()
    assert len(bookmarks_after) > len(bookmarks_before)

    # Delete bookmark
    await client.delete_bookmark("dashboard", 1)

    # Verify it was removed
    bookmarks_final = await client.get_bookmarks()
    assert len(bookmarks_final) == len(bookmarks_before)
