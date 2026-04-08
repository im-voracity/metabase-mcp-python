"""Integration tests for database operations."""

from __future__ import annotations

import pytest

from metabase_mcp.client import MetabaseClient

pytestmark = pytest.mark.integration


@pytest.mark.asyncio(loop_scope="session")
async def test_list_databases(client: MetabaseClient) -> None:
    dbs = await client.get_databases()
    db_list = dbs.get("data", dbs) if isinstance(dbs, dict) else dbs
    assert isinstance(db_list, list)
    assert len(db_list) > 0


@pytest.mark.asyncio(loop_scope="session")
async def test_get_database(client: MetabaseClient, sample_database_id: int) -> None:
    db = await client.get_database(sample_database_id)
    assert db["id"] == sample_database_id
    assert db["name"] == "Sample Database"


@pytest.mark.asyncio(loop_scope="session")
async def test_get_database_metadata(client: MetabaseClient, sample_database_id: int) -> None:
    metadata = await client.get_database_metadata(sample_database_id)
    assert metadata is not None
    assert "tables" in metadata


@pytest.mark.asyncio(loop_scope="session")
async def test_list_database_schemas(client: MetabaseClient, sample_database_id: int) -> None:
    schemas = await client.get_database_schemas(sample_database_id)
    assert isinstance(schemas, list)


@pytest.mark.asyncio(loop_scope="session")
async def test_execute_query(client: MetabaseClient, sample_database_id: int) -> None:
    result = await client.execute_query(sample_database_id, "SELECT 1 AS test_val")
    assert result is not None
    assert "data" in result
    rows = result["data"].get("rows", [])
    assert len(rows) > 0
    assert rows[0][0] == 1
