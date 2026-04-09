"""Tests for tool registry and filtering."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from fastmcp import FastMCP

from metabase_mcp.tools import (
    ESSENTIAL_TOOLS,
    WRITE_TOOLS,
    _should_register,
    register_all_tools,
)


def test_should_register_all_mode() -> None:
    assert _should_register("any_tool", "all") is True


def test_should_register_essential_mode() -> None:
    assert _should_register("list_dashboards", "essential") is True
    assert _should_register("delete_dashboard", "essential") is False


def test_should_register_write_mode() -> None:
    assert _should_register("list_dashboards", "write") is True  # essential
    assert _should_register("delete_dashboard", "write") is True  # write
    assert _should_register("nonexistent_tool", "write") is False


def test_should_register_unknown_mode() -> None:
    assert _should_register("any_tool", "unknown") is False


@pytest.fixture
def mcp() -> FastMCP:
    return FastMCP(name="test")


@pytest.fixture
def mock_client() -> AsyncMock:
    return AsyncMock()


def test_register_all_tools_all_mode(mcp: FastMCP, mock_client: AsyncMock) -> None:
    register_all_tools(mcp, mock_client, mode="all")
    provider = mcp._local_provider
    tool_names = {
        key.split(":")[1].split("@")[0] for key in provider._components if key.startswith("tool:")
    }
    # Should have many tools (all 87)
    assert len(tool_names) > 50


def test_register_all_tools_essential_mode(mcp: FastMCP, mock_client: AsyncMock) -> None:
    register_all_tools(mcp, mock_client, mode="essential")
    provider = mcp._local_provider
    tool_names = {
        key.split(":")[1].split("@")[0] for key in provider._components if key.startswith("tool:")
    }
    assert tool_names == ESSENTIAL_TOOLS


def test_register_all_tools_write_mode(mcp: FastMCP, mock_client: AsyncMock) -> None:
    register_all_tools(mcp, mock_client, mode="write")
    provider = mcp._local_provider
    tool_names = {
        key.split(":")[1].split("@")[0] for key in provider._components if key.startswith("tool:")
    }
    expected = ESSENTIAL_TOOLS | WRITE_TOOLS
    assert tool_names == expected
