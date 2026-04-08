"""Fixtures for integration tests against a real Metabase instance.

Tests are skipped if METABASE_URL is not configured.
A test collection is created at setup and cleaned up at teardown.
"""

from __future__ import annotations

import contextlib
import time
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio

from metabase_mcp.client import MetabaseClient
from metabase_mcp.config import MetabaseConfig


def pytest_collection_modifyitems(config, items):  # type: ignore[no-untyped-def]
    """Skip integration tests unless --run-integration is passed or marker is selected."""
    if config.getoption("-m", default="") and "integration" in config.getoption("-m", default=""):
        return
    skip = pytest.mark.skip(reason="need --run-integration or -m integration to run")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip)


@pytest.fixture(scope="session")
def metabase_config() -> MetabaseConfig:
    try:
        return MetabaseConfig()  # type: ignore[call-arg]
    except Exception:
        pytest.skip("Metabase credentials not configured (check .env)")
        raise  # unreachable


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def client(metabase_config: MetabaseConfig) -> AsyncIterator[MetabaseClient]:
    """Session-scoped client for integration tests."""
    c = MetabaseClient(metabase_config)
    yield c
    await c.close()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def test_collection(client: MetabaseClient) -> AsyncIterator[dict]:
    """Create a test collection for all integration tests. Cleaned up after session."""
    name = f"__metabase_mcp_test__{int(time.time())}"
    collection = await client.create_collection(
        {"name": name, "description": "Integration test collection"}
    )
    yield collection

    # Cleanup: delete all items in the collection, then the collection itself
    try:
        items = await client.api_call("GET", f"/api/collection/{collection['id']}/items")
        data = items.get("data", items) if isinstance(items, dict) else items
        if isinstance(data, list):
            for item in data:
                item_type = item.get("model", "")
                item_id = item.get("id")
                if item_type == "dashboard" and item_id:
                    with contextlib.suppress(Exception):
                        await client.delete_dashboard(item_id, hard_delete=True)
                elif item_type == "card" and item_id:
                    with contextlib.suppress(Exception):
                        await client.delete_card(item_id, hard_delete=True)
    except Exception:
        pass

    try:
        await client.delete_collection(collection["id"])
    except Exception:
        with contextlib.suppress(Exception):
            await client.update_collection(collection["id"], {"archived": True})


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def sample_database_id(client: MetabaseClient) -> int:
    """Find the Sample Database ID (always exists in Metabase)."""
    dbs = await client.get_databases()
    db_list = dbs.get("data", dbs) if isinstance(dbs, dict) else dbs
    for db in db_list:
        if db.get("name") == "Sample Database":
            return db["id"]
    pytest.skip("Sample Database not found in Metabase instance")
    return 0  # unreachable
