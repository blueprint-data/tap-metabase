"""Tap discovery tests."""

from tap_metabase.streams.base import GENERIC_SCHEMA
from tap_metabase.streams.core import CardDetailsStream
from tap_metabase.streams.core import DashboardsStream
from tap_metabase.streams.optional import OPTIONAL_ENDPOINT_GROUPS
from tap_metabase.tap import TapMetabase


def build_tap(**config):
    base = {
        "host": "https://example.metabaseapp.com",
        "api_key": "test-key",
    }
    base.update(config)
    return TapMetabase(config=base)


def test_discover_core_streams_only_by_default() -> None:
    tap = build_tap()
    names = {stream.name for stream in tap.discover_streams()}

    assert "users" in names
    assert "cards" in names
    assert "dashboard_cards" in names
    assert "tables" in names
    assert "fields" in names

    optional_names = {
        spec.stream_name
        for specs in OPTIONAL_ENDPOINT_GROUPS.values()
        for spec in specs
    }
    assert names.isdisjoint(optional_names)


def test_discover_streams_with_optional_groups() -> None:
    tap = build_tap(endpoint_groups=["content_management", "embedding_public"])
    names = {stream.name for stream in tap.discover_streams()}

    assert "revisions" in names
    assert "bookmarks" in names
    assert "public" in names
    assert "embed" in names
    assert "preview_embed" in names


_CORE_STREAM_NAMES = {
    "users", "activity", "permission_groups", "permissions_graph",
    "collections", "dashboards", "dashboard_cards", "cards",
    "card_details", "databases", "tables", "fields", "segments",
    "pulses", "alerts", "timelines", "timeline_events", "tasks",
}


def test_core_streams_have_explicit_schemas() -> None:
    tap = build_tap()
    for stream in tap.discover_streams():
        if stream.name in _CORE_STREAM_NAMES:
            assert stream.schema is not GENERIC_SCHEMA, (
                f"Stream '{stream.name}' still uses GENERIC_SCHEMA"
            )


def test_all_core_schemas_have_additional_properties_true() -> None:
    tap = build_tap()
    for stream in tap.discover_streams():
        if stream.name in _CORE_STREAM_NAMES:
            assert stream.schema.get("additionalProperties") is True, (
                f"Stream '{stream.name}' missing additionalProperties: True"
            )


def test_card_details_schema_has_required_fields() -> None:
    tap = build_tap()
    stream = next(s for s in tap.discover_streams() if s.name == "card_details")
    props = stream.schema["properties"]
    required = {
        "database_id", "database_name", "collection_id", "collection_name",
        "view_count", "creator_id", "display", "query_type",
        "dataset_query", "archived",
    }
    missing = required - props.keys()
    assert not missing, f"card_details schema missing: {missing}"


def test_dashboards_schema_has_required_fields() -> None:
    tap = build_tap()
    stream = next(s for s in tap.discover_streams() if s.name == "dashboards")
    props = stream.schema["properties"]
    required = {"view_count", "collection_id", "collection_name", "creator_id", "archived"}
    missing = required - props.keys()
    assert not missing, f"dashboards schema missing: {missing}"


def test_cards_schema_has_required_fields() -> None:
    tap = build_tap()
    stream = next(s for s in tap.discover_streams() if s.name == "cards")
    props = stream.schema["properties"]
    required = {"database_id", "collection_id", "view_count", "archived"}
    missing = required - props.keys()
    assert not missing, f"cards schema missing: {missing}"


def test_dashboards_post_process_flattens_collection_name() -> None:
    tap = build_tap()
    stream = DashboardsStream(tap=tap)

    # Derives from nested object when field is absent
    row = {"id": 1, "collection": {"id": 5, "name": "Marketing"}}
    assert stream.post_process(row)["collection_name"] == "Marketing"

    # Does NOT overwrite a value already provided by the API
    row_direct = {"id": 2, "collection_name": "Direct From API", "collection": None}
    assert stream.post_process(row_direct)["collection_name"] == "Direct From API"

    # Falls back to None when collection object is null and field absent
    row_null = {"id": 3, "collection": None}
    assert stream.post_process(row_null)["collection_name"] is None

    # Falls back to None when collection field entirely missing
    row_missing = {"id": 4}
    assert stream.post_process(row_missing)["collection_name"] is None


def test_card_details_post_process_flattens_nested_fields() -> None:
    tap = build_tap()
    stream = CardDetailsStream(tap=tap)

    row = {
        "id": 42,
        "database": {"id": 1, "name": "Production DB"},
        "collection": {"id": 7, "name": "Analytics"},
    }
    result = stream.post_process(row, context={"card_id": 42})
    assert result["database_name"] == "Production DB"
    assert result["collection_name"] == "Analytics"
    assert result["id"] == 42

    # Does NOT overwrite values already provided by the API
    row_direct = {
        "id": 10,
        "database_name": "Prod Direct",
        "collection_name": "Analytics Direct",
    }
    result_direct = stream.post_process(row_direct, context={"card_id": 10})
    assert result_direct["database_name"] == "Prod Direct"
    assert result_direct["collection_name"] == "Analytics Direct"

    row_null = {"database": None, "collection": None}
    result_null = stream.post_process(row_null, context={"card_id": 99})
    assert result_null["database_name"] is None
    assert result_null["collection_name"] is None
    assert result_null["id"] == 99
