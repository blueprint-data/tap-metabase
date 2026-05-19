"""Shared stream primitives for tap-metabase."""

from __future__ import annotations

import json
from typing import Any

import backoff
from requests.exceptions import JSONDecodeError as RequestsJSONDecodeError
from singer_sdk.exceptions import FatalAPIError
from singer_sdk.exceptions import RetriableAPIError
from singer_sdk.pagination import BasePageNumberPaginator
from singer_sdk.streams import RESTStream

from tap_metabase.client import DEFAULT_TIMEOUT_SECONDS
from tap_metabase.client import DEFAULT_BACKOFF_FACTOR
from tap_metabase.client import DEFAULT_MAX_RETRIES
from tap_metabase.client import build_api_url_base
from tap_metabase.client import build_default_headers
from tap_metabase.client import ensure_record_dict
from tap_metabase.client import extract_json_records
from tap_metabase.client import stable_record_id


GENERIC_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "_record_id": {"type": ["string", "null"]},
        "id": {"type": ["integer", "string", "null"]},
        "name": {"type": ["string", "null"]},
        "created_at": {"type": ["string", "null"]},
        "updated_at": {"type": ["string", "null"]},
        "timestamp": {"type": ["string", "null"]},
    },
    "additionalProperties": True,
}


class OptionalEndpointUnavailable(Exception):
    """Raised when an optional endpoint is not available."""


class MetabasePageNumberPaginator(BasePageNumberPaginator):
    """Paginator for Metabase endpoints that expose page metadata."""

    def __init__(self, page_size: int, start_value: int = 1) -> None:
        super().__init__(start_value=start_value)
        self.page_size = page_size

    def has_more(self, response: Any) -> bool:
        payload = response.json()
        if not isinstance(payload, dict):
            return False

        if payload.get("next_page"):
            return True

        next_value = payload.get("next")
        if next_value:
            return True

        has_more = payload.get("has_more")
        if isinstance(has_more, bool):
            return has_more

        total = payload.get("total")
        if isinstance(total, int):
            page = payload.get("page", self.current_value)
            return int(page) * self.page_size < total

        data = payload.get("data")
        if isinstance(data, list) and "page" in payload:
            return len(data) >= self.page_size

        return False

    def get_next(self, response: Any) -> int | None:
        payload = response.json()
        if isinstance(payload, dict):
            next_page = payload.get("next_page")
            if isinstance(next_page, int):
                return next_page

            next_value = payload.get("next")
            if isinstance(next_value, int):
                return next_value

        return super().get_next(response)


class MetabaseStream(RESTStream):
    """Base Metabase REST stream."""

    schema = GENERIC_SCHEMA
    primary_keys: list[str] = ["id"]
    replication_key: str | None = None
    soft_fail = False
    soft_fail_statuses: set[int] = {404, 405}
    supports_pagination = False
    page_size = 200
    ignore_parent_replication_keys = True

    @property
    def url_base(self) -> str:
        return build_api_url_base(self.config["host"])

    @property
    def http_headers(self) -> dict[str, str]:
        headers = super().http_headers or {}
        headers.update(build_default_headers(self.config["api_key"]))
        return headers

    @property
    def request_timeout(self) -> float:
        return float(self.config.get("timeout_seconds", DEFAULT_TIMEOUT_SECONDS))

    def backoff_max_tries(self) -> int:
        """Return configured max retries for transient failures."""
        return int(self.config.get("max_retries", DEFAULT_MAX_RETRIES))

    def backoff_wait_generator(self) -> Any:
        """Return exponential backoff generator using configured factor."""
        factor = int(self.config.get("backoff_factor", DEFAULT_BACKOFF_FACTOR))
        return backoff.expo(factor=factor)

    @property
    def requests_session(self) -> Any:
        session = super().requests_session
        session.verify = bool(self.config.get("verify_ssl", True))
        return session

    def get_new_paginator(self) -> Any:
        if self.supports_pagination:
            return MetabasePageNumberPaginator(page_size=self.page_size, start_value=1)
        return None

    def validate_response(self, response: Any) -> None:
        status_code = response.status_code
        if self.soft_fail and status_code in self.soft_fail_statuses:
            raise OptionalEndpointUnavailable(
                f"Endpoint {self.path} is unavailable (status={status_code})."
            )
        super().validate_response(response)

    def get_records(self, context: dict | None = None) -> Any:
        try:
            yield from super().get_records(context)
        except OptionalEndpointUnavailable as exc:
            self.logger.warning("Skipping optional stream '%s': %s", self.name, exc)
            return
        except FatalAPIError as exc:
            if self.soft_fail:
                response = getattr(exc, "response", None)
                status_code = getattr(response, "status_code", None)
                self.logger.warning(
                    "Skipping soft-fail stream '%s': status=%s",
                    self.name,
                    status_code,
                )
                return
            raise
        except (json.JSONDecodeError, RequestsJSONDecodeError) as exc:
            if self.soft_fail:
                self.logger.warning(
                    "Skipping soft-fail stream '%s': invalid JSON in response: %s",
                    self.name,
                    exc,
                )
                return
            raise
        except RetriableAPIError as exc:
            if self.soft_fail:
                self.logger.warning(
                    "Skipping soft-fail stream '%s': retries exhausted: %s",
                    self.name,
                    exc,
                )
                return
            raise

    def get_url_params(self, context: dict | None, next_page_token: Any | None) -> dict[str, Any]:
        if not self.supports_pagination:
            return {}
        return {
            "page": next_page_token or 1,
            "per_page": self.page_size,
        }

    def parse_response(self, response: Any) -> Any:
        payload = response.json()
        for record in extract_json_records(payload):
            normalized = ensure_record_dict(record)
            if "id" not in normalized and "id" in self.primary_keys:
                normalized["id"] = stable_record_id(self.name, normalized)
            yield normalized


class MetabaseSingletonStream(MetabaseStream):
    """A stream where each API response maps to one record."""

    primary_keys = ["_record_id"]

    def parse_response(self, response: Any) -> Any:
        payload = response.json()
        record = ensure_record_dict(payload)
        record["_record_id"] = self.name
        yield record


class OptionalEndpointStream(MetabaseStream):
    """Configurable stream used for optional endpoint groups."""

    soft_fail = True
    soft_fail_statuses = {400, 403, 404, 405}

    def __init__(
        self,
        tap: Any,
        stream_name: str,
        endpoint_path: str,
        primary_keys: list[str] | None = None,
    ) -> None:
        self._endpoint_path = endpoint_path
        self.primary_keys = primary_keys or ["id"]
        super().__init__(tap=tap, name=stream_name)

    @property
    def path(self) -> str:
        return self._endpoint_path
