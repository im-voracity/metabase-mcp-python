"""Integration tests for card (saved question) operations."""

from __future__ import annotations

from typing import Any

import pytest

from metabase_mcp.client import MetabaseClient

pytestmark = pytest.mark.integration


@pytest.mark.asyncio(loop_scope="session")
async def test_list_cards(client: MetabaseClient) -> None:
    cards = await client.get_cards()
    assert isinstance(cards, list)


@pytest.mark.asyncio(loop_scope="session")
async def test_card_crud(
    client: MetabaseClient,
    test_collection: dict[str, Any],
    sample_database_id: int,
) -> None:
    """Full CRUD cycle for a card."""
    # Create
    card = await client.create_card(
        {
            "name": "Test Card",
            "description": "Created by integration test",
            "dataset_query": {
                "type": "native",
                "native": {"query": "SELECT 1 AS test_val"},
                "database": sample_database_id,
            },
            "display": "table",
            "visualization_settings": {},
            "collection_id": test_collection["id"],
        }
    )
    assert card["name"] == "Test Card"
    card_id = card["id"]

    try:
        # Read
        fetched = await client.get_card(card_id)
        assert fetched["id"] == card_id

        # Update
        updated = await client.update_card(card_id, {"name": "Updated Card"})
        assert updated["name"] == "Updated Card"

        # Execute
        result = await client.execute_card(card_id)
        assert result is not None
        assert "data" in result

    finally:
        # Delete (hard)
        await client.delete_card(card_id, hard_delete=True)


@pytest.mark.asyncio(loop_scope="session")
async def test_execute_card_query(
    client: MetabaseClient,
    test_collection: dict[str, Any],
    sample_database_id: int,
) -> None:
    """Test executing a card's query."""
    card = await client.create_card(
        {
            "name": "Query Test Card",
            "dataset_query": {
                "type": "native",
                "native": {"query": "SELECT 42 AS answer"},
                "database": sample_database_id,
            },
            "display": "table",
            "visualization_settings": {},
            "collection_id": test_collection["id"],
        }
    )

    try:
        result = await client.execute_card(card["id"])
        rows = result["data"]["rows"]
        assert rows[0][0] == 42
    finally:
        await client.delete_card(card["id"], hard_delete=True)
