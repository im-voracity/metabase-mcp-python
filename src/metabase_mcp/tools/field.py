"""MCP tools for Metabase field operations."""

from __future__ import annotations

import json
from typing import Annotated, Any

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import BeforeValidator, Field

from metabase_mcp.client import MetabaseClient
from metabase_mcp.validators import parse_if_string


def register_field_tools(mcp: FastMCP, client: MetabaseClient) -> None:
    """Register all field-related MCP tools."""

    # ── Read tools ──────────────────────────────────────────────────────

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def get_field(
        field_id: Annotated[int, Field(description="The ID of the field")],
    ) -> str:
        """Get detailed information about a specific field including type, semantic type, and display settings"""
        result = await client.get_field(field_id)
        return json.dumps(result, indent=2)

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def get_field_values(
        field_id: Annotated[int, Field(description="The ID of the field")],
    ) -> str:
        """Get distinct values for a field - use this to understand value distributions or populate filter options"""
        result = await client.get_field_values(field_id)
        return json.dumps(result, indent=2)

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def get_field_summary(
        field_id: Annotated[int, Field(description="The ID of the field")],
    ) -> str:
        """Get a summary of field value distribution (count and distinct count) - use for quick data profiling"""
        result = await client.get_field_summary(field_id)
        return json.dumps(result, indent=2)

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def search_field_values(
        field_id: Annotated[int, Field(description="The ID of the field to search")],
        search_field_id: Annotated[
            int,
            Field(description="The ID of the field to search against (for remapped fields)"),
        ],
    ) -> str:
        """Search field values using a related field - use for remapped or foreign key lookups"""
        result = await client.search_field_values(field_id, search_field_id)
        return json.dumps(result, indent=2)

    # ── Write tools ─────────────────────────────────────────────────────

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False),
    )
    async def update_field(
        field_id: Annotated[int, Field(description="The ID of the field to update")],
        display_name: Annotated[
            str | None,
            Field(description="New display name for the field"),
        ] = None,
        description: Annotated[
            str | None,
            Field(description="New description for the field"),
        ] = None,
        semantic_type: Annotated[
            str | None,
            Field(description="Semantic type (e.g. 'type/Category', 'type/Email', 'type/FK')"),
        ] = None,
        visibility_type: Annotated[
            str | None,
            Field(description="Visibility: 'normal', 'details-only', 'hidden', or 'sensitive'"),
        ] = None,
        has_field_values: Annotated[
            str | None,
            Field(description="How to fetch values: 'none', 'list', 'search', or 'auto-list'"),
        ] = None,
        settings: Annotated[
            dict[str, Any] | None,
            BeforeValidator(parse_if_string),
            Field(description="Custom field settings as JSON"),
        ] = None,
    ) -> str:
        """Update field properties like display name, description, semantic type, or visibility - use to customize how a field appears and behaves in Metabase"""
        updates: dict[str, Any] = {}
        if display_name is not None:
            updates["display_name"] = display_name
        if description is not None:
            updates["description"] = description
        if semantic_type is not None:
            updates["semantic_type"] = semantic_type
        if visibility_type is not None:
            updates["visibility_type"] = visibility_type
        if has_field_values is not None:
            updates["has_field_values"] = has_field_values
        if settings is not None:
            updates["settings"] = settings
        result = await client.update_field(field_id, updates)
        return json.dumps(result, indent=2)

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False),
    )
    async def rescan_field_values(
        field_id: Annotated[int, Field(description="The ID of the field")],
    ) -> str:
        """Trigger a rescan of cached field values - use after data changes to refresh filter options"""
        await client.rescan_field_values(field_id)
        return json.dumps(
            {"field_id": field_id, "action": "rescan_triggered", "status": "success"},
            indent=2,
        )

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False),
    )
    async def discard_field_values(
        field_id: Annotated[int, Field(description="The ID of the field")],
    ) -> str:
        """Discard cached field values - use to clear stale cached data for a field"""
        await client.discard_field_values(field_id)
        return json.dumps(
            {"field_id": field_id, "action": "values_discarded", "status": "success"},
            indent=2,
        )
