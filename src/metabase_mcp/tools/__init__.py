"""MCP tool registry with filtering by mode.

Supports three modes:
- essential (default): Only core tools for basic operations
- write: Essential tools + all write/modification tools
- all: All available tools
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import FastMCP

    from metabase_mcp.client import MetabaseClient

# Tools loaded in --essential mode (default)
ESSENTIAL_TOOLS: set[str] = {
    # Dashboard
    "list_dashboards",
    "get_dashboard",
    "get_dashboard_cards",
    "create_dashboard",
    # Database
    "list_databases",
    "get_database",
    "execute_query",
    # Table
    "list_tables",
    "get_table",
    "get_field_id",
    "get_table_data",
    # Card
    "list_cards",
    "get_card",
    "execute_card",
    "get_card_dashboards",
    # Additional
    "list_collections",
    "get_collection_items",
    "search_content",
    "get_metabase_playground_link",
}

# Tools that perform write/modify operations
WRITE_TOOLS: set[str] = {
    # Dashboard write
    "create_dashboard",
    "update_dashboard",
    "delete_dashboard",
    "copy_dashboard",
    "create_public_link",
    "delete_public_link",
    "add_card_to_dashboard",
    "add_text_block",
    "update_dashboard_cards",
    "update_dashcard",
    "remove_cards_from_dashboard",
    "favorite_dashboard",
    "unfavorite_dashboard",
    "revert_dashboard",
    "save_dashboard",
    "save_dashboard_to_collection",
    "create_dashboard_tab",
    "update_dashboard_tab",
    "delete_dashboard_tab",
    # Card write
    "create_card",
    "update_card",
    "delete_card",
    "copy_card",
    "move_cards",
    "move_cards_to_collection",
    "create_card_public_link",
    "delete_card_public_link",
    # Database write
    "create_database",
    "update_database",
    "delete_database",
    "add_sample_database",
    "sync_database_schema",
    # Table write
    "update_tables",
    "update_table",
    "append_csv_to_table",
    "replace_table_csv",
    "discard_table_field_values",
    "reorder_table_fields",
    "rescan_table_field_values",
    "sync_table_schema",
    # Notification write
    "create_notification",
    "update_notification",
    "send_notification",
    "unsubscribe_notification",
    # Action write
    "create_action",
    "update_action",
    "delete_action",
    "execute_action",
    # Field write
    "update_field",
    "rescan_field_values",
    "discard_field_values",
    # Additional write
    "create_collection",
    "update_collection",
    "delete_collection",
    "move_to_collection",
}


def _should_register(tool_name: str, mode: str) -> bool:
    """Check if a tool should be registered based on the current mode."""
    if mode == "all":
        return True
    if mode == "essential":
        return tool_name in ESSENTIAL_TOOLS
    if mode == "write":
        return tool_name in ESSENTIAL_TOOLS or tool_name in WRITE_TOOLS
    return False


def register_all_tools(mcp: FastMCP, client: MetabaseClient, mode: str = "essential") -> None:
    """Register all MCP tools with filtering based on mode.

    After registering all tools, removes those that don't match the current mode.
    """
    from metabase_mcp.tools.action import register_action_tools
    from metabase_mcp.tools.additional import register_additional_tools
    from metabase_mcp.tools.card import register_card_tools
    from metabase_mcp.tools.dashboard import register_dashboard_tools
    from metabase_mcp.tools.database import register_database_tools
    from metabase_mcp.tools.field import register_field_tools
    from metabase_mcp.tools.notification import register_notification_tools
    from metabase_mcp.tools.table import register_table_tools

    # Register all tools first
    register_database_tools(mcp, client)
    register_table_tools(mcp, client)
    register_field_tools(mcp, client)
    register_card_tools(mcp, client)
    register_dashboard_tools(mcp, client)
    register_action_tools(mcp, client)
    register_notification_tools(mcp, client)
    register_additional_tools(mcp, client)

    if mode == "all":
        return

    # Remove tools that don't match the current mode
    provider = mcp._local_provider
    # Components are keyed as "tool:{name}@"
    tool_names = [
        key.split(":")[1].split("@")[0]
        for key in list(provider._components)
        if key.startswith("tool:")
    ]
    for name in tool_names:
        if not _should_register(name, mode):
            provider.remove_tool(name)
