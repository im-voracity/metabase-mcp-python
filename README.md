# metabase-mcp-python

A Python [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) server for [Metabase](https://www.metabase.com/), enabling AI assistants to query databases, manage dashboards, and interact with your Metabase instance.

Inspired by [CognitionAI/metabase-mcp-server](https://github.com/CognitionAI/metabase-mcp-server) (TypeScript). See [CREDITS.md](CREDITS.md) for attribution.

## Installation

### With uv (recommended)

```bash
uv tool install metabase-mcp-python
```

### With pip

```bash
pip install metabase-mcp-python
```

### From source

```bash
git clone https://github.com/im-voracity/metabase-mcp-python.git
cd metabase-mcp-python
uv sync
```

## Configuration

Set the following environment variables (or use a `.env` file):

| Variable | Required | Description |
|---|---|---|
| `METABASE_URL` | Yes | Your Metabase instance URL (e.g., `http://localhost:3000`) |
| `METABASE_API_KEY` | One of | Metabase API key for authentication |
| `METABASE_USERNAME` | One of | Username for session-based authentication |
| `METABASE_PASSWORD` | One of | Password for session-based authentication |

You must provide either `METABASE_API_KEY` or both `METABASE_USERNAME` and `METABASE_PASSWORD`.

## Usage

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "metabase": {
      "command": "uv",
      "args": ["tool", "run", "metabase-mcp-python"],
      "env": {
        "METABASE_URL": "http://localhost:3000",
        "METABASE_API_KEY": "your-api-key"
      }
    }
  }
}
```

With session authentication:

```json
{
  "mcpServers": {
    "metabase": {
      "command": "uv",
      "args": ["tool", "run", "metabase-mcp-python"],
      "env": {
        "METABASE_URL": "http://localhost:3000",
        "METABASE_USERNAME": "user@example.com",
        "METABASE_PASSWORD": "your-password"
      }
    }
  }
}
```

### Claude CLI

```json
{
  "mcpServers": {
    "metabase": {
      "command": "uv",
      "args": ["tool", "run", "metabase-mcp-python", "--write"],
      "env": {
        "METABASE_URL": "http://localhost:3000",
        "METABASE_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Running from source

```json
{
  "mcpServers": {
    "metabase": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/metabase-mcp-python", "metabase-mcp"],
      "env": {
        "METABASE_URL": "http://localhost:3000",
        "METABASE_API_KEY": "your-api-key"
      }
    }
  }
}
```

## Tool Filtering Modes

The server supports three modes to control which tools are exposed to the AI assistant:

| Mode | Flag | Tools | Description |
|---|---|---|---|
| Essential | `--essential` (default) | ~19 | Core read operations for querying and exploring |
| Write | `--write` | ~59 | Essential + create, update, and delete operations |
| All | `--all` | ~87 | Every available tool including advanced operations |

Examples:

```bash
metabase-mcp                # Essential mode (default)
metabase-mcp --write        # Essential + write tools
metabase-mcp --all          # All tools
```

The essential mode is the default to keep the tool list manageable and reduce the risk of unintended modifications. Use `--write` or `--all` when you need to create or modify Metabase resources.

## Available Tools

Tools are organized into five categories:

- **Database** (13 tools) -- List, inspect, create, and manage database connections; execute SQL queries
- **Table** (17 tools) -- Browse tables, inspect schemas, manage field metadata, import/export CSV
- **Card** (21 tools) -- CRUD for saved questions, execute queries, manage public links, move cards
- **Dashboard** (27 tools) -- CRUD for dashboards, manage cards/layout, filters audit, public links
- **Additional** (9 tools) -- Collections, search, users, playground links

See [docs/tools-reference.md](docs/tools-reference.md) for the complete tool listing.

## Development

### Setup

```bash
git clone https://github.com/im-voracity/metabase-mcp-python.git
cd metabase-mcp-python
uv sync --group dev
```

### Testing

```bash
uv run pytest
uv run pytest -m "not integration"    # Skip integration tests
```

### Linting and type checking

```bash
uv run ruff check src tests
uv run ruff format --check src tests
uv run mypy src
```

## Architecture

See [docs/architecture.md](docs/architecture.md) for a detailed overview of the codebase structure, request flow, and authentication system.

## License

[MIT](LICENSE)
