"""Integration tests for collection operations."""

from __future__ import annotations

from typing import Any

import pytest

from metabase_mcp.client import MetabaseClient

pytestmark = pytest.mark.integration


@pytest.mark.asyncio(loop_scope="session")
async def test_list_collections(client: MetabaseClient) -> None:
    collections = await client.get_collections()
    assert isinstance(collections, list)
    assert len(collections) > 0


@pytest.mark.asyncio(loop_scope="session")
async def test_create_and_get_collection(
    client: MetabaseClient,
    test_collection: dict[str, Any],
) -> None:
    """Verify the test collection was created and can be retrieved."""
    coll = await client.get_collection(test_collection["id"])
    assert coll["id"] == test_collection["id"]
    assert "__metabase_mcp_test__" in coll["name"]


@pytest.mark.asyncio(loop_scope="session")
async def test_update_collection(client: MetabaseClient, test_collection: dict[str, Any]) -> None:
    updated = await client.update_collection(
        test_collection["id"],
        {"description": "Updated by integration test"},
    )
    assert updated["description"] == "Updated by integration test"


@pytest.mark.asyncio(loop_scope="session")
async def test_get_collection_items(
    client: MetabaseClient,
    test_collection: dict[str, Any],
) -> None:
    items = await client.api_call("GET", f"/api/collection/{test_collection['id']}/items")
    assert items is not None
