"""MCP tools for Metabase bookmark operations."""

from __future__ import annotations

import json
from typing import Annotated, Any

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import BeforeValidator, Field

from metabase_mcp.client import MetabaseClient
from metabase_mcp.validators import parse_if_string


def register_bookmark_tools(mcp: FastMCP, client: MetabaseClient) -> None:
    """Register all bookmark-related MCP tools."""

    # ── Read tools ──────────────────────────────────────────────────────

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def list_bookmarks() -> str:
        """List all bookmarks for the current user - use this to see saved/favorited items"""
        result = await client.get_bookmarks()
        return json.dumps(result, indent=2)

    # ── Write tools ─────────────────────────────────────────────────────

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False),
    )
    async def create_bookmark(
        model: Annotated[
            str,
            Field(description="Type of item to bookmark: 'card', 'dashboard', or 'collection'"),
        ],
        model_id: Annotated[int, Field(description="The ID of the item to bookmark")],
    ) -> str:
        """Bookmark a card, dashboard, or collection for quick access"""
        result = await client.create_bookmark(model, model_id)
        return json.dumps(result, indent=2)

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
    )
    async def delete_bookmark(
        model: Annotated[
            str,
            Field(description="Type of bookmarked item: 'card', 'dashboard', or 'collection'"),
        ],
        model_id: Annotated[int, Field(description="The ID of the bookmarked item")],
    ) -> str:
        """Remove a bookmark from a card, dashboard, or collection"""
        await client.delete_bookmark(model, model_id)
        return json.dumps(
            {"model": model, "model_id": model_id, "action": "deleted", "status": "success"},
            indent=2,
        )

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False),
    )
    async def reorder_bookmarks(
        orderings: Annotated[
            list[dict[str, Any]],
            BeforeValidator(parse_if_string),
            Field(description="List of bookmark ordering objects with 'type' and 'item_id' keys"),
        ],
    ) -> str:
        """Reorder bookmarks - provide the full list in desired order"""
        await client.reorder_bookmarks(orderings)
        return json.dumps(
            {"action": "reordered", "status": "success"},
            indent=2,
        )
