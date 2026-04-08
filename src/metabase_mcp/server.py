"""FastMCP server setup with tool registration and filtering."""

from __future__ import annotations

from fastmcp import FastMCP

from metabase_mcp.client import MetabaseClient
from metabase_mcp.config import MetabaseConfig
from metabase_mcp.tools import register_all_tools


def create_server(mode: str = "essential") -> FastMCP:
    """Create and configure the MCP server.

    Args:
        mode: Tool filtering mode - "essential" (default), "write", or "all".

    Returns:
        Configured FastMCP server ready to run.
    """
    config = MetabaseConfig()  # type: ignore[call-arg]
    client = MetabaseClient(config)

    mcp = FastMCP(
        name="Metabase MCP Server",
        instructions=(
            "MCP server for interacting with Metabase analytics platform. "
            "Provides tools for managing dashboards, cards (saved questions), "
            "databases, tables, collections, and users."
        ),
    )

    register_all_tools(mcp, client, mode=mode)

    return mcp
