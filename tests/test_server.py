"""Tests for server creation."""

from __future__ import annotations

import pytest

from metabase_mcp.server import create_server


def test_create_server_returns_fastmcp(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify create_server returns a configured FastMCP instance."""
    monkeypatch.setenv("METABASE_URL", "http://localhost:3000")
    monkeypatch.setenv("METABASE_API_KEY", "mb_test_key")
    server = create_server(mode="essential")
    assert server.name == "Metabase MCP Server"


def test_create_server_all_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("METABASE_URL", "http://localhost:3000")
    monkeypatch.setenv("METABASE_API_KEY", "mb_test_key")
    server = create_server(mode="all")
    provider = server._local_provider
    tool_names = {
        key.split(":")[1].split("@")[0] for key in provider._components if key.startswith("tool:")
    }
    assert len(tool_names) > 50
