"""Shared fixtures for unit tests."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from metabase_mcp.config import MetabaseConfig


@pytest.fixture
def mock_config() -> MetabaseConfig:
    """MetabaseConfig with fake API key credentials."""
    return MetabaseConfig(  # type: ignore[call-arg]
        url="http://localhost:3000",
        api_key="mb_test_key_12345",
    )


@pytest.fixture
def mock_config_credentials() -> MetabaseConfig:
    """MetabaseConfig with fake username/password credentials."""
    return MetabaseConfig(  # type: ignore[call-arg]
        url="http://localhost:3000",
        username="test@example.com",
        password="testpassword",
    )


@pytest.fixture
def mock_client() -> AsyncMock:
    """Fully mocked MetabaseClient for tool tests."""
    client = AsyncMock()
    client.get_dashboards = AsyncMock(return_value=[])
    client.get_dashboard = AsyncMock(return_value={"id": 1, "name": "Test"})
    client.create_dashboard = AsyncMock(return_value={"id": 1, "name": "New"})
    client.update_dashboard = AsyncMock(return_value={"id": 1, "name": "Updated"})
    client.delete_dashboard = AsyncMock(return_value=None)
    client.get_cards = AsyncMock(return_value=[])
    client.get_card = AsyncMock(return_value={"id": 1, "name": "Test Card"})
    client.create_card = AsyncMock(return_value={"id": 1, "name": "New Card"})
    client.update_card = AsyncMock(return_value={"id": 1, "name": "Updated Card"})
    client.delete_card = AsyncMock(return_value=None)
    client.execute_card = AsyncMock(return_value={"data": {"rows": [[42]]}})
    client.get_databases = AsyncMock(return_value=[{"id": 1, "name": "Test DB"}])
    client.get_database = AsyncMock(return_value={"id": 1, "name": "Test DB"})
    client.execute_query = AsyncMock(return_value={"data": {"rows": [[1]]}})
    client.get_collections = AsyncMock(return_value=[{"id": 1, "name": "Root"}])
    client.get_collection = AsyncMock(return_value={"id": 1, "name": "Root"})
    client.api_call = AsyncMock(return_value={"data": []})
    return client
