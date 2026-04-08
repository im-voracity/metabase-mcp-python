"""MCP tools for Metabase dashboard operations."""

from __future__ import annotations

import json
from typing import Annotated, Any

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import BeforeValidator, Field

from metabase_mcp.client import MetabaseClient
from metabase_mcp.validators import JsonParsed, parse_if_string


def register_dashboard_tools(mcp: FastMCP, client: MetabaseClient) -> None:
    """Register all dashboard-related MCP tools."""

    # ── Read tools ──────────────────────────────────────────────────────

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def list_dashboards() -> str:
        """Retrieve all Metabase dashboards - use this to discover available dashboards, get an overview of analytical content, or find specific dashboards"""
        result = await client.get_dashboards()
        return json.dumps(result, indent=2)

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def get_dashboard(
        dashboard_id: Annotated[int, Field(description="The ID of the dashboard to retrieve")],
    ) -> str:
        """Retrieve detailed information about a specific Metabase dashboard including cards, layout, and settings - use this to examine dashboard structure or get configuration details"""
        result = await client.get_dashboard(dashboard_id)
        return json.dumps(result, indent=2)

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def get_dashboard_cards(
        dashboard_id: Annotated[int, Field(description="The ID of the dashboard")],
    ) -> str:
        """Retrieve all cards within a specific Metabase dashboard - use this to analyze dashboard content, understand data sources, or examine card configurations"""
        dashboard = await client.get_dashboard(dashboard_id)
        cards = dashboard.get("dashcards", []) if isinstance(dashboard, dict) else []
        return json.dumps(cards, indent=2)

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def get_dashboard_related(
        dashboard_id: Annotated[int, Field(description="The ID of the dashboard")],
    ) -> str:
        """Retrieve entities related to a Metabase dashboard - use this to discover related content, find similar analytical views, or understand dashboard relationships"""
        result = await client.get_dashboard_related(dashboard_id)
        return json.dumps(result, indent=2)

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def get_dashboard_revisions(
        dashboard_id: Annotated[int, Field(description="The ID of the dashboard")],
    ) -> str:
        """Retrieve revision history for a Metabase dashboard - use this to track dashboard evolution, review past changes, or restore previous versions"""
        result = await client.get_dashboard_revisions(dashboard_id)
        return json.dumps(result, indent=2)

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def list_embeddable_dashboards() -> str:
        """Retrieve all Metabase dashboards configured for embedding (requires superuser) - use this to audit embedded content or manage external integrations"""
        result = await client.get_embeddable_dashboards()
        return json.dumps(result, indent=2)

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def list_public_dashboards() -> str:
        """Retrieve all Metabase dashboards with public URLs enabled (requires superuser) - use this to audit publicly accessible content or review security settings"""
        result = await client.get_public_dashboards()
        return json.dumps(result, indent=2)

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def search_dashboards(
        query: Annotated[str, Field(description="Search query string")],
        limit: Annotated[int | None, Field(description="Maximum number of results to return")] = None,
    ) -> str:
        """Search dashboards by name or description text - use this to find specific dashboards or discover related analytical content"""
        dashboards = await client.get_dashboards()
        lower_q = query.lower()
        filtered = [
            d
            for d in dashboards
            if (d.get("name") or "").lower().find(lower_q) != -1
            or (d.get("description") or "").lower().find(lower_q) != -1
        ]
        if limit is not None:
            filtered = filtered[:limit]
        return json.dumps(filtered, indent=2)

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def execute_dashboard_card(
        dashboard_id: Annotated[int, Field(description="The ID of the dashboard containing the card")],
        card_id: Annotated[int, Field(description="The ID of the card to execute")],
    ) -> str:
        """Execute a specific card from a dashboard and retrieve fresh data - use this to get current results from dashboard components or test card functionality"""
        result = await client.execute_card(card_id)
        return json.dumps(
            {
                "dashboard_id": dashboard_id,
                "card_id": card_id,
                "status": "completed",
                "data": result,
            },
            indent=2,
        )

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def get_dashboard_queries(
        dashboard_id: Annotated[int, Field(description="The ID of the dashboard")],
    ) -> str:
        """Extract all queries from a dashboard with IDs resolved to actual table/column names - use this to understand dashboard data sources, audit queries, or plan migrations"""
        dashboard = await client.get_dashboard(dashboard_id)
        dashcards = dashboard.get("dashcards", []) if isinstance(dashboard, dict) else []
        tabs = dashboard.get("tabs", []) if isinstance(dashboard, dict) else []

        # Build tab lookup
        tab_lookup: dict[int, str] = {t["id"]: t["name"] for t in tabs}

        # Collect all unique table IDs we need to resolve
        table_ids: set[int] = set()
        for dc in dashcards:
            card = dc.get("card") or {}
            query = (card.get("dataset_query") or {}).get("query") or {}
            src = query.get("source-table")
            if isinstance(src, int):
                table_ids.add(src)
            for j in query.get("joins") or []:
                jsrc = j.get("source-table")
                if isinstance(jsrc, int):
                    table_ids.add(jsrc)

        # Fetch metadata for all tables to resolve field IDs
        table_metadata: dict[int, Any] = {}
        table_names: dict[int, str] = {}
        for tid in table_ids:
            try:
                metadata = await client.get_table_query_metadata(tid)
                table_metadata[tid] = metadata
                schema = metadata.get("schema") or ""
                tname = metadata.get("name") or f"table_{tid}"
                table_names[tid] = f"{schema}.{tname}" if schema else tname
            except Exception:
                table_names[tid] = f"unknown_table_{tid}"

        # Build field ID to name lookup across all tables
        field_lookup: dict[int, dict[str, str]] = {}
        for tid, metadata in table_metadata.items():
            fields = metadata.get("fields") or []
            tname = table_names[tid]
            for f in fields:
                field_lookup[f["id"]] = {"name": f["name"], "table": tname}

        # Helper to resolve field references in MBQL
        def resolve_field_ref(ref: Any) -> Any:
            if not isinstance(ref, list):
                return ref
            if len(ref) >= 2 and ref[0] == "field" and isinstance(ref[1], int):
                info = field_lookup.get(ref[1])
                field_name = info["name"] if info else f"field_{ref[1]}"
                if len(ref) > 2 and isinstance(ref[2], dict):
                    return ["field", field_name, ref[2]]
                return ["field", field_name]
            return [resolve_field_ref(item) for item in ref]

        # Helper to resolve entire MBQL query
        def resolve_mbql(query: dict[str, Any]) -> dict[str, Any]:
            if not query:
                return query
            resolved: dict[str, Any] = {}

            src = query.get("source-table")
            if isinstance(src, int):
                resolved["source-table"] = table_names.get(src, f"table_{src}")

            if query.get("aggregation"):
                resolved["aggregation"] = [resolve_field_ref(a) for a in query["aggregation"]]
            if query.get("breakout"):
                resolved["breakout"] = [resolve_field_ref(b) for b in query["breakout"]]
            if query.get("filter"):
                resolved["filter"] = resolve_field_ref(query["filter"])
            if query.get("order-by"):
                resolved["order-by"] = [resolve_field_ref(o) for o in query["order-by"]]

            if query.get("joins"):
                resolved_joins = []
                for j in query["joins"]:
                    rj = {**j}
                    jsrc = j.get("source-table")
                    if isinstance(jsrc, int):
                        rj["source-table"] = table_names.get(jsrc, f"table_{jsrc}")
                    rj["condition"] = resolve_field_ref(j.get("condition"))
                    resolved_joins.append(rj)
                resolved["joins"] = resolved_joins

            if query.get("fields"):
                resolved["fields"] = [resolve_field_ref(f) for f in query["fields"]]
            if query.get("limit"):
                resolved["limit"] = query["limit"]
            if query.get("expressions"):
                resolved["expressions"] = {
                    name: resolve_field_ref(expr)
                    for name, expr in query["expressions"].items()
                }
            return resolved

        # Process each card
        cards_out = []
        for dc in dashcards:
            card = dc.get("card") or {}
            dataset_query = card.get("dataset_query") or {}
            tab_name = tab_lookup.get(dc.get("dashboard_tab_id")) if dc.get("dashboard_tab_id") else None

            # Virtual/text cards
            if not dc.get("card_id"):
                viz = dc.get("visualization_settings") or {}
                cards_out.append(
                    {
                        "dashcard_id": dc["id"],
                        "card_id": None,
                        "card_name": "(virtual card)",
                        "tab": tab_name,
                        "query_type": "virtual",
                        "text": viz.get("text"),
                    }
                )
                continue

            # Native SQL cards
            if dataset_query.get("type") == "native":
                native = dataset_query.get("native") or {}
                template_tags = native.get("template-tags") or {}
                cards_out.append(
                    {
                        "dashcard_id": dc["id"],
                        "card_id": dc.get("card_id"),
                        "card_name": card.get("name") or "(unnamed)",
                        "tab": tab_name,
                        "query_type": "native",
                        "database_id": dataset_query.get("database"),
                        "sql": native.get("query"),
                        "template_tags": list(template_tags.keys()) if isinstance(template_tags, dict) else [],
                    }
                )
                continue

            # MBQL cards
            q = dataset_query.get("query") or {}
            cards_out.append(
                {
                    "dashcard_id": dc["id"],
                    "card_id": dc.get("card_id"),
                    "card_name": card.get("name") or "(unnamed)",
                    "tab": tab_name,
                    "query_type": "mbql",
                    "database_id": dataset_query.get("database"),
                    "mbql": resolve_mbql(q),
                }
            )

        tables_used = sorted(set(table_names.values()))

        return json.dumps(
            {
                "dashboard_id": dashboard_id,
                "dashboard_name": dashboard.get("name") if isinstance(dashboard, dict) else None,
                "total_cards": len(dashcards),
                "cards": cards_out,
                "tables_used": tables_used,
            },
            indent=2,
        )

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def audit_dashboard_filters(
        dashboard_id: Annotated[int, Field(description="The ID of the dashboard to audit")],
    ) -> str:
        """Analyze dashboard filter connections to find unconnected or misconfigured cards - use this to diagnose filter issues and ensure all cards are properly connected"""
        dashboard = await client.get_dashboard(dashboard_id)
        dashcards = dashboard.get("dashcards", []) if isinstance(dashboard, dict) else []
        parameters = dashboard.get("parameters", []) if isinstance(dashboard, dict) else []

        parameter_ids = [p["id"] for p in parameters]

        card_audit = []
        for dc in dashcards:
            card = dc.get("card") or {}
            mappings = dc.get("parameter_mappings") or []
            connected_params = [m["parameter_id"] for m in mappings]
            missing_params = [pid for pid in parameter_ids if pid not in connected_params]

            errors: list[str] = []
            for m in mappings:
                if not m.get("target"):
                    errors.append(f"Parameter '{m['parameter_id']}' has no target")
                elif isinstance(m["target"], list) and len(m["target"]) > 0 and m["target"][0] == "dimension":
                    has_stage = any(
                        isinstance(t, dict) and "stage-number" in t
                        for t in m["target"]
                    )
                    if not has_stage:
                        errors.append(
                            f"Parameter '{m['parameter_id']}' missing stage-number (MBQL cards require this)"
                        )

            source_table = None
            dq = card.get("dataset_query") or {}
            if dq.get("query", {}).get("source-table"):
                source_table = dq["query"]["source-table"]

            card_audit.append(
                {
                    "dashcard_id": dc["id"],
                    "card_id": dc.get("card_id"),
                    "card_name": card.get("name") or "(virtual card)",
                    "source_table": source_table,
                    "is_native_query": dq.get("type") == "native",
                    "connected_params": connected_params,
                    "missing_params": missing_params,
                    "errors": errors,
                }
            )

        cards_with_issues = [
            c for c in card_audit if c["missing_params"] or c["errors"]
        ]

        return json.dumps(
            {
                "dashboard_id": dashboard_id,
                "total_parameters": len(parameters),
                "parameter_ids": parameter_ids,
                "total_cards": len(dashcards),
                "cards_with_issues": len(cards_with_issues),
                "all_cards": card_audit,
                "cards_needing_attention": cards_with_issues,
            },
            indent=2,
        )

    # ── Write tools ─────────────────────────────────────────────────────

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False),
    )
    async def create_dashboard(
        name: Annotated[str, Field(description="Name of the dashboard (required)")],
        description: Annotated[str | None, Field(description="Description of the dashboard")] = None,
        parameters: Annotated[
            list[Any] | None,
            BeforeValidator(parse_if_string),
            Field(description="Dashboard parameters array"),
        ] = None,
        collection_id: Annotated[int | None, Field(description="Collection ID to save dashboard in")] = None,
        collection_position: Annotated[int | None, Field(description="Position within the collection")] = None,
    ) -> str:
        """Create a new Metabase dashboard - use this to build new analytical views, organize related cards, or establish monitoring interfaces"""
        payload: dict[str, Any] = {"name": name}
        if description is not None:
            payload["description"] = description
        if parameters is not None:
            payload["parameters"] = parameters
        if collection_id is not None:
            payload["collection_id"] = collection_id
        if collection_position is not None:
            payload["collection_position"] = collection_position
        result = await client.create_dashboard(payload)
        return json.dumps(result, indent=2)

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False),
    )
    async def create_public_link(
        dashboard_id: Annotated[int, Field(description="The ID of the dashboard")],
    ) -> str:
        """Generate publicly accessible URL for a dashboard (requires superuser) - use this for external reporting, client dashboards, or public data sharing"""
        result = await client.create_dashboard_public_link(dashboard_id)
        return json.dumps(result, indent=2)

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False),
    )
    async def copy_dashboard(
        from_dashboard_id: Annotated[int, Field(description="The ID of the dashboard to copy")],
        name: Annotated[str | None, Field(description="Name for the new dashboard copy")] = None,
        description: Annotated[str | None, Field(description="Description for the new dashboard copy")] = None,
        collection_id: Annotated[int | None, Field(description="Collection ID for the new dashboard")] = None,
        collection_position: Annotated[int | None, Field(description="Position within the collection")] = None,
    ) -> str:
        """Create a copy of an existing dashboard with all cards and layout - use this to create templates, backups, or variations of analytical views"""
        copy_data: dict[str, Any] = {}
        if name is not None:
            copy_data["name"] = name
        if description is not None:
            copy_data["description"] = description
        if collection_id is not None:
            copy_data["collection_id"] = collection_id
        if collection_position is not None:
            copy_data["collection_position"] = collection_position
        result = await client.copy_dashboard(from_dashboard_id, copy_data or None)
        return json.dumps(result, indent=2)

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False),
    )
    async def add_card_to_dashboard(
        dashboard_id: Annotated[int, Field(description="The ID of the dashboard")],
        cardId: Annotated[int | None, Field(description="The ID of the card to add (null for text/virtual cards)")] = None,
        dashboard_tab_id: Annotated[int | None, Field(description="The tab ID to add the card to (for dashboards with tabs)")] = None,
        row: Annotated[int | None, Field(description="Row position for the card")] = None,
        col: Annotated[int | None, Field(description="Column position for the card")] = None,
        size_x: Annotated[int | None, Field(description="Width of the card")] = None,
        size_y: Annotated[int | None, Field(description="Height of the card")] = None,
        visualization_settings: Annotated[
            dict[str, Any] | None,
            BeforeValidator(parse_if_string),
            Field(description="Visualization settings (required for text cards)"),
        ] = None,
        parameter_mappings: Annotated[
            Any | None,
            BeforeValidator(parse_if_string),
            Field(description="Parameter mappings for the card - connects dashboard filters to card fields"),
        ] = None,
        series: Annotated[
            list[Any] | None,
            BeforeValidator(parse_if_string),
            Field(description="Series data for the card"),
        ] = None,
    ) -> str:
        """Add an existing card to a dashboard with optional parameter mappings - use this to build comprehensive dashboards by combining multiple visualizations"""
        card_data: dict[str, Any] = {}
        if cardId is not None:
            card_data["card_id"] = cardId
        if dashboard_tab_id is not None:
            card_data["dashboard_tab_id"] = dashboard_tab_id
        if row is not None:
            card_data["row"] = row
        if col is not None:
            card_data["col"] = col
        if size_x is not None:
            card_data["size_x"] = size_x
        if size_y is not None:
            card_data["size_y"] = size_y
        if visualization_settings is not None:
            card_data["visualization_settings"] = visualization_settings
        if parameter_mappings is not None:
            card_data["parameter_mappings"] = parameter_mappings
        if series is not None:
            card_data["series"] = series
        result = await client.add_card_to_dashboard(dashboard_id, card_data)
        return json.dumps(result, indent=2)

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False),
    )
    async def add_text_block(
        dashboard_id: Annotated[int, Field(description="The ID of the dashboard")],
        text: Annotated[str, Field(description="The text content (supports Markdown)")],
        display_type: Annotated[str | None, Field(description="Display type: 'heading' for titles, 'text' for body text")] = "text",
        dashboard_tab_id: Annotated[int | None, Field(description="The tab ID to add the text to (for dashboards with tabs)")] = None,
        row: Annotated[int | None, Field(description="Row position")] = 0,
        col: Annotated[int | None, Field(description="Column position")] = 0,
        size_x: Annotated[int | None, Field(description="Width of the text block")] = 18,
        size_y: Annotated[int | None, Field(description="Height of the text block")] = None,
    ) -> str:
        """Add a text block or heading to a dashboard - use this for explanatory text, titles, or instructions"""
        dtype = display_type or "text"
        actual_size_y = size_y if size_y is not None else (1 if dtype == "heading" else 2)

        card_data: dict[str, Any] = {
            "row": row or 0,
            "col": col or 0,
            "size_x": size_x or 18,
            "size_y": actual_size_y,
            "visualization_settings": {
                "virtual_card": {
                    "display": dtype,
                    "visualization_settings": {},
                    "dataset_query": {},
                    "name": None,
                    "archived": False,
                },
                "text": text,
            },
        }
        if dashboard_tab_id is not None:
            card_data["dashboard_tab_id"] = dashboard_tab_id

        result = await client.add_card_to_dashboard(dashboard_id, card_data)
        return json.dumps(result, indent=2)

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False),
    )
    async def favorite_dashboard(
        dashboard_id: Annotated[int, Field(description="The ID of the dashboard")],
    ) -> str:
        """Mark a dashboard as favorite for quick access - use this to bookmark frequently accessed analytical views"""
        result = await client.favorite_dashboard(dashboard_id)
        return json.dumps(result, indent=2)

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False),
    )
    async def revert_dashboard(
        dashboard_id: Annotated[int, Field(description="The ID of the dashboard")],
        revision_id: Annotated[int, Field(description="The revision ID to revert to")],
    ) -> str:
        """Restore a dashboard to a specific previous revision - use this to undo changes, restore deleted content, or return to known good configuration"""
        result = await client.revert_dashboard(dashboard_id, revision_id)
        return json.dumps(result, indent=2)

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False),
    )
    async def save_dashboard(
        dashboard: Annotated[JsonParsed, Field(description="Dashboard object to save")],
    ) -> str:
        """Save a complete dashboard object with nested data - use this for bulk operations or complex dashboard structures"""
        result = await client.save_dashboard(dashboard)
        return json.dumps(result, indent=2)

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False),
    )
    async def save_dashboard_to_collection(
        parent_collection_id: Annotated[int, Field(description="The parent collection ID")],
        dashboard: Annotated[JsonParsed, Field(description="Dashboard object to save")],
    ) -> str:
        """Save a dashboard object directly into a specific collection - use this for organized dashboard creation or bulk imports"""
        result = await client.save_dashboard_to_collection(parent_collection_id, dashboard)
        return json.dumps(result, indent=2)

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False),
    )
    async def update_dashboard(
        dashboard_id: Annotated[int, Field(description="The ID of the dashboard to update")],
        name: Annotated[str | None, Field(description="New name for the dashboard")] = None,
        description: Annotated[str | None, Field(description="New description for the dashboard")] = None,
        parameters: Annotated[
            list[Any] | None,
            BeforeValidator(parse_if_string),
            Field(description="Dashboard parameters"),
        ] = None,
        points_of_interest: Annotated[str | None, Field(description="Points of interest")] = None,
        archived: Annotated[bool | None, Field(description="Whether to archive the dashboard")] = None,
        collection_position: Annotated[int | None, Field(description="Position within the collection")] = None,
        show_in_getting_started: Annotated[bool | None, Field(description="Show in getting started")] = None,
        enable_embedding: Annotated[bool | None, Field(description="Enable embedding (requires superuser)")] = None,
        collection_id: Annotated[int | None, Field(description="Collection ID to move dashboard to")] = None,
        caveats: Annotated[str | None, Field(description="Dashboard caveats")] = None,
        embedding_params: Annotated[
            dict[str, Any] | None,
            BeforeValidator(parse_if_string),
            Field(description="Embedding parameters"),
        ] = None,
        position: Annotated[int | None, Field(description="Dashboard position")] = None,
    ) -> str:
        """Update dashboard properties including name, description, parameters, and settings - use this to maintain metadata, reorganize content, or configure sharing"""
        updates: dict[str, Any] = {}
        if name is not None:
            updates["name"] = name
        if description is not None:
            updates["description"] = description
        if parameters is not None:
            updates["parameters"] = parameters
        if points_of_interest is not None:
            updates["points_of_interest"] = points_of_interest
        if archived is not None:
            updates["archived"] = archived
        if collection_position is not None:
            updates["collection_position"] = collection_position
        if show_in_getting_started is not None:
            updates["show_in_getting_started"] = show_in_getting_started
        if enable_embedding is not None:
            updates["enable_embedding"] = enable_embedding
        if collection_id is not None:
            updates["collection_id"] = collection_id
        if caveats is not None:
            updates["caveats"] = caveats
        if embedding_params is not None:
            updates["embedding_params"] = embedding_params
        if position is not None:
            updates["position"] = position
        result = await client.update_dashboard(dashboard_id, updates)
        return json.dumps(result, indent=2)

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False),
    )
    async def update_dashboard_cards(
        dashboard_id: Annotated[int, Field(description="The ID of the dashboard")],
        cards: Annotated[
            list[Any],
            BeforeValidator(parse_if_string),
            Field(description="Array of card configurations"),
        ],
    ) -> str:
        """WARNING: REPLACES ALL dashboard cards - any cards not in the array will be DELETED. To update a single card, first get_dashboard to fetch ALL cards, then include ALL of them with your modifications. This affects ALL tabs."""
        result = await client.update_dashboard_cards(dashboard_id, cards)
        return json.dumps(result, indent=2)

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False),
    )
    async def update_dashcard(
        dashboard_id: Annotated[int, Field(description="The ID of the dashboard")],
        dashcard_id: Annotated[int, Field(description="The dashcard 'id' field (not card_id)")],
        updates: Annotated[
            Any,
            BeforeValidator(parse_if_string),
            Field(description="Properties to update on the dashcard"),
        ],
    ) -> str:
        """Update a specific dashcard's properties without affecting other cards - use for parameter_mappings, visualization_settings, position, or size changes. Much safer than update_dashboard_cards."""
        result = await client.update_dashcard(dashboard_id, dashcard_id, updates)
        return json.dumps(result, indent=2)

    # ── Delete tools ────────────────────────────────────────────────────

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
    )
    async def delete_dashboard(
        dashboard_id: Annotated[int, Field(description="The ID of the dashboard to delete")],
        hard_delete: Annotated[bool, Field(description="Whether to permanently delete (true) or archive (false)")] = False,
    ) -> str:
        """Delete or archive a dashboard (soft or hard delete) - use with caution as permanent deletion cannot be undone"""
        await client.delete_dashboard(dashboard_id, hard_delete)
        return json.dumps(
            {
                "dashboard_id": dashboard_id,
                "action": "deleted" if hard_delete else "archived",
                "status": "success",
            },
            indent=2,
        )

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
    )
    async def delete_public_link(
        dashboard_id: Annotated[int, Field(description="The ID of the dashboard")],
    ) -> str:
        """Remove public URL access for a dashboard (requires superuser) - use this to revoke external access for security or privacy reasons"""
        await client.delete_dashboard_public_link(dashboard_id)
        return json.dumps(
            {
                "dashboard_id": dashboard_id,
                "action": "public_link_deleted",
                "status": "success",
            },
            indent=2,
        )

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
    )
    async def remove_cards_from_dashboard(
        dashboard_id: Annotated[int, Field(description="The ID of the dashboard")],
        dashcard_ids: Annotated[
            list[int],
            BeforeValidator(parse_if_string),
            Field(description="Array of dashcard IDs to remove (the 'id' field from dashcards, not 'card_id')"),
        ],
    ) -> str:
        """Remove specific dashcards from a dashboard by their dashcard IDs (not card_id) - use this to clean up dashboards or reorganize content"""
        result = await client.remove_cards_from_dashboard(dashboard_id, dashcard_ids)
        return json.dumps(result, indent=2)

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False),
    )
    async def unfavorite_dashboard(
        dashboard_id: Annotated[int, Field(description="The ID of the dashboard")],
    ) -> str:
        """Remove a dashboard from the user's favorites list - use this to clean up bookmarked dashboards"""
        result = await client.unfavorite_dashboard(dashboard_id)
        return json.dumps(result, indent=2)
