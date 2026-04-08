"""MCP tools for Metabase card (saved question) operations."""

from __future__ import annotations

import json
from typing import Annotated, Any

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import BeforeValidator, Field

from metabase_mcp.client import MetabaseClient
from metabase_mcp.validators import JsonParsed, parse_if_string


def register_card_tools(mcp: FastMCP, client: MetabaseClient) -> None:
    """Register all card-related MCP tools."""

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def list_cards(
        f: Annotated[str | None, Field(description="Filter by source (e.g., 'models')")] = None,
        model_id: Annotated[int | None, Field(description="Filter by model_id")] = None,
    ) -> str:
        """Retrieve all Metabase cards with optional filtering by source type (e.g., 'models') or model relationships - use this to discover available cards, find specific cards by type, or get an overview of all analytical content"""
        result = await client.get_cards(f=f, model_id=model_id)
        return json.dumps(result, indent=2)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def get_card(
        card_id: Annotated[int, Field(description="Card ID")],
    ) -> str:
        """Get complete metadata and configuration for a specific Metabase card including query definition, visualization settings, collection location, and permissions - use this when you need to examine or understand how a particular card is built"""
        result = await client.get_card(card_id)
        return json.dumps(result, indent=2)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False))
    async def create_card(
        name: Annotated[str, Field(description="Card name")],
        description: Annotated[str | None, Field(description="Description")] = None,
        dataset_query: Annotated[Any | None, BeforeValidator(parse_if_string), Field(description="Dataset query object - fully preserved including nested MBQL arrays")] = None,
        display: Annotated[str | None, Field(description="Visualization type")] = None,
        visualization_settings: Annotated[Any | None, BeforeValidator(parse_if_string), Field(description="Visualization settings")] = None,
        collection_id: Annotated[int | None, Field(description="Collection to save in")] = None,
        database_id: Annotated[int | None, Field(description="Database ID")] = None,
    ) -> str:
        """Create a new Metabase card with custom query, visualization type, and settings - use this to programmatically build new analytical cards, dashboards charts, or data exploration queries"""
        card_data: dict[str, Any] = {"name": name}
        if description is not None:
            card_data["description"] = description
        if dataset_query is not None:
            card_data["dataset_query"] = dataset_query
        if display is not None:
            card_data["display"] = display
        if visualization_settings is not None:
            card_data["visualization_settings"] = visualization_settings
        if collection_id is not None:
            card_data["collection_id"] = collection_id
        if database_id is not None:
            card_data["database_id"] = database_id
        result = await client.create_card(card_data)
        return json.dumps(result, indent=2)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False))
    async def update_card(
        card_id: Annotated[int, Field(description="Card ID")],
        updates: Annotated[JsonParsed, Field(description="Fields to update")],
        query_params: Annotated[JsonParsed | None, Field(description="Optional query parameters for update")] = None,
    ) -> str:
        """Modify an existing Metabase card's name, description, query definition, visualization type, or settings - use this to fix broken cards, change chart types, update queries, or move cards between collections"""
        result = await client.update_card(card_id, updates, query_params)
        return json.dumps(result, indent=2)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True))
    async def delete_card(
        card_id: Annotated[int, Field(description="Card ID")],
        hard_delete: Annotated[bool, Field(description="Hard delete if true, else archive")] = False,
    ) -> str:
        """Remove a Metabase card either by archiving (soft delete, preserves history) or permanent deletion - use this to clean up unused cards, remove broken cards, or organize analytical content"""
        await client.delete_card(card_id, hard_delete)
        return json.dumps(
            {
                "card_id": card_id,
                "action": "deleted" if hard_delete else "archived",
                "status": "success",
            },
            indent=2,
        )

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def execute_card(
        card_id: Annotated[int, Field(description="Card ID")],
        ignore_cache: Annotated[bool | None, Field(description="Ignore cached results")] = None,
        collection_preview: Annotated[bool | None, Field(description="Collection preview flag")] = None,
        dashboard_id: Annotated[int | None, Field(description="Execute within a dashboard context")] = None,
    ) -> str:
        """Run a Metabase card query and return the actual data results - use this to get current data from existing cards, refresh analytical insights, or programmatically access query results for further processing"""
        result = await client.execute_card(
            card_id,
            ignore_cache=ignore_cache or False,
            collection_preview=collection_preview,
            dashboard_id=dashboard_id,
        )
        return json.dumps(result, indent=2)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def export_card_result(
        card_id: Annotated[int, Field(description="Card ID")],
        export_format: Annotated[str, Field(description="Export format (e.g., csv, xlsx, json)")],
        parameters: Annotated[JsonParsed | None, Field(description="Execution parameters")] = None,
    ) -> str:
        """Execute a Metabase card and export the results in a specific format (CSV, Excel, JSON, etc.) - use this to download data for external analysis, create reports for stakeholders, or integrate query results with other systems"""
        result = await client.execute_card_query_with_format(
            card_id, export_format, parameters or {}
        )
        return json.dumps(result, indent=2)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False))
    async def copy_card(
        card_id: Annotated[int, Field(description="Card ID")],
    ) -> str:
        """Create a duplicate copy of an existing Metabase card with identical query and settings - use this to create variations of existing cards, build templates for similar analyses, or backup important queries before modifications"""
        result = await client.copy_card(card_id)
        return json.dumps(result, indent=2)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def get_card_dashboards(
        card_id: Annotated[int, Field(description="Card ID")],
    ) -> str:
        """Find all dashboards that include a specific Metabase card - use this to understand where a card is being used, track dependencies before making changes, or find related analytical content"""
        result = await client.get_card_dashboards(card_id)
        return json.dumps(result, indent=2)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def list_embeddable_cards() -> str:
        """Retrieve all Metabase cards configured for embedding in external applications (requires admin privileges) - use this to audit embedded content, manage external integrations, or review public-facing analytics"""
        result = await client.get_embeddable_cards()
        return json.dumps(result, indent=2)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False))
    async def create_card_public_link(
        card_id: Annotated[int, Field(description="Card ID")],
    ) -> str:
        """Generate a publicly accessible URL for a Metabase card that can be viewed without authentication (requires admin privileges) - use this to share analytical insights with external stakeholders, create public reports, or embed charts in websites"""
        result = await client.create_card_public_link(card_id)
        return json.dumps(result, indent=2)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True))
    async def delete_card_public_link(
        card_id: Annotated[int, Field(description="Card ID")],
    ) -> str:
        """Remove public access to a Metabase card by deleting its public URL (requires admin privileges) - use this to revoke external access to sensitive data, clean up unused public links, or update security permissions"""
        result = await client.delete_card_public_link(card_id)
        return json.dumps(result, indent=2)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def list_public_cards() -> str:
        """Retrieve all Metabase cards that have public URLs enabled (requires admin privileges) - use this to audit publicly accessible content, review security settings, or manage external data sharing"""
        result = await client.get_public_cards()
        return json.dumps(result, indent=2)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False))
    async def move_cards(
        card_ids: Annotated[list[int], Field(description="Card IDs to move")],
        collection_id: Annotated[int | None, Field(description="Target collection ID")] = None,
        dashboard_id: Annotated[int | None, Field(description="Target dashboard ID")] = None,
    ) -> str:
        """Relocate multiple Metabase cards to a different collection or dashboard for better organization - use this to reorganize analytical content, group related cards, or clean up workspace structure"""
        result = await client.move_cards(card_ids, collection_id, dashboard_id)
        return json.dumps(result, indent=2)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False))
    async def move_cards_to_collection(
        card_ids: Annotated[list[int], Field(description="Card IDs to move")],
        collection_id: Annotated[int | None, Field(description="Target collection ID")] = None,
    ) -> str:
        """Bulk transfer multiple Metabase cards to a specific collection for organizational purposes - use this to categorize cards by team, project, or topic, or to implement content governance policies"""
        result = await client.move_cards_to_collection(card_ids, collection_id)
        return json.dumps(result, indent=2)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def execute_pivot_card_query(
        card_id: Annotated[int, Field(description="Card ID")],
        parameters: Annotated[JsonParsed | None, Field(description="Execution parameters")] = None,
    ) -> str:
        """Run a Metabase card with pivot table formatting to cross-tabulate data with rows and columns - use this to create summary tables, analyze data relationships, or generate matrix-style reports from existing cards"""
        result = await client.execute_pivot_card_query(card_id, parameters or {})
        return json.dumps(result, indent=2)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def get_card_param_values(
        card_id: Annotated[int, Field(description="Card ID")],
        param_key: Annotated[str, Field(description="Parameter key")],
    ) -> str:
        """Retrieve all available values for a specific parameter in a Metabase card - use this to populate dropdown filters, validate parameter inputs, or understand what data options are available for interactive cards"""
        result = await client.get_card_param_values(card_id, param_key)
        return json.dumps(result, indent=2)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def search_card_param_values(
        card_id: Annotated[int, Field(description="Card ID")],
        param_key: Annotated[str, Field(description="Parameter key")],
        query: Annotated[str, Field(description="Search query")],
    ) -> str:
        """Search and filter available parameter values for a Metabase card using a text query - use this to find specific parameter options in large datasets, help users locate filter values, or implement autocomplete functionality"""
        result = await client.search_card_param_values(card_id, param_key, query)
        return json.dumps(result, indent=2)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def get_card_param_remapping(
        card_id: Annotated[int, Field(description="Card ID")],
        param_key: Annotated[str, Field(description="Parameter key")],
        value: Annotated[str, Field(description="Parameter value to remap")],
    ) -> str:
        """Retrieve how parameter values are remapped or transformed for display in a Metabase card - use this to understand data transformations, debug parameter issues, or see how raw values are presented to users"""
        result = await client.get_card_param_remapping(card_id, param_key, value)
        return json.dumps(result, indent=2)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def get_card_query_metadata(
        card_id: Annotated[int, Field(description="Card ID")],
    ) -> str:
        """Retrieve structural metadata about a Metabase card's underlying query including column types, field information, and data schema - use this to understand card structure, validate data types, or build dynamic interfaces"""
        result = await client.get_card_query_metadata(card_id)
        return json.dumps(result, indent=2)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def get_card_series(
        card_id: Annotated[int, Field(description="Card ID")],
        last_cursor: Annotated[str | int | None, Field(description="Pagination cursor")] = None,
        query: Annotated[str | None, Field(description="Filter query")] = None,
        exclude_ids: Annotated[list[int] | None, Field(description="IDs to exclude")] = None,
    ) -> str:
        """Retrieve time series data or related card suggestions for a Metabase card - use this to get chronological data trends, find similar cards, or discover related analytical content for dashboard building"""
        result = await client.get_card_series(
            card_id,
            last_cursor=last_cursor,
            query=query,
            exclude_ids=exclude_ids,
        )
        return json.dumps(result, indent=2)
