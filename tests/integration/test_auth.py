"""Integration tests for authentication methods."""

from __future__ import annotations

import pytest

from metabase_mcp.client import MetabaseClient
from metabase_mcp.config import MetabaseConfig

pytestmark = pytest.mark.integration


@pytest.mark.asyncio(loop_scope="session")
async def test_auth_with_api_key(metabase_config: MetabaseConfig) -> None:
    """Test authentication using API key."""
    if not metabase_config.api_key:
        pytest.skip("METABASE_API_KEY not set")

    config = MetabaseConfig(url=metabase_config.url, api_key=metabase_config.api_key)  # type: ignore[call-arg]
    async with MetabaseClient(config) as client:
        dbs = await client.get_databases()
        assert dbs is not None


@pytest.mark.asyncio(loop_scope="session")
async def test_auth_with_credentials(metabase_config: MetabaseConfig) -> None:
    """Test authentication using username/password."""
    if not metabase_config.username or not metabase_config.password:
        pytest.skip("METABASE_USERNAME/METABASE_PASSWORD not set")

    config = MetabaseConfig(  # type: ignore[call-arg]
        url=metabase_config.url,
        username=metabase_config.username,
        password=metabase_config.password,
    )
    async with MetabaseClient(config) as client:
        dbs = await client.get_databases()
        assert dbs is not None
