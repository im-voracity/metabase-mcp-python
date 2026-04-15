"""Integration tests for field operations."""

from __future__ import annotations

import pytest

from metabase_mcp.client import MetabaseClient

pytestmark = pytest.mark.integration


@pytest.mark.asyncio(loop_scope="session")
async def test_get_field(client: MetabaseClient) -> None:
    field = await client.get_field(1)
    assert "id" in field
    assert "name" in field
    assert "base_type" in field


@pytest.mark.asyncio(loop_scope="session")
async def test_get_field_values(client: MetabaseClient) -> None:
    values = await client.get_field_values(1)
    assert "values" in values
    assert "has_more_values" in values


@pytest.mark.asyncio(loop_scope="session")
async def test_get_field_summary(client: MetabaseClient) -> None:
    summary = await client.get_field_summary(1)
    assert isinstance(summary, list)
    assert len(summary) >= 1


@pytest.mark.asyncio(loop_scope="session")
async def test_update_field_roundtrip(client: MetabaseClient) -> None:
    """Update a field's description and restore it."""
    original = await client.get_field(1)
    original_desc = original.get("description")

    updated = await client.update_field(1, {"description": "Integration test"})
    assert updated["description"] == "Integration test"

    # Restore
    await client.update_field(1, {"description": original_desc})
