"""Metabase API Client.

Async HTTP client wrapping the Metabase REST API using httpx.
Authentication is handled via httpx.Auth subclass (replaces axios interceptors).
"""

from __future__ import annotations

import logging
import sys
import time
from typing import Any
from urllib.parse import quote

import httpx

from metabase_mcp.config import MetabaseConfig
from metabase_mcp.exceptions import (
    MetabaseAPIError,
    MetabaseAuthError,
    MetabaseError,
    MetabaseNotFoundError,
)

logger = logging.getLogger("metabase_mcp")


def _build_bool_params(**kwargs: bool | None) -> dict[str, str]:
    """Build query params dict from optional boolean values, excluding None."""
    return {k: str(v).lower() for k, v in kwargs.items() if v is not None}

# Configure logging to stderr in JSON-ish format
if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class MetabaseAuth(httpx.Auth):
    """Custom httpx Auth that handles API key or session token authentication.

    This replaces the axios request interceptor from the TypeScript version.
    The auth_flow() generator can yield sub-requests for session token acquisition.

    Session tokens are automatically refreshed when they approach expiration
    or when a 401 response is received.
    """

    TOKEN_TTL_SECONDS = 3600  # Metabase default session expiry: ~1 hour
    TOKEN_REFRESH_MARGIN = 0.9  # Refresh at 90% of TTL

    def __init__(self, config: MetabaseConfig) -> None:
        self._config = config
        self._session_token: str | None = None
        self._token_obtained_at: float = 0.0

    def _is_token_expired(self) -> bool:
        if not self._session_token:
            return True
        elapsed = time.monotonic() - self._token_obtained_at
        return elapsed > self.TOKEN_TTL_SECONDS * self.TOKEN_REFRESH_MARGIN

    def _clear_token(self) -> None:
        self._session_token = None
        self._token_obtained_at = 0.0

    def _acquire_token(self, request: httpx.Request) -> httpx.Request:
        """Build a login request to acquire a session token."""
        return httpx.Request(
            "POST",
            str(request.url).split("/api/")[0] + "/api/session",
            json={
                "username": self._config.username,
                "password": self._config.password,
            },
            headers={"Content-Type": "application/json"},
        )

    def auth_flow(self, request: httpx.Request) -> Any:
        if self._config.api_key:
            request.headers["X-API-Key"] = self._config.api_key
            yield request
            return

        if self._is_token_expired():
            login_response = yield self._acquire_token(request)
            if login_response.status_code != 200:
                self._clear_token()
                raise MetabaseAuthError(
                    "Failed to authenticate with Metabase",
                    status_code=login_response.status_code,
                )
            self._session_token = login_response.json()["id"]
            self._token_obtained_at = time.monotonic()
            logger.info("Session token acquired")

        assert self._session_token is not None  # guaranteed by _is_token_expired check
        request.headers["X-Metabase-Session"] = self._session_token
        response = yield request

        # If we get 401, clear token so next request re-authenticates
        if response.status_code == 401:
            logger.debug("Received 401, clearing session token for re-auth")
            self._clear_token()


class MetabaseClient:
    """Async client for the Metabase REST API."""

    def __init__(self, config: MetabaseConfig) -> None:
        self._config = config
        self._client = httpx.AsyncClient(
            base_url=config.url,
            timeout=30.0,
            auth=MetabaseAuth(config),
            headers={"Content-Type": "application/json"},
            follow_redirects=True,
        )
        auth_method = "API Key" if config.api_key else "username/password"
        logger.info("MetabaseClient initialized with %s authentication", auth_method)

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> MetabaseClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    # ── Core request method ──────────────────────────────────────────────

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        """Central request method with error handling."""
        try:
            response = await self._client.request(method, path, **kwargs)
        except httpx.TimeoutException as e:
            raise MetabaseError(f"Request timed out: {method} {path}") from e
        except httpx.HTTPError as e:
            raise MetabaseError(f"HTTP error: {method} {path}: {e}") from e

        if response.status_code in (401, 403):
            logger.debug("Auth error response: %s", response.text)
            raise MetabaseAuthError(
                f"Authentication failed: {method} {path} (HTTP {response.status_code})",
                status_code=response.status_code,
            )
        if response.status_code == 404:
            raise MetabaseNotFoundError(
                f"Not found: {method} {path}",
                status_code=404,
            )
        if response.status_code >= 400:
            logger.debug("API error response: %s", response.text)
            raise MetabaseAPIError(
                f"API error: {method} {path} (HTTP {response.status_code})",
                status_code=response.status_code,
            )

        if not response.content:
            return None
        return response.json()

    # ── Dashboard operations ─────────────────────────────────────────────

    async def get_dashboards(self) -> Any:
        return await self._request("GET", "/api/dashboard")

    async def get_dashboard(self, id: int) -> Any:
        return await self._request("GET", f"/api/dashboard/{id}")

    async def create_dashboard(self, dashboard: dict[str, Any]) -> Any:
        return await self._request("POST", "/api/dashboard", json=dashboard)

    async def update_dashboard(self, id: int, updates: dict[str, Any]) -> Any:
        return await self._request("PUT", f"/api/dashboard/{id}", json=updates)

    async def delete_dashboard(self, id: int, hard_delete: bool = False) -> Any:
        if hard_delete:
            return await self._request("DELETE", f"/api/dashboard/{id}")
        return await self._request("PUT", f"/api/dashboard/{id}", json={"archived": True})

    async def get_dashboard_related(self, id: int) -> Any:
        return await self._request("GET", f"/api/dashboard/{id}/related")

    async def get_dashboard_revisions(self, id: int) -> Any:
        return await self._request("GET", f"/api/dashboard/{id}/revisions")

    async def get_embeddable_dashboards(self) -> Any:
        return await self._request("GET", "/api/dashboard/embeddable")

    async def get_public_dashboards(self) -> Any:
        return await self._request("GET", "/api/dashboard/public")

    async def create_dashboard_public_link(self, id: int) -> Any:
        return await self._request("POST", f"/api/dashboard/{id}/public_link")

    async def delete_dashboard_public_link(self, id: int) -> Any:
        return await self._request("DELETE", f"/api/dashboard/{id}/public_link")

    async def copy_dashboard(self, from_id: int, copy_data: dict[str, Any] | None = None) -> Any:
        return await self._request("POST", f"/api/dashboard/{from_id}/copy", json=copy_data or {})

    # ── Dashboard card operations ────────────────────────────────────────

    async def add_card_to_dashboard(self, dashboard_id: int, card_data: dict[str, Any]) -> Any:
        dashboard = await self.get_dashboard(dashboard_id)
        existing_dashcards = dashboard.get("dashcards", [])
        existing_tabs = dashboard.get("tabs", [])

        new_dashcard: dict[str, Any] = {
            "id": -1,
            "row": card_data.get("row", 0),
            "col": card_data.get("col", 0),
            "size_x": card_data.get("size_x") or card_data.get("sizeX") or 12,
            "size_y": card_data.get("size_y") or card_data.get("sizeY") or 8,
            "series": card_data.get("series", []),
            "visualization_settings": card_data.get("visualization_settings", {}),
            "parameter_mappings": card_data.get("parameter_mappings", []),
        }

        card_id = card_data.get("cardId") or card_data.get("card_id")
        if card_id is not None:
            new_dashcard["card_id"] = card_id

        if "dashboard_tab_id" in card_data:
            new_dashcard["dashboard_tab_id"] = card_data["dashboard_tab_id"]

        cleaned = self._clean_dashcards(existing_dashcards)

        return await self._request(
            "PUT",
            f"/api/dashboard/{dashboard_id}",
            json={"dashcards": [*cleaned, new_dashcard], "tabs": existing_tabs},
        )

    async def update_dashboard_cards(self, dashboard_id: int, cards: list[Any]) -> Any:
        dashboard = await self.get_dashboard(dashboard_id)
        return await self._request(
            "PUT",
            f"/api/dashboard/{dashboard_id}",
            json={**dashboard, "dashcards": cards},
        )

    async def update_dashcard(
        self, dashboard_id: int, dashcard_id: int, updates: dict[str, Any]
    ) -> Any:
        dashboard = await self.get_dashboard(dashboard_id)
        dashcards = dashboard.get("dashcards", [])

        if not any(dc["id"] == dashcard_id for dc in dashcards):
            raise MetabaseError(
                f"Dashcard with id {dashcard_id} not found in dashboard {dashboard_id}"
            )

        updated = [{**dc, **updates} if dc["id"] == dashcard_id else dc for dc in dashcards]
        return await self._request(
            "PUT",
            f"/api/dashboard/{dashboard_id}",
            json={**dashboard, "dashcards": updated},
        )

    async def remove_cards_from_dashboard(
        self, dashboard_id: int, dashcard_ids: list[int]
    ) -> Any:
        dashboard = await self.get_dashboard(dashboard_id)
        existing = dashboard.get("dashcards", [])
        filtered = [dc for dc in existing if dc["id"] not in dashcard_ids]
        return await self._request(
            "PUT",
            f"/api/dashboard/{dashboard_id}",
            json={**dashboard, "dashcards": filtered},
        )

    async def favorite_dashboard(self, id: int) -> Any:
        return await self._request("POST", f"/api/dashboard/{id}/favorite")

    async def unfavorite_dashboard(self, id: int) -> Any:
        return await self._request("DELETE", f"/api/dashboard/{id}/favorite")

    async def revert_dashboard(self, id: int, revision_id: int) -> Any:
        return await self._request(
            "POST", f"/api/dashboard/{id}/revert", json={"revision_id": revision_id}
        )

    async def save_dashboard(self, dashboard: dict[str, Any]) -> Any:
        return await self._request("POST", "/api/dashboard/save", json=dashboard)

    async def save_dashboard_to_collection(
        self, parent_collection_id: int, dashboard: dict[str, Any]
    ) -> Any:
        return await self._request(
            "POST", f"/api/dashboard/save/collection/{parent_collection_id}", json=dashboard
        )

    # ── Dashboard parameter operations ──────────────────────────────────────

    async def get_dashboard_param_values(
        self, dashboard_id: int, param_key: str
    ) -> Any:
        return await self._request(
            "GET", f"/api/dashboard/{dashboard_id}/params/{param_key}/values"
        )

    async def search_dashboard_param_values(
        self, dashboard_id: int, param_key: str, query: str
    ) -> Any:
        return await self._request(
            "GET",
            f"/api/dashboard/{dashboard_id}/params/{param_key}/search/{query}",
        )

    # ── Dashboard tab operations ──────────────────────────────────────────
    #
    # Metabase manages tabs atomically through PUT /api/dashboard/:id
    # with the full tabs + dashcards arrays. There are no dedicated
    # tab sub-resource endpoints.

    async def create_dashboard_tab(self, dashboard_id: int, name: str) -> Any:
        dashboard = await self.get_dashboard(dashboard_id)
        existing_tabs = dashboard.get("tabs", [])
        existing_dashcards = dashboard.get("dashcards", [])
        new_tab = {"id": -1, "name": name}
        result = await self._request(
            "PUT",
            f"/api/dashboard/{dashboard_id}",
            json={
                "dashcards": self._clean_dashcards(existing_dashcards),
                "tabs": [*existing_tabs, new_tab],
            },
        )
        # Return only the newly created tab (last one with a new id)
        existing_ids = {t["id"] for t in existing_tabs}
        for tab in reversed(result.get("tabs", [])):
            if tab["id"] not in existing_ids:
                return tab
        return result.get("tabs", [])[-1] if result.get("tabs") else result

    async def update_dashboard_tab(
        self, dashboard_id: int, tab_id: int, name: str
    ) -> Any:
        dashboard = await self.get_dashboard(dashboard_id)
        tabs = dashboard.get("tabs", [])
        existing_dashcards = dashboard.get("dashcards", [])
        updated_tabs = [
            {**t, "name": name} if t["id"] == tab_id else t for t in tabs
        ]
        result = await self._request(
            "PUT",
            f"/api/dashboard/{dashboard_id}",
            json={
                "dashcards": self._clean_dashcards(existing_dashcards),
                "tabs": updated_tabs,
            },
        )
        for tab in result.get("tabs", []):
            if tab["id"] == tab_id:
                return tab
        return result

    async def delete_dashboard_tab(self, dashboard_id: int, tab_id: int) -> Any:
        dashboard = await self.get_dashboard(dashboard_id)
        tabs = dashboard.get("tabs", [])
        existing_dashcards = dashboard.get("dashcards", [])
        filtered_tabs = [t for t in tabs if t["id"] != tab_id]
        # Also remove dashcards assigned to the deleted tab
        filtered_dashcards = [
            dc for dc in existing_dashcards if dc.get("dashboard_tab_id") != tab_id
        ]
        return await self._request(
            "PUT",
            f"/api/dashboard/{dashboard_id}",
            json={
                "dashcards": self._clean_dashcards(filtered_dashcards),
                "tabs": filtered_tabs,
            },
        )

    @staticmethod
    def _clean_dashcards(dashcards: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Normalize dashcards for PUT /api/dashboard/:id payload."""
        return [
            {
                "id": dc["id"],
                "card_id": dc.get("card_id"),
                "row": dc.get("row", 0),
                "col": dc.get("col", 0),
                "size_x": dc.get("size_x", 12),
                "size_y": dc.get("size_y", 8),
                "series": dc.get("series", []),
                "visualization_settings": dc.get("visualization_settings", {}),
                "parameter_mappings": dc.get("parameter_mappings", []),
                **(
                    {"dashboard_tab_id": dc["dashboard_tab_id"]}
                    if "dashboard_tab_id" in dc
                    else {}
                ),
            }
            for dc in dashcards
        ]

    # ── Card operations ──────────────────────────────────────────────────

    async def get_cards(self, f: str | None = None, model_id: int | None = None) -> Any:
        params: dict[str, Any] = {}
        if f is not None:
            params["f"] = f
        if model_id is not None:
            params["model_id"] = model_id
        return await self._request("GET", "/api/card", params=params)

    async def get_card(self, id: int) -> Any:
        return await self._request("GET", f"/api/card/{id}")

    async def create_card(self, card: dict[str, Any]) -> Any:
        return await self._request("POST", "/api/card", json=card)

    async def update_card(
        self,
        id: int,
        updates: dict[str, Any],
        query_params: dict[str, Any] | None = None,
    ) -> Any:
        params = {}
        if query_params:
            params = {k: str(v) for k, v in query_params.items() if v is not None}
        return await self._request("PUT", f"/api/card/{id}", json=updates, params=params)

    async def delete_card(self, id: int, hard_delete: bool = False) -> Any:
        if hard_delete:
            return await self._request("DELETE", f"/api/card/{id}")
        return await self._request("PUT", f"/api/card/{id}", json={"archived": True})

    async def execute_card(
        self,
        id: int,
        ignore_cache: bool = False,
        collection_preview: bool | None = None,
        dashboard_id: int | None = None,
    ) -> Any:
        body: dict[str, Any] = {"ignore_cache": ignore_cache}
        if collection_preview is not None:
            body["collection_preview"] = collection_preview
        if dashboard_id is not None:
            body["dashboard_id"] = dashboard_id
        return await self._request("POST", f"/api/card/{id}/query", json=body)

    async def move_cards(
        self,
        card_ids: list[int],
        collection_id: int | None = None,
        dashboard_id: int | None = None,
    ) -> Any:
        data: dict[str, Any] = {"card_ids": card_ids}
        if collection_id is not None:
            data["collection_id"] = collection_id
        if dashboard_id is not None:
            data["dashboard_id"] = dashboard_id
        return await self._request("POST", "/api/cards/move", json=data)

    async def move_cards_to_collection(
        self, card_ids: list[int], collection_id: int | None = None
    ) -> Any:
        data: dict[str, Any] = {"card_ids": card_ids}
        if collection_id is not None:
            data["collection_id"] = collection_id
        return await self._request("POST", "/api/card/collections", json=data)

    async def get_embeddable_cards(self) -> Any:
        return await self._request("GET", "/api/card/embeddable")

    async def execute_pivot_card_query(
        self, card_id: int, parameters: dict[str, Any] | None = None
    ) -> Any:
        return await self._request(
            "POST", f"/api/card/pivot/{card_id}/query", json=parameters or {}
        )

    async def get_public_cards(self) -> Any:
        return await self._request("GET", "/api/card/public")

    async def get_card_param_values(self, card_id: int, param_key: str) -> Any:
        return await self._request(
            "GET", f"/api/card/{card_id}/params/{quote(param_key, safe='')}/values"
        )

    async def search_card_param_values(
        self, card_id: int, param_key: str, query: str
    ) -> Any:
        encoded_key = quote(param_key, safe="")
        encoded_query = quote(query, safe="")
        return await self._request(
            "GET",
            f"/api/card/{card_id}/params/{encoded_key}/search/{encoded_query}",
        )

    async def get_card_param_remapping(
        self, card_id: int, param_key: str, value: str
    ) -> Any:
        return await self._request(
            "GET",
            f"/api/card/{card_id}/params/{quote(param_key, safe='')}/remapping",
            params={"value": value},
        )

    async def create_card_public_link(self, card_id: int) -> Any:
        return await self._request("POST", f"/api/card/{card_id}/public_link")

    async def delete_card_public_link(self, card_id: int) -> Any:
        await self._request("DELETE", f"/api/card/{card_id}/public_link")
        return {"success": True}

    async def execute_card_query_with_format(
        self, card_id: int, export_format: str, parameters: dict[str, Any] | None = None
    ) -> Any:
        return await self._request(
            "POST",
            f"/api/card/{card_id}/query/{quote(export_format, safe='')}",
            json=parameters or {},
        )

    async def copy_card(self, card_id: int) -> Any:
        return await self._request("POST", f"/api/card/{card_id}/copy")

    async def get_card_dashboards(self, card_id: int) -> Any:
        return await self._request("GET", f"/api/card/{card_id}/dashboards")

    async def get_card_query_metadata(self, card_id: int) -> Any:
        return await self._request("GET", f"/api/card/{card_id}/query_metadata")

    async def get_card_series(
        self,
        card_id: int,
        last_cursor: str | int | None = None,
        query: str | None = None,
        exclude_ids: list[int] | None = None,
    ) -> Any:
        params: dict[str, Any] = {}
        if last_cursor is not None:
            params["last_cursor"] = str(last_cursor)
        if query:
            params["query"] = query
        if exclude_ids:
            # httpx handles repeated params differently — join as comma-separated
            for eid in exclude_ids:
                params.setdefault("exclude_ids", [])
                params["exclude_ids"].append(str(eid))
        return await self._request("GET", f"/api/card/{card_id}/series", params=params)

    # ── Database operations ──────────────────────────────────────────────

    async def get_databases(self) -> Any:
        return await self._request("GET", "/api/database")

    async def get_database(self, id: int) -> Any:
        return await self._request("GET", f"/api/database/{id}")

    async def create_database(self, payload: dict[str, Any]) -> Any:
        return await self._request("POST", "/api/database", json=payload)

    async def update_database(self, id: int, updates: dict[str, Any]) -> Any:
        return await self._request("PUT", f"/api/database/{id}", json=updates)

    async def delete_database(self, id: int) -> Any:
        return await self._request("DELETE", f"/api/database/{id}")

    async def validate_database(self, engine: str, details: dict[str, Any]) -> Any:
        return await self._request(
            "POST", "/api/database/validate", json={"engine": engine, "details": details}
        )

    async def add_sample_database(self) -> Any:
        return await self._request("POST", "/api/database/sample_database")

    async def check_database_health(self, id: int) -> Any:
        return await self._request("GET", f"/api/database/{id}/healthcheck")

    async def get_database_metadata(self, id: int) -> Any:
        return await self._request("GET", f"/api/database/{id}/metadata")

    async def get_database_schemas(self, id: int) -> Any:
        return await self._request("GET", f"/api/database/{id}/schemas")

    async def get_database_schema(self, id: int, schema: str) -> Any:
        return await self._request(
            "GET", f"/api/database/{id}/schema/{quote(schema, safe='')}"
        )

    async def sync_database_schema(self, id: int) -> Any:
        return await self._request("POST", f"/api/database/{id}/sync_schema")

    async def execute_query(
        self, database_id: int, query: str, parameters: list[Any] | None = None
    ) -> Any:
        data = {
            "type": "native",
            "native": {"query": query, "template_tags": {}},
            "parameters": parameters or [],
            "database": database_id,
        }
        return await self._request("POST", "/api/dataset", json=data)

    # ── Collection operations ────────────────────────────────────────────

    async def get_collections(self, archived: bool = False) -> Any:
        params = {"archived": "true"} if archived else {}
        return await self._request("GET", "/api/collection", params=params)

    async def get_collection(self, id: int) -> Any:
        return await self._request("GET", f"/api/collection/{id}")

    async def create_collection(self, collection: dict[str, Any]) -> Any:
        return await self._request("POST", "/api/collection", json=collection)

    async def update_collection(self, id: int, updates: dict[str, Any]) -> Any:
        return await self._request("PUT", f"/api/collection/{id}", json=updates)

    async def delete_collection(self, id: int) -> Any:
        return await self._request("DELETE", f"/api/collection/{id}")

    # ── User operations ──────────────────────────────────────────────────

    async def get_users(self, include_deactivated: bool = False) -> Any:
        params = {"include_deactivated": "true"} if include_deactivated else {}
        return await self._request("GET", "/api/user", params=params)

    async def get_user(self, id: int) -> Any:
        return await self._request("GET", f"/api/user/{id}")

    async def create_user(self, user: dict[str, Any]) -> Any:
        return await self._request("POST", "/api/user", json=user)

    async def update_user(self, id: int, updates: dict[str, Any]) -> Any:
        return await self._request("PUT", f"/api/user/{id}", json=updates)

    async def delete_user(self, id: int) -> Any:
        return await self._request("DELETE", f"/api/user/{id}")

    # ── Permission operations ────────────────────────────────────────────

    async def get_permission_groups(self) -> Any:
        return await self._request("GET", "/api/permissions/group")

    async def create_permission_group(self, name: str) -> Any:
        return await self._request("POST", "/api/permissions/group", json={"name": name})

    async def update_permission_group(self, id: int, name: str) -> Any:
        return await self._request("PUT", f"/api/permissions/group/{id}", json={"name": name})

    async def delete_permission_group(self, id: int) -> Any:
        return await self._request("DELETE", f"/api/permissions/group/{id}")

    # ── Activity operations ──────────────────────────────────────────────

    async def get_most_recently_viewed_dashboard(self) -> Any:
        return await self._request("GET", "/api/activity/most_recently_viewed_dashboard")

    async def get_popular_items(self) -> Any:
        return await self._request("GET", "/api/activity/popular_items")

    async def get_recent_views(self) -> Any:
        return await self._request("GET", "/api/activity/recent_views")

    async def get_recents(
        self, context: list[str], include_metadata: bool = False
    ) -> Any:
        params: dict[str, Any] = {"include_metadata": str(include_metadata).lower()}
        for ctx in context:
            params.setdefault("context", [])
            params["context"].append(ctx)
        return await self._request("GET", "/api/activity/recents", params=params)

    async def post_recents(self, data: dict[str, Any]) -> Any:
        return await self._request("POST", "/api/activity/recents", json=data)

    async def execute_query_export(
        self,
        export_format: str,
        query: Any,
        format_rows: bool = False,
        pivot_results: bool = False,
        visualization_settings: dict[str, Any] | None = None,
    ) -> Any:
        data = {
            "format_rows": format_rows,
            "pivot_results": pivot_results,
            "query": query,
            "visualization_settings": visualization_settings or {},
        }
        return await self._request(
            "POST", f"/api/dataset/{quote(export_format, safe='')}", json=data
        )

    # ── Table operations ─────────────────────────────────────────────────

    async def get_tables(self, ids: list[int] | None = None) -> Any:
        params = {}
        if ids:
            params["ids"] = ",".join(str(i) for i in ids)
        return await self._request("GET", "/api/table", params=params)

    async def update_tables(self, ids: list[int], updates: dict[str, Any]) -> Any:
        return await self._request("PUT", "/api/table", json={"ids": ids, **updates})

    async def get_card_table_fks(self, card_id: int) -> Any:
        return await self._request("GET", f"/api/table/card__{card_id}/fks")

    async def get_card_table_query_metadata(self, card_id: int) -> Any:
        return await self._request("GET", f"/api/table/card__{card_id}/query_metadata")

    async def get_table(
        self,
        id: int,
        include_sensitive_fields: bool | None = None,
        include_hidden_fields: bool | None = None,
        include_editable_data_model: bool | None = None,
    ) -> Any:
        params = _build_bool_params(
            include_sensitive_fields=include_sensitive_fields,
            include_hidden_fields=include_hidden_fields,
            include_editable_data_model=include_editable_data_model,
        )
        return await self._request("GET", f"/api/table/{id}", params=params)

    async def update_table(self, id: int, update_data: dict[str, Any]) -> Any:
        return await self._request("PUT", f"/api/table/{id}", json=update_data)

    async def append_csv_to_table(
        self, id: int, filename: str, file_content: str
    ) -> Any:
        files = {"file": (filename, file_content.encode(), "text/csv")}
        # Remove Content-Type header for multipart — httpx sets it automatically
        return await self._request(
            "POST",
            f"/api/table/{id}/append-csv",
            files=files,
        )

    async def discard_table_field_values(self, id: int) -> Any:
        return await self._request("POST", f"/api/table/{id}/discard_values")

    async def reorder_table_fields(self, id: int, field_order: list[int]) -> Any:
        return await self._request(
            "PUT", f"/api/table/{id}/fields/order", json=field_order
        )

    async def get_table_fks(self, id: int) -> Any:
        return await self._request("GET", f"/api/table/{id}/fks")

    async def get_table_query_metadata(
        self,
        id: int,
        include_sensitive_fields: bool | None = None,
        include_hidden_fields: bool | None = None,
        include_editable_data_model: bool | None = None,
    ) -> Any:
        params = _build_bool_params(
            include_sensitive_fields=include_sensitive_fields,
            include_hidden_fields=include_hidden_fields,
            include_editable_data_model=include_editable_data_model,
        )
        return await self._request("GET", f"/api/table/{id}/query_metadata", params=params)

    @staticmethod
    def _find_field_by_name(
        fields: list[dict[str, Any]], column_name: str
    ) -> dict[str, Any] | None:
        """Find a field by name or display_name (case-insensitive)."""
        lower_name = column_name.lower()
        return next(
            (
                f
                for f in fields
                if f.get("name", "").lower() == lower_name
                or f.get("display_name", "").lower() == lower_name
            ),
            None,
        )

    async def get_field_by_name(self, table_id: int, column_name: str) -> Any:
        metadata = await self.get_table_query_metadata(table_id)
        fields = metadata.get("fields", [])

        field = self._find_field_by_name(fields, column_name)
        if not field:
            available = [f.get("name") for f in fields[:20]]
            suffix = "..." if len(fields) > 20 else ""
            raise MetabaseError(
                f"Field '{column_name}' not found in table {table_id}. "
                f"Available fields: {', '.join(str(n) for n in available)}{suffix}"
            )

        return {
            "field_id": field["id"],
            "name": field["name"],
            "display_name": field.get("display_name"),
            "base_type": field.get("base_type"),
            "semantic_type": field.get("semantic_type"),
            "table_id": table_id,
        }

    async def get_table_related(self, id: int) -> Any:
        return await self._request("GET", f"/api/table/{id}/related")

    async def replace_table_csv(self, id: int, csv_file: str) -> Any:
        files = {"file": ("data.csv", csv_file.encode(), "text/csv")}
        return await self._request("POST", f"/api/table/{id}/replace-csv", files=files)

    async def rescan_table_field_values(self, id: int) -> Any:
        return await self._request("POST", f"/api/table/{id}/rescan_values")

    async def sync_table_schema(self, id: int) -> Any:
        return await self._request("POST", f"/api/table/{id}/sync_schema")

    async def get_table_data(self, table_id: int, limit: int = 1000) -> Any:
        return await self._request(
            "GET", f"/api/table/{table_id}/data", params={"limit": str(limit)}
        )

    # ── Generic API method ───────────────────────────────────────────────

    async def api_call(
        self, method: str, endpoint: str, data: dict[str, Any] | None = None
    ) -> Any:
        kwargs: dict[str, Any] = {}
        if data is not None:
            kwargs["json"] = data
        return await self._request(method, endpoint, **kwargs)
