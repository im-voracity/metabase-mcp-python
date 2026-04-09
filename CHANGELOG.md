# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Session token automatic refresh with TTL tracking and 401-based re-authentication in `MetabaseAuth` (#2)
- Comprehensive test suite: 190 tests with 84% coverage (up from 51%) (#6)
- `pytest-cov` dev dependency and `--cov-fail-under=80` enforcement in CI (#6)
- Portuguese (pt-BR) documentation: translated README, architecture guide, and tools reference (#11)

### Changed

- Replaced nested `if/elif` with guard clauses in `audit_dashboard_filters()` for readability (#8)
- Extracted `_build_bool_params()` helper to eliminate duplicated optional parameter building in `client.py` (#9)
- Extracted `_find_field_by_name()` static method from `get_field_by_name()` for testability (#10)
- Removed repetitive `try/except RuntimeError` boilerplate from all tool functions in `table.py` and `additional.py` (#5)
- Decomposed `get_dashboard_queries()` into focused helpers: `_resolve_field_ref`, `_resolve_mbql`, `_process_dashcard` (#7)

### Fixed

- URL-encode string parameters interpolated in URL paths to prevent path traversal (#3)
- Removed raw `response.text` from exception messages to prevent leaking sensitive data (#4)

## [0.1.0] - 2026-04-08

### Added

- Async HTTP client (`MetabaseClient`) with API key and session token authentication via `httpx.Auth` subclass
- 87 MCP tools across 5 categories: database (13), table (17), card (21), dashboard (27), additional (9)
- Tool filtering modes: `--essential` (19 tools, default), `--write` (59 tools), `--all` (87 tools)
- Configuration via environment variables or `.env` file using `pydantic-settings`
- `parse_if_string` validator for MCP clients that serialize objects as JSON strings
- Pydantic models with `extra="allow"` for all Metabase API types
- Custom exception hierarchy: `MetabaseError`, `MetabaseAuthError`, `MetabaseNotFoundError`, `MetabaseAPIError`
- CLI entry point: `metabase-mcp` / `python -m metabase_mcp`
- 68 unit tests with respx mocks and AsyncMock
- 19 integration tests against real Metabase instance
- CI pipeline with ruff, mypy, pytest, and pip-audit
- Documentation: README, architecture guide, tools reference, credits

[0.1.0]: https://github.com/im-voracity/metabase-mcp-python/releases/tag/v0.1.0
