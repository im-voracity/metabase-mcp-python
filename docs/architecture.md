# Architecture

## Component Overview

```
+------------------+     +------------------+     +----------------+     +------------------+
|                  |     |                  |     |                |     |                  |
|  MetabaseConfig  +---->+  MetabaseClient  +---->+  Tool modules  +---->+  FastMCP Server  |
|  (config.py)     |     |  (client.py)     |     |  (tools/*.py)  |     |  (server.py)     |
|                  |     |                  |     |                |     |                  |
+------------------+     +------------------+     +----------------+     +------------------+
       |                        |                        |                        |
  Env vars / .env         httpx.AsyncClient        @mcp.tool()              stdio transport
  pydantic-settings       MetabaseAuth             Tool filtering           MCP protocol
```

### MetabaseConfig (`src/metabase_mcp/config.py`)

Loads configuration from environment variables using `pydantic-settings`. Validates that `METABASE_URL` is a well-formed URL and that either an API key or username/password credentials are provided.

### MetabaseClient (`src/metabase_mcp/client.py`)

Async HTTP client wrapping the Metabase REST API. Uses `httpx.AsyncClient` with a custom `MetabaseAuth` handler. Provides typed methods for every supported API endpoint (dashboards, cards, databases, tables, collections, users, permissions, activity).

### Tool Modules (`src/metabase_mcp/tools/`)

Each module registers a group of MCP tools via `@mcp.tool()` decorators:

- `database.py` -- Database connections, queries, schema inspection
- `table.py` -- Table metadata, field operations, CSV import/export
- `card.py` -- Saved questions CRUD, execution, public links
- `dashboard.py` -- Dashboard CRUD, card layout, filter auditing
- `additional.py` -- Collections, search, users, playground links

### FastMCP Server (`src/metabase_mcp/server.py`)

Creates the `FastMCP` instance, initializes the client, and registers all tools. Tool filtering is applied after registration by removing tools that do not match the selected mode.

### Entry Point (`src/metabase_mcp/__main__.py`)

Parses CLI arguments (`--essential`, `--write`, `--all`), creates the server, and starts it with stdio transport.

## Request Flow

```
MCP Client (Claude, etc.)
    |
    |  MCP protocol (stdio)
    v
FastMCP Server
    |
    |  Routes to registered tool function
    v
Tool function (e.g., list_dashboards)
    |
    |  Calls client method
    v
MetabaseClient._request()
    |
    |  httpx.AsyncClient with MetabaseAuth
    v
Metabase REST API
```

1. The MCP client sends a tool call request over stdio.
2. FastMCP dispatches the call to the matching tool function.
3. The tool function calls the appropriate `MetabaseClient` method.
4. `MetabaseClient._request()` sends the HTTP request via `httpx.AsyncClient`.
5. `MetabaseAuth` injects the authentication header (API key or session token).
6. The response is parsed, error-checked, and returned as JSON.

## Authentication

Authentication is handled by `MetabaseAuth`, an `httpx.Auth` subclass that implements the `auth_flow()` generator:

- **API key**: Sets the `X-API-Key` header on every request. No additional round-trips.
- **Session token**: On the first request, yields a sub-request to `POST /api/session` with username/password. Caches the returned session token and sets `X-Metabase-Session` on subsequent requests.

This replaces the axios request interceptor pattern from the original TypeScript implementation. The `httpx.Auth` approach is idiomatic Python and allows httpx to handle the authentication flow transparently.

### Redirect Handling

`MetabaseClient._request()` handles HTTP-to-HTTPS redirects manually (up to 3 hops) to preserve the original HTTP method. The default `follow_redirects` behavior in httpx converts POST/PUT to GET on 301/302 redirects, which breaks API calls.

## Tool Filtering

The tool registry (`src/metabase_mcp/tools/__init__.py`) defines three sets:

- **ESSENTIAL_TOOLS**: ~19 core read-only tools for querying and exploration.
- **WRITE_TOOLS**: ~40 additional tools that create, update, or delete resources.
- **All tools**: The full set of ~87 tools across all modules.

Filtering works by registering all tools first, then removing those that do not match the selected mode. This approach avoids conditional logic inside each tool module.

| Mode | Includes |
|---|---|
| `essential` | Only tools in `ESSENTIAL_TOOLS` |
| `write` | Tools in `ESSENTIAL_TOOLS` + `WRITE_TOOLS` |
| `all` | All registered tools |

## Adding New Tools

1. Identify the Metabase API endpoint and add a client method to `MetabaseClient` in `client.py`.
2. Create the tool function in the appropriate module under `tools/` using `@mcp.tool()`.
3. If the tool should be available in essential or write mode, add its name to the corresponding set in `tools/__init__.py`.
4. Add tests in `tests/tools/`.

### Tool function conventions

- Use `Annotated[type, Field(description="...")]` for all parameters.
- Set `annotations=ToolAnnotations(readOnlyHint=True)` for read operations, `readOnlyHint=False` for writes, and add `destructiveHint=True` for deletes.
- Return `json.dumps(result, indent=2)` as a string.
- Use validators from `validators.py` (`JsonParsed`, `JsonParsedList`, `parse_if_string`) for parameters that may arrive as JSON strings.
