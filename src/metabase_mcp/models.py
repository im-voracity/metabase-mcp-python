"""Pydantic models for Metabase API types.

All models use extra="allow" to accept undocumented fields from the API.
Fields are optional to support both creation (few fields) and read (all fields).
"""

from pydantic import BaseModel, ConfigDict


class MetabaseModel(BaseModel):
    """Base model with extra="allow" for all Metabase types."""

    model_config = ConfigDict(extra="allow")


class Dashboard(MetabaseModel):
    id: int | None = None
    name: str | None = None
    description: str | None = None
    collection_id: int | None = None
    archived: bool | None = None
    parameters: list[dict] | None = None  # type: ignore[type-arg]
    dashcards: list[dict] | None = None  # type: ignore[type-arg]


class DashboardCard(MetabaseModel):
    id: int | None = None
    card_id: int | None = None
    dashboard_id: int | None = None
    row: int | None = None
    col: int | None = None
    size_x: int | None = None
    size_y: int | None = None
    parameter_mappings: list[dict] | None = None  # type: ignore[type-arg]
    visualization_settings: dict | None = None  # type: ignore[type-arg]


class Card(MetabaseModel):
    id: int | None = None
    name: str | None = None
    description: str | None = None
    collection_id: int | None = None
    archived: bool | None = None
    dataset_query: dict | None = None  # type: ignore[type-arg]
    display: str | None = None
    visualization_settings: dict | None = None  # type: ignore[type-arg]


class Database(MetabaseModel):
    id: int | None = None
    name: str | None = None
    engine: str | None = None
    details: dict | None = None  # type: ignore[type-arg]
    auto_run_queries: bool | None = None
    is_full_sync: bool | None = None


class Table(MetabaseModel):
    id: int | None = None
    name: str | None = None
    display_name: str | None = None
    description: str | None = None
    database_id: int | None = None
    schema_: str | None = None
    visibility_type: str | None = None
    field_order: str | None = None


class Field(MetabaseModel):
    id: int | None = None
    name: str | None = None
    display_name: str | None = None
    table_id: int | None = None
    database_type: str | None = None
    base_type: str | None = None


class Collection(MetabaseModel):
    id: int | None = None
    name: str | None = None
    description: str | None = None
    color: str | None = None
    parent_id: int | None = None
    archived: bool | None = None


class User(MetabaseModel):
    id: int | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    group_ids: list[int] | None = None


class PermissionGroup(MetabaseModel):
    id: int | None = None
    name: str | None = None


class QueryResult(MetabaseModel):
    data: dict | None = None  # type: ignore[type-arg]
    status: str | None = None
    row_count: int | None = None
    running_time: int | None = None
