# Tools Reference

Complete listing of all 87 MCP tools, organized by category. Each tool's availability depends on the selected [filtering mode](../README.md#tool-filtering-modes).

**Legend**: E = essential, W = write, A = all-only

## Database (13 tools)

| Tool | Mode | Description |
|---|---|---|
| `list_databases` | E | Retrieve all database connections in Metabase |
| `get_database` | E | Retrieve detailed information about a specific database |
| `execute_query` | E | Execute a native SQL query against a database |
| `create_database` | W | Add a new database connection to Metabase |
| `update_database` | W | Update database configuration (name, connection, sync settings) |
| `delete_database` | W | Permanently remove a database from Metabase |
| `validate_database` | A | Test database connection parameters before creating |
| `add_sample_database` | W | Add the built-in Metabase sample database |
| `check_database_health` | A | Perform health check on a database connection |
| `get_database_metadata` | A | Retrieve comprehensive metadata (tables, fields, relationships) |
| `list_database_schemas` | A | Retrieve all schema names in a database |
| `get_database_schema` | A | Retrieve detailed information about a specific schema |
| `sync_database_schema` | W | Initiate schema sync to update Metabase metadata cache |

## Table (17 tools)

| Tool | Mode | Description |
|---|---|---|
| `list_tables` | E | Retrieve all tables with optional ID filtering |
| `get_table` | E | Retrieve comprehensive table information including schema and fields |
| `get_field_id` | E | Look up a field's ID and metadata by table and column name |
| `get_table_data` | E | Retrieve sample data from a table for preview |
| `update_tables` | W | Bulk update multiple tables with the same configuration |
| `update_table` | W | Update a single table's display name, description, and settings |
| `get_table_fks` | A | Retrieve foreign key relationships for a table |
| `get_table_query_metadata` | A | Retrieve query-optimized table metadata |
| `get_table_related` | A | Find tables and entities related through relationships |
| `get_card_table_fks` | A | Retrieve foreign keys for a card's virtual table |
| `get_card_table_query_metadata` | A | Retrieve query metadata for a card's virtual table |
| `append_csv_to_table` | W | Add new rows from CSV content to an existing table |
| `discard_table_field_values` | W | Clear cached field values to force fresh loading |
| `reorder_table_fields` | W | Change display order of table fields |
| `replace_table_csv` | W | Completely replace table data with new CSV content |
| `rescan_table_field_values` | W | Trigger rescan to refresh field values cache |
| `sync_table_schema` | W | Initiate schema sync for a specific table |

## Card (21 tools)

| Tool | Mode | Description |
|---|---|---|
| `list_cards` | E | Retrieve all cards with optional filtering by source type |
| `get_card` | E | Get complete metadata and configuration for a specific card |
| `execute_card` | E | Run a card query and return the data results |
| `get_card_dashboards` | E | Find all dashboards that include a specific card |
| `create_card` | W | Create a new card with custom query and visualization |
| `update_card` | W | Modify a card's name, query, visualization, or settings |
| `delete_card` | W | Remove a card (archive or permanent delete) |
| `copy_card` | W | Create a duplicate copy of an existing card |
| `move_cards` | W | Relocate multiple cards to a different collection or dashboard |
| `move_cards_to_collection` | W | Bulk transfer multiple cards to a specific collection |
| `create_card_public_link` | W | Generate a publicly accessible URL for a card |
| `delete_card_public_link` | W | Remove public access to a card |
| `export_card_result` | A | Execute a card and export results in a specific format (CSV, XLSX, JSON) |
| `list_embeddable_cards` | A | Retrieve all cards configured for embedding |
| `list_public_cards` | A | Retrieve all cards with public URLs enabled |
| `execute_pivot_card_query` | A | Run a card with pivot table formatting |
| `get_card_param_values` | A | Retrieve available values for a card parameter |
| `search_card_param_values` | A | Search and filter available parameter values |
| `get_card_param_remapping` | A | Retrieve how parameter values are remapped for display |
| `get_card_query_metadata` | A | Retrieve structural metadata about a card's query |
| `get_card_series` | A | Retrieve time series data or related card suggestions |

## Dashboard (27 tools)

| Tool | Mode | Description |
|---|---|---|
| `list_dashboards` | E | Retrieve all dashboards |
| `get_dashboard` | E | Retrieve detailed information about a specific dashboard |
| `get_dashboard_cards` | E | Retrieve all cards within a specific dashboard |
| `create_dashboard` | E/W | Create a new dashboard |
| `create_public_link` | W | Generate a publicly accessible URL for a dashboard |
| `copy_dashboard` | W | Create a copy of an existing dashboard with all cards |
| `add_card_to_dashboard` | W | Add an existing card to a dashboard |
| `add_text_block` | W | Add a text block or heading to a dashboard |
| `update_dashboard` | W | Update dashboard properties (name, description, parameters) |
| `update_dashboard_cards` | W | Replace all dashboard cards (destructive) |
| `update_dashcard` | W | Update a specific dashcard's properties |
| `delete_dashboard` | W | Delete or archive a dashboard |
| `delete_public_link` | W | Remove public URL access for a dashboard |
| `remove_cards_from_dashboard` | W | Remove specific dashcards from a dashboard |
| `favorite_dashboard` | W | Mark a dashboard as favorite |
| `unfavorite_dashboard` | W | Remove a dashboard from favorites |
| `revert_dashboard` | W | Restore a dashboard to a previous revision |
| `save_dashboard` | W | Save a complete dashboard object |
| `save_dashboard_to_collection` | W | Save a dashboard into a specific collection |
| `get_dashboard_related` | A | Retrieve entities related to a dashboard |
| `get_dashboard_revisions` | A | Retrieve revision history for a dashboard |
| `list_embeddable_dashboards` | A | Retrieve all dashboards configured for embedding |
| `list_public_dashboards` | A | Retrieve all dashboards with public URLs enabled |
| `search_dashboards` | A | Search dashboards by name or description |
| `execute_dashboard_card` | A | Execute a specific card from a dashboard |
| `get_dashboard_queries` | A | Extract all queries from a dashboard with resolved names |
| `audit_dashboard_filters` | A | Analyze filter connections to find misconfigurations |

## Additional (9 tools)

| Tool | Mode | Description |
|---|---|---|
| `list_collections` | E | Retrieve all collections |
| `get_collection_items` | E | Retrieve all items within a collection |
| `search_content` | E | Search across all Metabase content |
| `get_metabase_playground_link` | E | Generate a Metabase playground link for interactive exploration |
| `create_collection` | W | Create a new collection |
| `update_collection` | W | Update collection properties |
| `delete_collection` | W | Permanently delete a collection |
| `move_to_collection` | W | Move a card or dashboard to a different collection |
| `list_users` | A | Retrieve all Metabase users with roles and permissions |
