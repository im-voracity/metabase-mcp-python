"""MCP tools for collections, search, users, and playground."""

from __future__ import annotations

import base64
import json
import os
from typing import Annotated, Any
from urllib.parse import urlencode

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from metabase_mcp.client import MetabaseClient


def register_additional_tools(mcp: FastMCP, client: MetabaseClient) -> None:
    """Register collection, search, user, and playground tools."""

    # ── get_collection_items ────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def get_collection_items(
        collection_id: Annotated[int, Field(description="Collection ID")],
    ) -> str:
        """Retrieve all items (cards, dashboards) within a Metabase collection - use this to explore collection contents, organize analytical assets, or understand content structure"""
        try:
            result = await client.api_call(
                "GET", f"/api/collection/{collection_id}/items"
            )
            return json.dumps(result, indent=2)
        except Exception as e:
            raise RuntimeError(
                f"Failed to get items for collection {collection_id}: {e}"
            ) from e

    # ── move_to_collection ──────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False))
    async def move_to_collection(
        item_type: Annotated[str, Field(description="Item type (card or dashboard)")],
        item_id: Annotated[int, Field(description="Item ID")],
        collection_id: Annotated[
            int | None, Field(description="Target collection ID (null for root)")
        ],
    ) -> str:
        """Move a Metabase card or dashboard to a different collection - use this to reorganize content, implement governance policies, or clean up analytical assets"""
        try:
            result = await client.api_call(
                "PUT",
                f"/api/{item_type}/{item_id}",
                {"collection_id": collection_id},
            )
            return json.dumps(result, indent=2)
        except Exception as e:
            raise RuntimeError(
                f"Failed to move {item_type} {item_id} to collection {collection_id}: {e}"
            ) from e

    # ── search_content ──────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def search_content(
        q: Annotated[str, Field(description="Search query")],
        type: Annotated[
            str | None,
            Field(
                default=None,
                description="Filter by type (card, dashboard, collection, table, etc.)",
            ),
        ] = None,
        models: Annotated[
            list[str] | None,
            Field(default=None, description="Filter by model types"),
        ] = None,
        archived: Annotated[
            bool | None,
            Field(default=None, description="Include archived items"),
        ] = None,
        table_db_id: Annotated[
            int | None,
            Field(default=None, description="Filter by database ID"),
        ] = None,
        limit: Annotated[
            int | None,
            Field(default=None, description="Maximum number of results"),
        ] = None,
    ) -> str:
        """Search across all Metabase content including cards, dashboards, collections, and models - use this to find specific content, discover assets, or explore analytical resources"""
        try:
            params: dict[str, Any] = {"q": q}
            if type is not None:
                params["type"] = type
            if models is not None:
                params["models"] = models
            if archived is not None:
                params["archived"] = str(archived).lower()
            if table_db_id is not None:
                params["table_db_id"] = table_db_id
            if limit is not None:
                params["limit"] = limit
            url = f"/api/search?{urlencode(params, doseq=True)}"
            result = await client.api_call("GET", url)
            return json.dumps(result, indent=2)
        except Exception as e:
            raise RuntimeError(f"Failed to search content: {e}") from e

    # ── list_collections ────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def list_collections(
        archived: Annotated[
            bool,
            Field(default=False, description="Include archived collections"),
        ] = False,
    ) -> str:
        """Retrieve all Metabase collections for organizing analytical content - use this to understand content structure, find collections, or explore organizational hierarchy"""
        try:
            collections = await client.get_collections(archived)
            return json.dumps(collections, indent=2)
        except Exception as e:
            raise RuntimeError(f"Failed to fetch collections: {e}") from e

    # ── create_collection ───────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False))
    async def create_collection(
        name: Annotated[str, Field(description="Name of the collection (required)")],
        description: Annotated[
            str | None,
            Field(default=None, description="Description of the collection"),
        ] = None,
        parent_id: Annotated[
            int | None,
            Field(
                default=None,
                description="Parent collection ID for nested organization",
            ),
        ] = None,
        color: Annotated[
            str | None,
            Field(default=None, description="Color for the collection (hex code)"),
        ] = None,
    ) -> str:
        """Create a new Metabase collection for organizing analytical content - use this to establish organizational containers for cards, dashboards, and reports"""
        try:
            payload: dict[str, Any] = {"name": name}
            if description is not None:
                payload["description"] = description
            if parent_id is not None:
                payload["parent_id"] = parent_id
            if color is not None:
                payload["color"] = color
            collection = await client.create_collection(payload)
            return json.dumps(collection, indent=2)
        except Exception as e:
            raise RuntimeError(f"Failed to create collection: {e}") from e

    # ── update_collection ───────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False))
    async def update_collection(
        collection_id: Annotated[
            int, Field(description="The ID of the collection to update")
        ],
        name: Annotated[
            str | None,
            Field(default=None, description="New name for the collection"),
        ] = None,
        description: Annotated[
            str | None,
            Field(default=None, description="New description for the collection"),
        ] = None,
        parent_id: Annotated[
            int | None,
            Field(default=None, description="New parent collection ID"),
        ] = None,
        color: Annotated[
            str | None,
            Field(default=None, description="New color for the collection"),
        ] = None,
    ) -> str:
        """Update collection properties including name, description, and organization - use this to maintain metadata, reorganize hierarchies, or update structure"""
        try:
            updates: dict[str, Any] = {}
            if name is not None:
                updates["name"] = name
            if description is not None:
                updates["description"] = description
            if parent_id is not None:
                updates["parent_id"] = parent_id
            if color is not None:
                updates["color"] = color
            collection = await client.update_collection(collection_id, updates)
            return json.dumps(collection, indent=2)
        except Exception as e:
            raise RuntimeError(
                f"Failed to update collection {collection_id}: {e}"
            ) from e

    # ── delete_collection ───────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True))
    async def delete_collection(
        collection_id: Annotated[
            int, Field(description="The ID of the collection to delete")
        ],
    ) -> str:
        """Permanently delete a Metabase collection - use with caution as this affects contained content and cannot be undone"""
        try:
            await client.delete_collection(collection_id)
            return json.dumps(
                {
                    "collection_id": collection_id,
                    "action": "deleted",
                    "status": "success",
                },
                indent=2,
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to delete collection {collection_id}: {e}"
            ) from e

    # ── list_users ──────────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def list_users(
        include_deactivated: Annotated[
            bool,
            Field(default=False, description="Include deactivated users"),
        ] = False,
    ) -> str:
        """Retrieve all Metabase users with their roles and permissions - use this to understand user access, manage permissions, or audit accounts"""
        try:
            users = await client.get_users(include_deactivated)
            return json.dumps(users, indent=2)
        except Exception as e:
            raise RuntimeError(f"Failed to fetch users: {e}") from e

    # ── get_metabase_playground_link ─────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def get_metabase_playground_link(
        query: Annotated[
            str, Field(description="The SQL query to execute in the playground")
        ],
        display: Annotated[
            str,
            Field(
                default="table",
                description="Display type (table, bar, line, etc.)",
            ),
        ] = "table",
    ) -> str:
        """Generate a Metabase playground link for interactive query exploration - allows users to see results and experiment with data in a user-friendly interface"""
        try:
            payload = {
                "dataset_query": {
                    "type": "native",
                    "native": {
                        "template_tags": {},
                        "query": query,
                    },
                },
                "display": display,
                "parameters": [],
                "visualization_settings": {},
                "type": "question",
            }

            query_b64 = base64.b64encode(
                json.dumps(payload).encode()
            ).decode()

            metabase_url = os.environ.get(
                "METABASE_PLAYGROUND_URL"
            ) or os.environ.get("METABASE_URL")

            if not metabase_url:
                raise ValueError("METABASE_URL environment variable is required")

            playground_url = f"{metabase_url}/question#{query_b64}"

            return json.dumps(
                {
                    "playground_url": playground_url,
                    "query": query,
                    "display": display,
                },
                indent=2,
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to generate playground link: {e}"
            ) from e
