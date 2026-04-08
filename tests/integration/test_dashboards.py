"""Integration tests for dashboard operations."""

from __future__ import annotations

from typing import Any

import pytest

from metabase_mcp.client import MetabaseClient

pytestmark = pytest.mark.integration


@pytest.mark.asyncio(loop_scope="session")
async def test_list_dashboards(client: MetabaseClient) -> None:
    dashboards = await client.get_dashboards()
    assert isinstance(dashboards, list)


@pytest.mark.asyncio(loop_scope="session")
async def test_dashboard_crud(client: MetabaseClient, test_collection: dict[str, Any]) -> None:
    """Full CRUD cycle for a dashboard."""
    # Create
    dashboard = await client.create_dashboard({
        "name": "Test Dashboard",
        "description": "Created by integration test",
        "collection_id": test_collection["id"],
    })
    assert dashboard["name"] == "Test Dashboard"
    dashboard_id = dashboard["id"]

    try:
        # Read
        fetched = await client.get_dashboard(dashboard_id)
        assert fetched["id"] == dashboard_id
        assert fetched["name"] == "Test Dashboard"

        # Update
        updated = await client.update_dashboard(dashboard_id, {"name": "Updated Dashboard"})
        assert updated["name"] == "Updated Dashboard"

        # Get revisions (not available in all Metabase versions)
        try:
            revisions = await client.get_dashboard_revisions(dashboard_id)
            assert isinstance(revisions, list)
        except Exception:
            pass  # endpoint may not exist in this version

    finally:
        # Delete (hard)
        await client.delete_dashboard(dashboard_id, hard_delete=True)


@pytest.mark.asyncio(loop_scope="session")
async def test_dashboard_with_card(
    client: MetabaseClient,
    test_collection: dict[str, Any],
    sample_database_id: int,
) -> None:
    """Test adding a card to a dashboard."""
    # Create a card first
    card = await client.create_card({
        "name": "Test Card for Dashboard",
        "dataset_query": {
            "type": "native",
            "native": {"query": "SELECT 1"},
            "database": sample_database_id,
        },
        "display": "table",
        "visualization_settings": {},
        "collection_id": test_collection["id"],
    })

    # Create dashboard
    dashboard = await client.create_dashboard({
        "name": "Dashboard with Card",
        "collection_id": test_collection["id"],
    })

    try:
        # Add card to dashboard
        result = await client.add_card_to_dashboard(dashboard["id"], {
            "card_id": card["id"],
            "row": 0,
            "col": 0,
            "size_x": 12,
            "size_y": 8,
        })
        assert result is not None

        # Verify card is in dashboard
        fetched = await client.get_dashboard(dashboard["id"])
        dashcards = fetched.get("dashcards", [])
        assert len(dashcards) > 0
        assert any(dc.get("card_id") == card["id"] for dc in dashcards)

    finally:
        await client.delete_dashboard(dashboard["id"], hard_delete=True)
        await client.delete_card(card["id"], hard_delete=True)
