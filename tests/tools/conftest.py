"""Shared fixtures for tool tests."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from fastmcp import FastMCP


@pytest.fixture
def mcp() -> FastMCP:
    return FastMCP("test")


@pytest.fixture
def mock_client() -> AsyncMock:
    return AsyncMock()
