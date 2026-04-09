"""Tests for CLI entry point."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


def test_main_parses_essential_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify --essential mode is the default."""
    monkeypatch.setenv("METABASE_URL", "http://localhost:3000")
    monkeypatch.setenv("METABASE_API_KEY", "mb_test_key")
    monkeypatch.setattr("sys.argv", ["metabase-mcp"])

    mock_server = MagicMock()
    with patch("metabase_mcp.__main__.create_server", return_value=mock_server) as mock_create:
        from metabase_mcp.__main__ import main

        main()
    mock_create.assert_called_once_with(mode="essential")
    mock_server.run.assert_called_once_with(transport="stdio")


def test_main_parses_all_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("METABASE_URL", "http://localhost:3000")
    monkeypatch.setenv("METABASE_API_KEY", "mb_test_key")
    monkeypatch.setattr("sys.argv", ["metabase-mcp", "--all"])

    mock_server = MagicMock()
    with patch("metabase_mcp.__main__.create_server", return_value=mock_server) as mock_create:
        from metabase_mcp.__main__ import main

        main()
    mock_create.assert_called_once_with(mode="all")


def test_main_parses_write_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("METABASE_URL", "http://localhost:3000")
    monkeypatch.setenv("METABASE_API_KEY", "mb_test_key")
    monkeypatch.setattr("sys.argv", ["metabase-mcp", "--write"])

    mock_server = MagicMock()
    with patch("metabase_mcp.__main__.create_server", return_value=mock_server) as mock_create:
        from metabase_mcp.__main__ import main

        main()
    mock_create.assert_called_once_with(mode="write")
