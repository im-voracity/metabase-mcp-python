"""Tests for parse_if_string and related validators."""

from __future__ import annotations

from metabase_mcp.validators import parse_if_string


def test_parse_json_object_string() -> None:
    assert parse_if_string('{"a": 1}') == {"a": 1}


def test_parse_json_array_string() -> None:
    assert parse_if_string("[1, 2, 3]") == [1, 2, 3]


def test_passthrough_dict() -> None:
    value = {"a": 1}
    assert parse_if_string(value) is value


def test_passthrough_list() -> None:
    value = [1, 2]
    assert parse_if_string(value) is value


def test_passthrough_none() -> None:
    assert parse_if_string(None) is None


def test_passthrough_int() -> None:
    assert parse_if_string(42) == 42


def test_invalid_json_string_returns_string() -> None:
    assert parse_if_string("not json") == "not json"


def test_empty_string_returns_empty() -> None:
    assert parse_if_string("") == ""


def test_nested_json_string() -> None:
    result = parse_if_string('{"nested": {"key": "value"}}')
    assert result == {"nested": {"key": "value"}}


def test_json_string_with_boolean() -> None:
    assert parse_if_string("true") is True


def test_json_string_with_number() -> None:
    assert parse_if_string("42") == 42
