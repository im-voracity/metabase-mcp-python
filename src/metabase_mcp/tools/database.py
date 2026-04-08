"""MCP tools for Metabase database operations."""

from __future__ import annotations

import json
from typing import Annotated, Any

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from metabase_mcp.client import MetabaseClient
from metabase_mcp.validators import JsonParsed, JsonParsedList


def register_database_tools(mcp: FastMCP, client: MetabaseClient) -> None:
    """Register all database-related MCP tools."""

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def list_databases() -> str:
        """Retrieve all database connections in Metabase - use this to discover available data sources, check connection status, or get an overview of connected databases"""
        result = await client.get_databases()
        return json.dumps(result, indent=2)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def get_database(
        database_id: Annotated[int, Field(description="The ID of the database to retrieve")],
    ) -> str:
        """Retrieve detailed information about a specific Metabase database including connection details and schema - use this to examine database properties or troubleshoot connections"""
        result = await client.get_database(database_id)
        return json.dumps(result, indent=2)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False))
    async def create_database(
        engine: Annotated[str, Field(description="Database engine type (e.g., postgres, mysql, redshift)")],
        name: Annotated[str, Field(description="Display name for the database")],
        details: Annotated[JsonParsed, Field(description="Database connection details")],
        is_full_sync: Annotated[bool | None, Field(description="Whether to perform full sync")] = None,
        is_on_demand: Annotated[bool | None, Field(description="Whether database is on-demand")] = None,
        schedules: Annotated[JsonParsed | None, Field(description="Sync schedules")] = None,
    ) -> str:
        """Add a new database connection to Metabase - use this to connect new data sources, establish analytical pipelines, or expand data access"""
        payload: dict[str, Any] = {
            "engine": engine,
            "name": name,
            "details": details,
        }
        if is_full_sync is not None:
            payload["is_full_sync"] = is_full_sync
        if is_on_demand is not None:
            payload["is_on_demand"] = is_on_demand
        if schedules is not None:
            payload["schedules"] = schedules
        result = await client.create_database(payload)
        return json.dumps(result, indent=2)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False))
    async def update_database(
        database_id: Annotated[int, Field(description="The ID of the database to update")],
        name: Annotated[str | None, Field(description="New display name for the database")] = None,
        engine: Annotated[str | None, Field(description="Database engine type")] = None,
        details: Annotated[JsonParsed | None, Field(description="Updated database connection details")] = None,
        is_full_sync: Annotated[bool | None, Field(description="Whether to perform full sync")] = None,
        is_on_demand: Annotated[bool | None, Field(description="Whether database is on-demand")] = None,
        schedules: Annotated[JsonParsed | None, Field(description="Updated sync schedules")] = None,
    ) -> str:
        """Update database configuration including name, connection details, and sync settings - use this to maintain connections, update credentials, or modify sync behavior"""
        updates: dict[str, Any] = {}
        if name is not None:
            updates["name"] = name
        if engine is not None:
            updates["engine"] = engine
        if details is not None:
            updates["details"] = details
        if is_full_sync is not None:
            updates["is_full_sync"] = is_full_sync
        if is_on_demand is not None:
            updates["is_on_demand"] = is_on_demand
        if schedules is not None:
            updates["schedules"] = schedules
        result = await client.update_database(database_id, updates)
        return json.dumps(result, indent=2)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True))
    async def delete_database(
        database_id: Annotated[int, Field(description="The ID of the database to delete")],
    ) -> str:
        """Permanently remove a database from Metabase - use with caution as this will break dependent content and cannot be undone"""
        await client.delete_database(database_id)
        return json.dumps(
            {
                "database_id": database_id,
                "action": "deleted",
                "status": "success",
            },
            indent=2,
        )

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False))
    async def validate_database(
        engine: Annotated[str, Field(description="Database engine type (e.g., postgres, mysql, redshift)")],
        details: Annotated[JsonParsed, Field(description="Database connection details to validate")],
    ) -> str:
        """Test database connection parameters before creating - use this to verify credentials, connectivity, and accessibility"""
        result = await client.validate_database(engine, details)
        return json.dumps(result, indent=2)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False))
    async def add_sample_database() -> str:
        """Add the built-in Metabase sample database with demo data - use this for testing, learning, or exploring Metabase features"""
        result = await client.add_sample_database()
        return json.dumps(result, indent=2)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def check_database_health(
        database_id: Annotated[int, Field(description="The ID of the database to check")],
    ) -> str:
        """Perform health check on database connection - use this to diagnose issues, monitor status, or troubleshoot sync problems"""
        result = await client.check_database_health(database_id)
        return json.dumps(result, indent=2)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def get_database_metadata(
        database_id: Annotated[int, Field(description="The ID of the database")],
    ) -> str:
        """Retrieve comprehensive database metadata including tables, fields, and relationships - use this to understand structure or build dynamic queries"""
        result = await client.get_database_metadata(database_id)
        return json.dumps(result, indent=2)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def list_database_schemas(
        database_id: Annotated[int, Field(description="The ID of the database")],
    ) -> str:
        """Retrieve all schema names in a database - use this to explore database organization or navigate multi-schema databases"""
        result = await client.get_database_schemas(database_id)
        return json.dumps(result, indent=2)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def get_database_schema(
        database_id: Annotated[int, Field(description="The ID of the database")],
        schema_name: Annotated[str, Field(description="The name of the schema")],
    ) -> str:
        """Retrieve detailed information about a specific schema including tables and objects - use this to explore schema contents or understand organization"""
        result = await client.get_database_schema(database_id, schema_name)
        return json.dumps(result, indent=2)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def execute_query(
        database_id: Annotated[int, Field(description="The ID of the database to query against")],
        query: Annotated[str, Field(description="The SQL query to execute")],
        parameters: Annotated[JsonParsedList | None, Field(description="Optional query parameters for parameterized queries")] = None,
    ) -> str:
        """Execute a native SQL query against a Metabase database - use this for custom data analysis, complex queries, or extracting specific data not available through existing cards"""
        result = await client.execute_query(database_id, query, parameters or [])
        return json.dumps(result, indent=2)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False))
    async def sync_database_schema(
        database_id: Annotated[int, Field(description="The ID of the database to sync")],
    ) -> str:
        """Initiate schema sync to update Metabase metadata cache - use this after database changes to recognize new tables, columns, or relationships"""
        result = await client.sync_database_schema(database_id)
        return json.dumps(
            {
                "database_id": database_id,
                "action": "schema_sync_triggered",
                "status": "success",
                "result": result,
            },
            indent=2,
        )
