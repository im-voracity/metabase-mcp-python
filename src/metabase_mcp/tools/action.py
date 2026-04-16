"""MCP tools for Metabase action operations."""

from __future__ import annotations

import json
from typing import Annotated, Any

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import BeforeValidator, Field

from metabase_mcp.client import MetabaseClient
from metabase_mcp.validators import parse_if_string


def register_action_tools(mcp: FastMCP, client: MetabaseClient) -> None:
    """Register all action-related MCP tools."""

    # ── Read tools ──────────────────────────────────────────────────────

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def list_actions() -> str:
        """List all actions - use this to discover available write-back actions or custom HTTP actions"""
        result = await client.get_actions()
        return json.dumps(result, indent=2)

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def get_action(
        action_id: Annotated[int, Field(description="The ID of the action")],
    ) -> str:
        """Get detailed information about a specific action including its query, parameters, and settings"""
        result = await client.get_action(action_id)
        return json.dumps(result, indent=2)

    # ── Write tools ─────────────────────────────────────────────────────

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False),
    )
    async def create_action(
        name: Annotated[str, Field(description="Name of the action")],
        model_id: Annotated[int, Field(description="The ID of the model this action belongs to")],
        type: Annotated[
            str,
            Field(description="Action type: 'query' (SQL), 'implicit', or 'http'"),
        ],
        database_id: Annotated[
            int | None,
            Field(description="Database ID (required for query actions)"),
        ] = None,
        dataset_query: Annotated[
            dict[str, Any] | None,
            BeforeValidator(parse_if_string),
            Field(description="The query definition (for query-type actions)"),
        ] = None,
        description: Annotated[
            str | None,
            Field(description="Description of the action"),
        ] = None,
        parameters: Annotated[
            list[dict[str, Any]] | None,
            BeforeValidator(parse_if_string),
            Field(description="Action parameters definition"),
        ] = None,
    ) -> str:
        """Create a new action (query, implicit, or HTTP) on a model - use this to enable write-back operations on databases through Metabase"""
        action_data: dict[str, Any] = {
            "name": name,
            "model_id": model_id,
            "type": type,
        }
        if database_id is not None:
            action_data["database_id"] = database_id
        if dataset_query is not None:
            action_data["dataset_query"] = dataset_query
        if description is not None:
            action_data["description"] = description
        if parameters is not None:
            action_data["parameters"] = parameters
        result = await client.create_action(action_data)
        return json.dumps(result, indent=2)

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False),
    )
    async def update_action(
        action_id: Annotated[int, Field(description="The ID of the action to update")],
        name: Annotated[str | None, Field(description="New name")] = None,
        description: Annotated[str | None, Field(description="New description")] = None,
        dataset_query: Annotated[
            dict[str, Any] | None,
            BeforeValidator(parse_if_string),
            Field(description="Updated query definition"),
        ] = None,
    ) -> str:
        """Update an existing action's properties - use this to modify action queries, names, or settings"""
        updates: dict[str, Any] = {}
        if name is not None:
            updates["name"] = name
        if description is not None:
            updates["description"] = description
        if dataset_query is not None:
            updates["dataset_query"] = dataset_query
        result = await client.update_action(action_id, updates)
        return json.dumps(result, indent=2)

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
    )
    async def delete_action(
        action_id: Annotated[int, Field(description="The ID of the action to delete")],
    ) -> str:
        """Delete an action - WARNING: this permanently removes the action"""
        await client.delete_action(action_id)
        return json.dumps(
            {"action_id": action_id, "action": "deleted", "status": "success"},
            indent=2,
        )

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False),
    )
    async def execute_action(
        action_id: Annotated[int, Field(description="The ID of the action to execute")],
        parameters: Annotated[
            dict[str, Any] | None,
            BeforeValidator(parse_if_string),
            Field(description="Parameters to pass to the action as JSON"),
        ] = None,
    ) -> str:
        """Execute an action with optional parameters - use this to trigger write-back operations, custom HTTP calls, or implicit CRUD actions"""
        result = await client.execute_action(action_id, parameters)
        return json.dumps(result, indent=2)
