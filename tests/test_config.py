"""Tests for MetabaseConfig validation."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from metabase_mcp.config import MetabaseConfig


def test_config_with_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("METABASE_URL", raising=False)
    monkeypatch.delenv("METABASE_API_KEY", raising=False)
    monkeypatch.delenv("METABASE_USERNAME", raising=False)
    monkeypatch.delenv("METABASE_PASSWORD", raising=False)
    config = MetabaseConfig(url="http://localhost:3000", api_key="mb_test", _env_file=None)  # type: ignore[call-arg]
    assert config.url == "http://localhost:3000"
    assert config.api_key == "mb_test"
    assert config.username is None
    assert config.password is None


def test_config_with_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("METABASE_URL", raising=False)
    monkeypatch.delenv("METABASE_API_KEY", raising=False)
    monkeypatch.delenv("METABASE_USERNAME", raising=False)
    monkeypatch.delenv("METABASE_PASSWORD", raising=False)
    config = MetabaseConfig(  # type: ignore[call-arg]
        url="http://localhost:3000",
        username="user@test.com",
        password="secret",
        _env_file=None,
    )
    assert config.username == "user@test.com"
    assert config.password == "secret"
    assert config.api_key is None


def test_config_missing_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("METABASE_URL", raising=False)
    monkeypatch.delenv("METABASE_API_KEY", raising=False)
    monkeypatch.delenv("METABASE_USERNAME", raising=False)
    monkeypatch.delenv("METABASE_PASSWORD", raising=False)
    with pytest.raises(ValidationError):
        MetabaseConfig(api_key="mb_test", _env_file=None)  # type: ignore[call-arg]


def test_config_no_auth(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("METABASE_URL", raising=False)
    monkeypatch.delenv("METABASE_API_KEY", raising=False)
    monkeypatch.delenv("METABASE_USERNAME", raising=False)
    monkeypatch.delenv("METABASE_PASSWORD", raising=False)
    with pytest.raises(ValidationError, match="authentication not configured"):
        MetabaseConfig(url="http://localhost:3000", _env_file=None)  # type: ignore[call-arg]


def test_config_invalid_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("METABASE_URL", raising=False)
    monkeypatch.delenv("METABASE_API_KEY", raising=False)
    with pytest.raises(ValidationError, match="Invalid Metabase URL"):
        MetabaseConfig(url="not-a-url", api_key="mb_test", _env_file=None)  # type: ignore[call-arg]


def test_config_partial_credentials_missing_password(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("METABASE_URL", raising=False)
    monkeypatch.delenv("METABASE_API_KEY", raising=False)
    monkeypatch.delenv("METABASE_USERNAME", raising=False)
    monkeypatch.delenv("METABASE_PASSWORD", raising=False)
    with pytest.raises(ValidationError, match="authentication not configured"):
        MetabaseConfig(url="http://localhost:3000", username="user@test.com", _env_file=None)  # type: ignore[call-arg]


def test_config_partial_credentials_missing_username(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("METABASE_URL", raising=False)
    monkeypatch.delenv("METABASE_API_KEY", raising=False)
    monkeypatch.delenv("METABASE_USERNAME", raising=False)
    monkeypatch.delenv("METABASE_PASSWORD", raising=False)
    with pytest.raises(ValidationError, match="authentication not configured"):
        MetabaseConfig(url="http://localhost:3000", password="secret", _env_file=None)  # type: ignore[call-arg]


def test_config_https_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("METABASE_URL", raising=False)
    monkeypatch.delenv("METABASE_API_KEY", raising=False)
    config = MetabaseConfig(url="https://metabase.example.com", api_key="mb_test", _env_file=None)  # type: ignore[call-arg]
    assert config.url == "https://metabase.example.com"
