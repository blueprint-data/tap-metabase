"""Tests for Metabase client helpers."""

from tap_metabase.client import build_api_url_base
from tap_metabase.client import build_default_headers
from tap_metabase.client import ensure_record_dict
from tap_metabase.client import extract_json_records
from tap_metabase.client import normalize_host
from tap_metabase.client import stable_record_id


def test_normalize_host_trims_trailing_slash() -> None:
    assert normalize_host("https://acme.metabaseapp.com/") == "https://acme.metabaseapp.com"


def test_build_api_url_base_handles_existing_api_suffix() -> None:
    assert build_api_url_base("https://acme.metabaseapp.com/api") == "https://acme.metabaseapp.com/api/"
    assert build_api_url_base("https://acme.metabaseapp.com") == "https://acme.metabaseapp.com/api/"


def test_build_default_headers_contains_api_key() -> None:
    headers = build_default_headers("token")
    assert headers["x-api-key"] == "token"
    assert headers["Content-Type"] == "application/json"


def test_extract_json_records_handles_common_shapes() -> None:
    assert extract_json_records([{"id": 1}]) == [{"id": 1}]
    assert extract_json_records({"data": [{"id": 2}]}) == [{"id": 2}]
    assert extract_json_records({"results": [{"id": 3}]}) == [{"id": 3}]
    assert extract_json_records({"id": 4}) == [{"id": 4}]


def test_ensure_record_dict_for_scalars() -> None:
    assert ensure_record_dict("x") == {"value": "x"}
    assert ensure_record_dict(1) == {"value": 1}
    assert ensure_record_dict({"id": 1}) == {"id": 1}


def test_stable_record_id_is_deterministic() -> None:
    first = stable_record_id("stream", {"b": 2, "a": 1})
    second = stable_record_id("stream", {"a": 1, "b": 2})
    assert first == second
