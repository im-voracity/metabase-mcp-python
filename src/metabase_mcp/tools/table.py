"""MCP tools for Metabase table operations."""

from __future__ import annotations

import json
from typing import Annotated, Any

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from metabase_mcp.client import MetabaseClient


def register_table_tools(mcp: FastMCP, client: MetabaseClient) -> None:
    """Register all table-related MCP tools."""

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def list_tables(
        ids: Annotated[
            list[int] | None,
            Field(description="Optional list of table IDs to filter by"),
        ] = None,
    ) -> str:
        """Retrieve all Metabase tables with optional ID filtering - use this to discover available tables, explore database schema, or get metadata about specific tables."""
        try:
            result = await client.get_tables(ids)
            return json.dumps(result, indent=2)
        except Exception as e:
            raise RuntimeError(f"Failed to list tables: {e}") from e

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False),
    )
    async def update_tables(
        ids: Annotated[
            list[int],
            Field(description="IDs of tables to update"),
        ],
        display_name: Annotated[
            str | None,
            Field(description="New display name for the tables", min_length=1),
        ] = None,
        description: Annotated[
            str | None,
            Field(description="New description"),
        ] = None,
        caveats: Annotated[
            str | None,
            Field(description="Caveats"),
        ] = None,
        points_of_interest: Annotated[
            str | None,
            Field(description="Points of interest"),
        ] = None,
        visibility_type: Annotated[
            str | None,
            Field(description="Table visibility type"),
        ] = None,
        data_authority: Annotated[
            Any | None,
            Field(description="Data authority settings (see Metabase OpenAPI spec)"),
        ] = None,
        data_layer: Annotated[
            str | None,
            Field(description="Data layer"),
        ] = None,
        data_source: Annotated[
            str | None,
            Field(description="Data source"),
        ] = None,
        owner_email: Annotated[
            str | None,
            Field(description="Owner email"),
        ] = None,
        owner_user_id: Annotated[
            int | None,
            Field(description="Owner user ID"),
        ] = None,
        show_in_getting_started: Annotated[
            bool | None,
            Field(description="Show table in getting started"),
        ] = None,
        entity_type: Annotated[
            str | None,
            Field(description="Entity type"),
        ] = None,
    ) -> str:
        """Bulk update multiple Metabase tables with same configuration - use this to apply consistent settings, update metadata, or modify table properties efficiently."""
        try:
            updates: dict[str, Any] = {}
            if display_name is not None:
                updates["display_name"] = display_name
            if description is not None:
                updates["description"] = description
            if caveats is not None:
                updates["caveats"] = caveats
            if points_of_interest is not None:
                updates["points_of_interest"] = points_of_interest
            if visibility_type is not None:
                updates["visibility_type"] = visibility_type
            if data_authority is not None:
                updates["data_authority"] = data_authority
            if data_layer is not None:
                updates["data_layer"] = data_layer
            if data_source is not None:
                updates["data_source"] = data_source
            if owner_email is not None:
                updates["owner_email"] = owner_email
            if owner_user_id is not None:
                updates["owner_user_id"] = owner_user_id
            if show_in_getting_started is not None:
                updates["show_in_getting_started"] = show_in_getting_started
            if entity_type is not None:
                updates["entity_type"] = entity_type
            result = await client.update_tables(ids, updates)
            return json.dumps(result, indent=2)
        except Exception as e:
            raise RuntimeError(f"Failed to bulk update tables: {e}") from e

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def get_table(
        table_id: Annotated[int, Field(description="Table ID")],
        include_sensitive_fields: Annotated[
            bool | None,
            Field(description="Include sensitive fields"),
        ] = None,
        include_hidden_fields: Annotated[
            bool | None,
            Field(description="Include hidden fields"),
        ] = None,
        include_editable_data_model: Annotated[
            bool | None,
            Field(description="Include editable data model"),
        ] = None,
    ) -> str:
        """Retrieve comprehensive table information including schema, fields, and metadata - use this to understand structure, explore fields, or get configuration details."""
        try:
            result = await client.get_table(
                table_id,
                include_sensitive_fields=include_sensitive_fields,
                include_hidden_fields=include_hidden_fields,
                include_editable_data_model=include_editable_data_model,
            )
            return json.dumps(result, indent=2)
        except Exception as e:
            raise RuntimeError(f"Failed to get table {table_id}: {e}") from e

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False),
    )
    async def update_table(
        table_id: Annotated[int, Field(description="Table ID")],
        display_name: Annotated[
            str | None,
            Field(description="New display name", min_length=1),
        ] = None,
        description: Annotated[
            str | None,
            Field(description="New description"),
        ] = None,
        caveats: Annotated[
            str | None,
            Field(description="Caveats"),
        ] = None,
        points_of_interest: Annotated[
            str | None,
            Field(description="Points of interest"),
        ] = None,
        visibility_type: Annotated[
            str | None,
            Field(description="Table visibility type"),
        ] = None,
        field_order: Annotated[
            str | None,
            Field(description="Field ordering"),
        ] = None,
        data_authority: Annotated[
            Any | None,
            Field(description="Data authority settings (see Metabase OpenAPI spec)"),
        ] = None,
        data_layer: Annotated[
            str | None,
            Field(description="Data layer"),
        ] = None,
        data_source: Annotated[
            str | None,
            Field(description="Data source"),
        ] = None,
        owner_email: Annotated[
            str | None,
            Field(description="Owner email"),
        ] = None,
        owner_user_id: Annotated[
            int | None,
            Field(description="Owner user ID"),
        ] = None,
        show_in_getting_started: Annotated[
            bool | None,
            Field(description="Show table in getting started"),
        ] = None,
        entity_type: Annotated[
            str | None,
            Field(description="Entity type"),
        ] = None,
    ) -> str:
        """Update table configuration including display name, description, and field settings - use this to customize presentation, update metadata, or configure data model."""
        try:
            updates: dict[str, Any] = {}
            if display_name is not None:
                updates["display_name"] = display_name
            if description is not None:
                updates["description"] = description
            if caveats is not None:
                updates["caveats"] = caveats
            if points_of_interest is not None:
                updates["points_of_interest"] = points_of_interest
            if visibility_type is not None:
                updates["visibility_type"] = visibility_type
            if field_order is not None:
                updates["field_order"] = field_order
            if data_authority is not None:
                updates["data_authority"] = data_authority
            if data_layer is not None:
                updates["data_layer"] = data_layer
            if data_source is not None:
                updates["data_source"] = data_source
            if owner_email is not None:
                updates["owner_email"] = owner_email
            if owner_user_id is not None:
                updates["owner_user_id"] = owner_user_id
            if show_in_getting_started is not None:
                updates["show_in_getting_started"] = show_in_getting_started
            if entity_type is not None:
                updates["entity_type"] = entity_type
            result = await client.update_table(table_id, updates)
            return json.dumps(result, indent=2)
        except Exception as e:
            raise RuntimeError(f"Failed to update table {table_id}: {e}") from e

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def get_table_fks(
        table_id: Annotated[int, Field(description="Table ID")],
    ) -> str:
        """Retrieve foreign key relationships for a table - use this to understand data connections, build joins, or explore table dependencies."""
        try:
            result = await client.get_table_fks(table_id)
            return json.dumps(result, indent=2)
        except Exception as e:
            raise RuntimeError(
                f"Failed to get FKs for table {table_id}: {e}"
            ) from e

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def get_table_query_metadata(
        table_id: Annotated[int, Field(description="Table ID")],
        include_sensitive_fields: Annotated[
            bool | None,
            Field(description="Include sensitive fields"),
        ] = None,
        include_hidden_fields: Annotated[
            bool | None,
            Field(description="Include hidden fields"),
        ] = None,
        include_editable_data_model: Annotated[
            bool | None,
            Field(description="Include editable data model"),
        ] = None,
    ) -> str:
        """Retrieve query-optimized table metadata for building dynamic queries - use this when constructing queries or building query interfaces."""
        try:
            result = await client.get_table_query_metadata(
                table_id,
                include_sensitive_fields=include_sensitive_fields,
                include_hidden_fields=include_hidden_fields,
                include_editable_data_model=include_editable_data_model,
            )
            return json.dumps(result, indent=2)
        except Exception as e:
            raise RuntimeError(
                f"Failed to get query metadata for table {table_id}: {e}"
            ) from e

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def get_table_related(
        table_id: Annotated[int, Field(description="Table ID")],
    ) -> str:
        """Find tables and entities related through relationships or schemas - use this to discover connected data, find related content, or understand context."""
        try:
            result = await client.get_table_related(table_id)
            return json.dumps(result, indent=2)
        except Exception as e:
            raise RuntimeError(
                f"Failed to get related entities for table {table_id}: {e}"
            ) from e

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def get_card_table_fks(
        card_id: Annotated[int, Field(description="Card ID for the virtual table")],
    ) -> str:
        """Retrieve foreign keys for a card's virtual table - use this to understand relationships in card-based queries or saved question tables."""
        try:
            result = await client.get_card_table_fks(card_id)
            return json.dumps(result, indent=2)
        except Exception as e:
            raise RuntimeError(
                f"Failed to get FKs for card table card__{card_id}: {e}"
            ) from e

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def get_card_table_query_metadata(
        card_id: Annotated[int, Field(description="Card ID for the virtual table")],
    ) -> str:
        """Retrieve query metadata for a card's virtual table - use this to build queries on top of saved questions or treat cards as queryable tables."""
        try:
            result = await client.get_card_table_query_metadata(card_id)
            return json.dumps(result, indent=2)
        except Exception as e:
            raise RuntimeError(
                f"Failed to get query metadata for card table card__{card_id}: {e}"
            ) from e

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False),
    )
    async def append_csv_to_table(
        table_id: Annotated[int, Field(description="Table ID")],
        filename: Annotated[str, Field(description="CSV filename (for metadata only)")],
        file_content: Annotated[str, Field(description="CSV file content as string")],
    ) -> str:
        """Add new rows from CSV content to existing table - use this for incremental data loading, updates, or importing additional records."""
        try:
            result = await client.append_csv_to_table(
                table_id, filename, file_content
            )
            return json.dumps(result, indent=2)
        except Exception as e:
            raise RuntimeError(
                f"Failed to append CSV to table {table_id}: {e}"
            ) from e

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
    )
    async def discard_table_field_values(
        table_id: Annotated[int, Field(description="Table ID")],
    ) -> str:
        """Clear cached field values to force fresh data loading - use this when table data has changed or cached values are stale."""
        try:
            result = await client.discard_table_field_values(table_id)
            return json.dumps(result, indent=2)
        except Exception as e:
            raise RuntimeError(
                f"Failed to discard values for table {table_id}: {e}"
            ) from e

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False),
    )
    async def reorder_table_fields(
        table_id: Annotated[int, Field(description="Table ID")],
        field_order: Annotated[
            list[int],
            Field(description="Array of field IDs in desired order"),
        ],
    ) -> str:
        """Change display order of table fields for better organization - use this to arrange fields logically, group columns, or improve presentation."""
        try:
            result = await client.reorder_table_fields(table_id, field_order)
            return json.dumps(result, indent=2)
        except Exception as e:
            raise RuntimeError(
                f"Failed to reorder fields for table {table_id}: {e}"
            ) from e

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
    )
    async def replace_table_csv(
        table_id: Annotated[int, Field(description="Table ID")],
        csv_file: Annotated[str, Field(description="CSV file content as string")],
    ) -> str:
        """Completely replace table data with new CSV content - use this for full data refreshes, model updates, or complete table replacements."""
        try:
            result = await client.replace_table_csv(table_id, csv_file)
            return json.dumps(result, indent=2)
        except Exception as e:
            raise RuntimeError(
                f"Failed to replace CSV for table {table_id}: {e}"
            ) from e

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False),
    )
    async def rescan_table_field_values(
        table_id: Annotated[int, Field(description="Table ID")],
    ) -> str:
        """Trigger rescan to refresh field values cache with current data - use this to update dropdown options, statistics, or filter values."""
        try:
            result = await client.rescan_table_field_values(table_id)
            return json.dumps(result, indent=2)
        except Exception as e:
            raise RuntimeError(
                f"Failed to rescan values for table {table_id}: {e}"
            ) from e

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False),
    )
    async def sync_table_schema(
        table_id: Annotated[int, Field(description="Table ID")],
    ) -> str:
        """Initiate schema sync for specific table to update metadata - use this when table structure has changed and needs recognition."""
        try:
            result = await client.sync_table_schema(table_id)
            return json.dumps(
                {
                    "table_id": table_id,
                    "status": "schema_sync_triggered",
                    "result": result,
                },
                indent=2,
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to sync schema for table {table_id}: {e}"
            ) from e

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def get_table_data(
        table_id: Annotated[int, Field(description="Table ID")],
        limit: Annotated[
            int | None,
            Field(description="Row limit (default 1000)"),
        ] = None,
    ) -> str:
        """Retrieve sample data from table for preview and analysis - use this to examine content, verify quality, or understand data patterns."""
        try:
            result = await client.get_table_data(
                table_id, limit if limit is not None else 1000
            )
            return json.dumps(result, indent=2)
        except Exception as e:
            raise RuntimeError(
                f"Failed to fetch data for table {table_id}: {e}"
            ) from e

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def get_field_id(
        table_id: Annotated[int, Field(description="Table ID to search in")],
        column_name: Annotated[
            str,
            Field(
                description="Column name to look up (searches both name and display_name)"
            ),
        ],
    ) -> str:
        """Look up a field's ID and metadata by table and column name - essential for building parameter mappings. Returns field_id, base_type, and other metadata needed for filter connections."""
        try:
            result = await client.get_field_by_name(table_id, column_name)
            return json.dumps(result, indent=2)
        except Exception as e:
            raise RuntimeError(
                f"Failed to find field '{column_name}' in table {table_id}: {e}"
            ) from e
