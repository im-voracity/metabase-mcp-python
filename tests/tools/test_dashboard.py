"""Tests for dashboard tool registration and execution."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest
from fastmcp import FastMCP

from metabase_mcp.tools.dashboard import (
    _process_dashcard,
    _resolve_field_ref,
    _resolve_mbql,
    register_dashboard_tools,
)


@pytest.fixture
def mcp_with_dash_tools(mcp: FastMCP, mock_client: AsyncMock) -> FastMCP:
    register_dashboard_tools(mcp, mock_client)
    return mcp


@pytest.mark.asyncio
async def test_list_dashboards_tool(mcp_with_dash_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.get_dashboards.return_value = [{"id": 1, "name": "Sales"}]
    result = await mcp_with_dash_tools.call_tool("list_dashboards", {})
    mock_client.get_dashboards.assert_awaited_once()
    data = json.loads(result.content[0].text)
    assert data[0]["name"] == "Sales"


@pytest.mark.asyncio
async def test_get_dashboard_tool(mcp_with_dash_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.get_dashboard.return_value = {"id": 1, "name": "Sales", "dashcards": []}
    result = await mcp_with_dash_tools.call_tool("get_dashboard", {"dashboard_id": 1})
    mock_client.get_dashboard.assert_awaited_once_with(1)
    data = json.loads(result.content[0].text)
    assert data["name"] == "Sales"


@pytest.mark.asyncio
async def test_create_dashboard_tool(mcp_with_dash_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.create_dashboard.return_value = {"id": 2, "name": "New Dash"}
    result = await mcp_with_dash_tools.call_tool(
        "create_dashboard",
        {
            "name": "New Dash",
        },
    )
    mock_client.create_dashboard.assert_awaited_once()
    data = json.loads(result.content[0].text)
    assert data["name"] == "New Dash"


@pytest.mark.asyncio
async def test_update_dashboard_tool(mcp_with_dash_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.update_dashboard.return_value = {"id": 1, "name": "Updated"}
    result = await mcp_with_dash_tools.call_tool(
        "update_dashboard",
        {
            "dashboard_id": 1,
            "name": "Updated",
        },
    )
    mock_client.update_dashboard.assert_awaited_once()
    data = json.loads(result.content[0].text)
    assert data["name"] == "Updated"


@pytest.mark.asyncio
async def test_delete_dashboard_tool(mcp_with_dash_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.delete_dashboard.return_value = None
    await mcp_with_dash_tools.call_tool(
        "delete_dashboard",
        {
            "dashboard_id": 1,
        },
    )
    mock_client.delete_dashboard.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_dashboard_cards_tool(
    mcp_with_dash_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.get_dashboard.return_value = {
        "id": 1,
        "dashcards": [{"id": 10, "card_id": 5}],
    }
    result = await mcp_with_dash_tools.call_tool("get_dashboard_cards", {"dashboard_id": 1})
    data = json.loads(result.content[0].text)
    assert len(data) == 1
    assert data[0]["card_id"] == 5


@pytest.mark.asyncio
async def test_get_dashboard_related_tool(
    mcp_with_dash_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.get_dashboard_related.return_value = {"related": []}
    result = await mcp_with_dash_tools.call_tool("get_dashboard_related", {"dashboard_id": 1})
    data = json.loads(result.content[0].text)
    assert "related" in data


@pytest.mark.asyncio
async def test_get_dashboard_revisions_tool(
    mcp_with_dash_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.get_dashboard_revisions.return_value = [{"id": 1, "is_reversion": False}]
    result = await mcp_with_dash_tools.call_tool("get_dashboard_revisions", {"dashboard_id": 1})
    data = json.loads(result.content[0].text)
    assert len(data) == 1


@pytest.mark.asyncio
async def test_list_embeddable_dashboards_tool(
    mcp_with_dash_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.get_embeddable_dashboards.return_value = []
    result = await mcp_with_dash_tools.call_tool("list_embeddable_dashboards", {})
    data = json.loads(result.content[0].text)
    assert data == []


@pytest.mark.asyncio
async def test_list_public_dashboards_tool(
    mcp_with_dash_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.get_public_dashboards.return_value = []
    result = await mcp_with_dash_tools.call_tool("list_public_dashboards", {})
    data = json.loads(result.content[0].text)
    assert data == []


@pytest.mark.asyncio
async def test_search_dashboards_tool(mcp_with_dash_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.get_dashboards.return_value = [
        {"name": "Sales Report", "description": ""},
        {"name": "Marketing", "description": "sales figures"},
        {"name": "Ops", "description": ""},
    ]
    result = await mcp_with_dash_tools.call_tool("search_dashboards", {"query": "sales"})
    data = json.loads(result.content[0].text)
    assert len(data) == 2  # "Sales Report" and "Marketing" (description matches)


@pytest.mark.asyncio
async def test_search_dashboards_with_limit(
    mcp_with_dash_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.get_dashboards.return_value = [
        {"name": "Sales 1", "description": ""},
        {"name": "Sales 2", "description": ""},
    ]
    result = await mcp_with_dash_tools.call_tool(
        "search_dashboards", {"query": "sales", "limit": 1}
    )
    data = json.loads(result.content[0].text)
    assert len(data) == 1


@pytest.mark.asyncio
async def test_execute_dashboard_card_tool(
    mcp_with_dash_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.execute_card.return_value = {"data": {"rows": [[1]]}}
    result = await mcp_with_dash_tools.call_tool(
        "execute_dashboard_card",
        {
            "dashboard_id": 1,
            "card_id": 5,
        },
    )
    data = json.loads(result.content[0].text)
    assert data["card_id"] == 5
    assert data["status"] == "completed"


@pytest.mark.asyncio
async def test_copy_dashboard_tool(mcp_with_dash_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.copy_dashboard.return_value = {"id": 2, "name": "Copy"}
    result = await mcp_with_dash_tools.call_tool(
        "copy_dashboard",
        {
            "from_dashboard_id": 1,
            "name": "Copy",
        },
    )
    data = json.loads(result.content[0].text)
    assert data["name"] == "Copy"


@pytest.mark.asyncio
async def test_add_card_to_dashboard_tool(
    mcp_with_dash_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.add_card_to_dashboard.return_value = {"id": 1, "dashcards": []}
    result = await mcp_with_dash_tools.call_tool(
        "add_card_to_dashboard",
        {
            "dashboard_id": 1,
            "cardId": 5,
        },
    )
    data = json.loads(result.content[0].text)
    assert data["id"] == 1


@pytest.mark.asyncio
async def test_add_text_block_tool(mcp_with_dash_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.add_card_to_dashboard.return_value = {"id": 1, "dashcards": []}
    result = await mcp_with_dash_tools.call_tool(
        "add_text_block",
        {
            "dashboard_id": 1,
            "text": "Hello World",
        },
    )
    data = json.loads(result.content[0].text)
    assert data["id"] == 1
    # Verify visualization_settings was passed with text
    call_args = mock_client.add_card_to_dashboard.call_args[0]
    assert call_args[1]["visualization_settings"]["text"] == "Hello World"


@pytest.mark.asyncio
async def test_favorite_dashboard_tool(
    mcp_with_dash_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.favorite_dashboard.return_value = {"status": "ok"}
    result = await mcp_with_dash_tools.call_tool("favorite_dashboard", {"dashboard_id": 1})
    data = json.loads(result.content[0].text)
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_unfavorite_dashboard_tool(
    mcp_with_dash_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.unfavorite_dashboard.return_value = {"status": "ok"}
    result = await mcp_with_dash_tools.call_tool("unfavorite_dashboard", {"dashboard_id": 1})
    data = json.loads(result.content[0].text)
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_revert_dashboard_tool(mcp_with_dash_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.revert_dashboard.return_value = {"id": 1}
    result = await mcp_with_dash_tools.call_tool(
        "revert_dashboard",
        {
            "dashboard_id": 1,
            "revision_id": 10,
        },
    )
    mock_client.revert_dashboard.assert_awaited_once_with(1, 10)
    data = json.loads(result.content[0].text)
    assert data["id"] == 1


@pytest.mark.asyncio
async def test_save_dashboard_tool(mcp_with_dash_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.save_dashboard.return_value = {"id": 1}
    result = await mcp_with_dash_tools.call_tool(
        "save_dashboard",
        {
            "dashboard": {"name": "Test"},
        },
    )
    data = json.loads(result.content[0].text)
    assert data["id"] == 1


@pytest.mark.asyncio
async def test_save_dashboard_to_collection_tool(
    mcp_with_dash_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.save_dashboard_to_collection.return_value = {"id": 1}
    result = await mcp_with_dash_tools.call_tool(
        "save_dashboard_to_collection",
        {
            "parent_collection_id": 5,
            "dashboard": {"name": "Test"},
        },
    )
    mock_client.save_dashboard_to_collection.assert_awaited_once()
    data = json.loads(result.content[0].text)
    assert data["id"] == 1


@pytest.mark.asyncio
async def test_update_dashboard_cards_tool(
    mcp_with_dash_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.update_dashboard_cards.return_value = {"id": 1, "dashcards": []}
    result = await mcp_with_dash_tools.call_tool(
        "update_dashboard_cards",
        {
            "dashboard_id": 1,
            "cards": [{"id": 10}],
        },
    )
    data = json.loads(result.content[0].text)
    assert data["id"] == 1


@pytest.mark.asyncio
async def test_update_dashcard_tool(mcp_with_dash_tools: FastMCP, mock_client: AsyncMock) -> None:
    mock_client.update_dashcard.return_value = {"id": 1}
    result = await mcp_with_dash_tools.call_tool(
        "update_dashcard",
        {
            "dashboard_id": 1,
            "dashcard_id": 10,
            "updates": {"size_x": 6},
        },
    )
    data = json.loads(result.content[0].text)
    assert data["id"] == 1


@pytest.mark.asyncio
async def test_create_public_link_tool(
    mcp_with_dash_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.create_dashboard_public_link.return_value = {"uuid": "abc-123"}
    result = await mcp_with_dash_tools.call_tool("create_public_link", {"dashboard_id": 1})
    data = json.loads(result.content[0].text)
    assert data["uuid"] == "abc-123"


@pytest.mark.asyncio
async def test_delete_public_link_tool(
    mcp_with_dash_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.delete_dashboard_public_link.return_value = None
    result = await mcp_with_dash_tools.call_tool("delete_public_link", {"dashboard_id": 1})
    data = json.loads(result.content[0].text)
    assert data["status"] == "success"


@pytest.mark.asyncio
async def test_remove_cards_from_dashboard_tool(
    mcp_with_dash_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.remove_cards_from_dashboard.return_value = {"id": 1, "dashcards": []}
    result = await mcp_with_dash_tools.call_tool(
        "remove_cards_from_dashboard",
        {
            "dashboard_id": 1,
            "dashcard_ids": [10, 20],
        },
    )
    data = json.loads(result.content[0].text)
    assert data["id"] == 1


# ── Tests for dashboard helper functions ──────────────────────────────


def test_resolve_field_ref_with_known_field() -> None:
    field_lookup = {10: {"name": "user_id", "table": "users"}}
    result = _resolve_field_ref(["field", 10], field_lookup)
    assert result == ["field", "user_id"]


def test_resolve_field_ref_with_unknown_field() -> None:
    result = _resolve_field_ref(["field", 99], {})
    assert result == ["field", "field_99"]


def test_resolve_field_ref_with_options() -> None:
    field_lookup = {10: {"name": "created_at", "table": "orders"}}
    result = _resolve_field_ref(["field", 10, {"temporal-unit": "month"}], field_lookup)
    assert result == ["field", "created_at", {"temporal-unit": "month"}]


def test_resolve_field_ref_non_field() -> None:
    result = _resolve_field_ref("plain_string", {})
    assert result == "plain_string"


def test_resolve_field_ref_nested() -> None:
    field_lookup = {10: {"name": "amount", "table": "orders"}}
    result = _resolve_field_ref([">", ["field", 10], 100], field_lookup)
    assert result == [">", ["field", "amount"], 100]


def test_resolve_mbql_basic() -> None:
    query = {
        "source-table": 1,
        "aggregation": [["count"]],
        "breakout": [["field", 10]],
        "filter": [">", ["field", 10], 100],
    }
    table_names = {1: "public.orders"}
    field_lookup = {10: {"name": "amount", "table": "public.orders"}}
    result = _resolve_mbql(query, table_names, field_lookup)
    assert result["source-table"] == "public.orders"
    assert result["filter"] == [">", ["field", "amount"], 100]


def test_resolve_mbql_with_joins() -> None:
    query = {
        "source-table": 1,
        "joins": [
            {
                "source-table": 2,
                "condition": ["=", ["field", 10], ["field", 20]],
            }
        ],
    }
    table_names = {1: "orders", 2: "users"}
    field_lookup = {
        10: {"name": "user_id", "table": "orders"},
        20: {"name": "id", "table": "users"},
    }
    result = _resolve_mbql(query, table_names, field_lookup)
    assert result["joins"][0]["source-table"] == "users"


def test_resolve_mbql_empty() -> None:
    assert _resolve_mbql({}, {}, {}) == {}


def test_process_dashcard_virtual() -> None:
    dc = {
        "id": 1,
        "card_id": None,
        "visualization_settings": {"text": "Hello"},
    }
    result = _process_dashcard(dc, {}, {}, {})
    assert result["query_type"] == "virtual"
    assert result["text"] == "Hello"


def test_process_dashcard_native() -> None:
    dc = {
        "id": 2,
        "card_id": 5,
        "card": {
            "name": "SQL Card",
            "dataset_query": {
                "type": "native",
                "database": 1,
                "native": {
                    "query": "SELECT 1",
                    "template-tags": {"tag1": {}},
                },
            },
        },
    }
    result = _process_dashcard(dc, {}, {}, {})
    assert result["query_type"] == "native"
    assert result["sql"] == "SELECT 1"
    assert result["template_tags"] == ["tag1"]


def test_process_dashcard_mbql() -> None:
    dc = {
        "id": 3,
        "card_id": 10,
        "card": {
            "name": "MBQL Card",
            "dataset_query": {
                "type": "query",
                "database": 1,
                "query": {"source-table": 1},
            },
        },
    }
    table_names = {1: "orders"}
    result = _process_dashcard(dc, {}, table_names, {})
    assert result["query_type"] == "mbql"
    assert result["mbql"]["source-table"] == "orders"


def test_process_dashcard_with_tab() -> None:
    dc = {
        "id": 4,
        "card_id": 10,
        "dashboard_tab_id": 1,
        "card": {
            "name": "Card",
            "dataset_query": {"type": "native", "native": {"query": "SELECT 1"}},
        },
    }
    tab_lookup = {1: "Tab A"}
    result = _process_dashcard(dc, tab_lookup, {}, {})
    assert result["tab"] == "Tab A"


@pytest.mark.asyncio
async def test_get_dashboard_queries_tool(
    mcp_with_dash_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.get_dashboard.return_value = {
        "id": 1,
        "name": "Test Dash",
        "dashcards": [
            {
                "id": 10,
                "card_id": 5,
                "card": {
                    "name": "Native Q",
                    "dataset_query": {
                        "type": "native",
                        "database": 1,
                        "native": {"query": "SELECT 1"},
                    },
                },
            },
        ],
        "tabs": [],
    }
    result = await mcp_with_dash_tools.call_tool("get_dashboard_queries", {"dashboard_id": 1})
    data = json.loads(result.content[0].text)
    assert data["total_cards"] == 1
    assert data["cards"][0]["query_type"] == "native"


@pytest.mark.asyncio
async def test_audit_dashboard_filters_tool(
    mcp_with_dash_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.get_dashboard.return_value = {
        "id": 1,
        "dashcards": [
            {
                "id": 10,
                "card_id": 5,
                "card": {"name": "Card", "dataset_query": {}},
                "parameter_mappings": [
                    {
                        "parameter_id": "p1",
                        "target": ["dimension", ["field", 1], {"stage-number": 0}],
                    }
                ],
            },
        ],
        "parameters": [
            {"id": "p1", "name": "Filter 1"},
            {"id": "p2", "name": "Filter 2"},
        ],
    }
    result = await mcp_with_dash_tools.call_tool("audit_dashboard_filters", {"dashboard_id": 1})
    data = json.loads(result.content[0].text)
    assert data["total_parameters"] == 2
    assert data["cards_with_issues"] == 1  # p2 is missing
    assert data["all_cards"][0]["missing_params"] == ["p2"]


@pytest.mark.asyncio
async def test_audit_dashboard_filters_missing_stage(
    mcp_with_dash_tools: FastMCP, mock_client: AsyncMock
) -> None:
    """Test that missing stage-number is flagged."""
    mock_client.get_dashboard.return_value = {
        "id": 1,
        "dashcards": [
            {
                "id": 10,
                "card_id": 5,
                "card": {"name": "Card", "dataset_query": {}},
                "parameter_mappings": [
                    {"parameter_id": "p1", "target": ["dimension", ["field", 1]]},
                ],
            },
        ],
        "parameters": [{"id": "p1"}],
    }
    result = await mcp_with_dash_tools.call_tool("audit_dashboard_filters", {"dashboard_id": 1})
    data = json.loads(result.content[0].text)
    assert len(data["all_cards"][0]["errors"]) == 1
    assert "stage-number" in data["all_cards"][0]["errors"][0]


# ── Dashboard tab tools ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_dashboard_tab_tool(
    mcp_with_dash_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.create_dashboard_tab.return_value = {"id": 10, "name": "Overview"}
    result = await mcp_with_dash_tools.call_tool(
        "create_dashboard_tab",
        {"dashboard_id": 1, "name": "Overview"},
    )
    mock_client.create_dashboard_tab.assert_awaited_once_with(1, "Overview")
    data = json.loads(result.content[0].text)
    assert data["name"] == "Overview"
    assert data["id"] == 10


@pytest.mark.asyncio
async def test_update_dashboard_tab_tool(
    mcp_with_dash_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.update_dashboard_tab.return_value = {"id": 10, "name": "Renamed"}
    result = await mcp_with_dash_tools.call_tool(
        "update_dashboard_tab",
        {"dashboard_id": 1, "tab_id": 10, "name": "Renamed"},
    )
    mock_client.update_dashboard_tab.assert_awaited_once_with(1, 10, "Renamed")
    data = json.loads(result.content[0].text)
    assert data["name"] == "Renamed"


@pytest.mark.asyncio
async def test_delete_dashboard_tab_tool(
    mcp_with_dash_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.delete_dashboard_tab.return_value = None
    result = await mcp_with_dash_tools.call_tool(
        "delete_dashboard_tab",
        {"dashboard_id": 1, "tab_id": 10},
    )
    mock_client.delete_dashboard_tab.assert_awaited_once_with(1, 10)
    data = json.loads(result.content[0].text)
    assert data["status"] == "success"
    assert data["tab_id"] == 10
    assert data["action"] == "deleted"


# ── Dashboard parameter tools ───────────────────────────────────────


@pytest.mark.asyncio
async def test_get_dashboard_param_values_tool(
    mcp_with_dash_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.get_dashboard_param_values.return_value = {
        "values": [["Gadget"], ["Widget"]],
        "has_more_values": False,
    }
    result = await mcp_with_dash_tools.call_tool(
        "get_dashboard_param_values",
        {"dashboard_id": 1, "param_key": "abc123"},
    )
    mock_client.get_dashboard_param_values.assert_awaited_once_with(1, "abc123")
    data = json.loads(result.content[0].text)
    assert len(data["values"]) == 2
    assert data["has_more_values"] is False


@pytest.mark.asyncio
async def test_search_dashboard_param_values_tool(
    mcp_with_dash_tools: FastMCP, mock_client: AsyncMock
) -> None:
    mock_client.search_dashboard_param_values.return_value = {
        "values": [["Gadget"]],
        "has_more_values": False,
    }
    result = await mcp_with_dash_tools.call_tool(
        "search_dashboard_param_values",
        {"dashboard_id": 1, "param_key": "abc123", "query": "Gad"},
    )
    mock_client.search_dashboard_param_values.assert_awaited_once_with(1, "abc123", "Gad")
    data = json.loads(result.content[0].text)
    assert data["values"] == [["Gadget"]]
