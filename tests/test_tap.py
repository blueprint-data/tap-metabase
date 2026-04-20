"""Tap discovery tests."""

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
