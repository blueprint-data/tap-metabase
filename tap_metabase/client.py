"""HTTP helpers for the Metabase tap."""

from __future__ import annotations

import json
from collections.abc import Iterable
from collections.abc import Iterator
from typing import Any


DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_MAX_RETRIES = 5
DEFAULT_BACKOFF_FACTOR = 2


def normalize_host(host: str) -> str:
    """Return a normalized host URL without trailing slash."""
    return host.rstrip("/")


def build_api_url_base(host: str) -> str:
    """Build the REST stream base URL ending in `/api/`."""
    normalized = normalize_host(host)
    if normalized.endswith("/api"):
        return f"{normalized}/"
    return f"{normalized}/api/"


def build_default_headers(api_key: str) -> dict[str, str]:
    """Build default headers for Metabase API requests."""
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "x-api-key": api_key,
    }


def extract_json_records(payload: Any) -> list[Any]:
    """Extract records from common Metabase response payload shapes."""
    if payload is None:
        return []
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        return [payload]

    for key in ("data", "items", "results", "rows"):
        candidate = payload.get(key)
        if isinstance(candidate, list):
            return candidate

    for key in ("dashcards", "tables", "fields"):
        candidate = payload.get(key)
        if isinstance(candidate, list):
            return candidate

    return [payload]


def ensure_record_dict(record: Any) -> dict[str, Any]:
    """Coerce a payload entry into a dictionary."""
    if isinstance(record, dict):
        return record
    if isinstance(record, (str, int, float, bool)) or record is None:
        return {"value": record}
    if isinstance(record, Iterable):
        return {"value": list(record)}
    return {"value": str(record)}


def stable_record_id(prefix: str, record: Any) -> str:
    """Generate a deterministic record id for payloads without natural keys."""
    serialized = json.dumps(record, sort_keys=True, default=str)
    return f"{prefix}:{serialized}"


def iter_table_fields(table: dict[str, Any]) -> Iterator[dict[str, Any]]:
    """Iterate table field records if present."""
    fields = table.get("fields")
    if not isinstance(fields, list):
        return iter(())

    def _generator() -> Iterator[dict[str, Any]]:
        for field in fields:
            if isinstance(field, dict):
                yield field
            else:
                yield {"value": field}

    return _generator()
