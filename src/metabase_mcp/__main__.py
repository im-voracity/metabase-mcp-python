"""Entry point for running the Metabase MCP server.

Usage:
    python -m metabase_mcp              # Essential tools only (default)
    python -m metabase_mcp --all        # All tools
    python -m metabase_mcp --write      # Essential + write tools
"""

from __future__ import annotations

import argparse

from metabase_mcp.server import create_server


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Metabase MCP Server - Connect AI assistants to Metabase",
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--essential",
        action="store_true",
        default=True,
        help="Load only essential tools (default)",
    )
    group.add_argument(
        "--all",
        action="store_true",
        help="Load all available tools",
    )
    group.add_argument(
        "--write",
        action="store_true",
        help="Load essential + write tools",
    )

    args = parser.parse_args()

    if args.all:
        mode = "all"
    elif args.write:
        mode = "write"
    else:
        mode = "essential"

    server = create_server(mode=mode)
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
