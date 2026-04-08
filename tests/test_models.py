"""Tests for Pydantic models."""

from __future__ import annotations

from metabase_mcp.models import (
    Card,
    Collection,
    Dashboard,
    DashboardCard,
    Database,
    Field,
    PermissionGroup,
    QueryResult,
    Table,
    User,
)


def test_dashboard_with_minimal_data() -> None:
    d = Dashboard(id=1, name="Test")
    assert d.id == 1
    assert d.name == "Test"
    assert d.description is None


def test_dashboard_extra_fields_allowed() -> None:
    d = Dashboard(id=1, name="Test", unknown_field="value")  # type: ignore[call-arg]
    assert d.id == 1
    assert d.model_extra == {"unknown_field": "value"}


def test_dashboard_full_data() -> None:
    d = Dashboard(
        id=1,
        name="Test Dashboard",
        description="A test",
        collection_id=5,
        archived=False,
        parameters=[{"id": "p1", "type": "string"}],
        dashcards=[{"id": 10, "card_id": 3}],
    )
    assert d.collection_id == 5
    assert len(d.parameters) == 1  # type: ignore[arg-type]
    assert len(d.dashcards) == 1  # type: ignore[arg-type]


def test_card_model() -> None:
    c = Card(id=1, name="Q1", display="table")
    assert c.display == "table"
    assert c.dataset_query is None


def test_database_model() -> None:
    db = Database(id=1, name="PG", engine="postgres")
    assert db.engine == "postgres"


def test_table_model() -> None:
    t = Table(id=1, name="users", database_id=1)
    assert t.database_id == 1


def test_field_model() -> None:
    f = Field(id=1, name="email", base_type="type/Text")
    assert f.base_type == "type/Text"


def test_collection_model() -> None:
    c = Collection(id=1, name="My Collection")
    assert c.parent_id is None


def test_user_model() -> None:
    u = User(id=1, email="test@test.com", is_superuser=True)
    assert u.is_superuser is True


def test_permission_group_model() -> None:
    pg = PermissionGroup(id=1, name="Admins")
    assert pg.name == "Admins"


def test_dashboard_card_model() -> None:
    dc = DashboardCard(id=1, card_id=5, dashboard_id=2, size_x=12, size_y=8)
    assert dc.size_x == 12


def test_query_result_model() -> None:
    qr = QueryResult(data={"rows": [[1]]}, status="completed", row_count=1)
    assert qr.status == "completed"
    assert qr.row_count == 1


def test_all_models_accept_none() -> None:
    """All models should work with no arguments (all fields optional)."""
    all_models = [
        Dashboard, DashboardCard, Card, Database, Table,
        Field, Collection, User, PermissionGroup, QueryResult,
    ]
    for model_cls in all_models:
        instance = model_cls()
        assert instance is not None
