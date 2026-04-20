"""Core Metabase streams enabled by default."""

from __future__ import annotations

from typing import Any

from tap_metabase.client import ensure_record_dict
from tap_metabase.client import iter_table_fields
from tap_metabase.client import stable_record_id
from tap_metabase.streams.base import MetabaseSingletonStream
from tap_metabase.streams.base import MetabaseStream


class UsersStream(MetabaseStream):
    name = "users"
    path = "user"
    primary_keys = ["id"]


class ActivityStream(MetabaseStream):
    name = "activity"
    path = "activity"
    primary_keys = ["id"]
    replication_key = "timestamp"
    supports_pagination = True
    soft_fail = True


class PermissionGroupsStream(MetabaseStream):
    name = "permission_groups"
    path = "permissions/group"
    primary_keys = ["id"]


class PermissionsGraphStream(MetabaseSingletonStream):
    name = "permissions_graph"
    path = "permissions/graph"
    primary_keys = ["_record_id"]


class CollectionsStream(MetabaseStream):
    name = "collections"
    path = "collection"
    primary_keys = ["id"]


class DashboardsStream(MetabaseStream):
    name = "dashboards"
    path = "dashboard"
    primary_keys = ["id"]

    def get_child_context(
        self,
        record: dict[str, Any],
        context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        return {"dashboard_id": record.get("id")}


class DashboardCardsStream(MetabaseStream):
    name = "dashboard_cards"
    path = "dashboard/{dashboard_id}"
    parent_stream_type = DashboardsStream
    primary_keys = ["id"]

    def parse_response(self, response: Any) -> Any:
        payload = response.json()
        dashcards = payload.get("dashcards", []) if isinstance(payload, dict) else []
        for dashcard in dashcards:
            record = ensure_record_dict(dashcard)
            if "id" not in record:
                record["id"] = stable_record_id("dashboard_card", record)
            yield record

    def post_process(self, row: dict[str, Any], context: dict | None = None) -> dict[str, Any]:
        row["dashboard_id"] = (context or {}).get("dashboard_id")
        return row


class CardsStream(MetabaseStream):
    name = "cards"
    path = "card"
    primary_keys = ["id"]

    def get_child_context(
        self,
        record: dict[str, Any],
        context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        return {"card_id": record.get("id")}


class CardDetailsStream(MetabaseStream):
    name = "card_details"
    path = "card/{card_id}"
    parent_stream_type = CardsStream
    primary_keys = ["id"]

    def parse_response(self, response: Any) -> Any:
        record = ensure_record_dict(response.json())
        yield record

    def post_process(self, row: dict[str, Any], context: dict | None = None) -> dict[str, Any]:
        if "id" not in row:
            row["id"] = (context or {}).get("card_id")
        if "id" not in row:
            row["id"] = stable_record_id("card_detail", row)
        return row


class DatabasesStream(MetabaseStream):
    name = "databases"
    path = "database"
    primary_keys = ["id"]

    def get_child_context(
        self,
        record: dict[str, Any],
        context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        return {"database_id": record.get("id")}


class TablesStream(MetabaseStream):
    name = "tables"
    path = "database/{database_id}/metadata"
    parent_stream_type = DatabasesStream
    primary_keys = ["id"]

    def parse_response(self, response: Any) -> Any:
        payload = response.json()
        tables = payload.get("tables", []) if isinstance(payload, dict) else []
        for table in tables:
            record = ensure_record_dict(table)
            if "id" not in record:
                record["id"] = stable_record_id("table", record)
            yield record

    def post_process(self, row: dict[str, Any], context: dict | None = None) -> dict[str, Any]:
        row["database_id"] = (context or {}).get("database_id")
        return row


class FieldsStream(MetabaseStream):
    name = "fields"
    path = "database/{database_id}/metadata"
    parent_stream_type = DatabasesStream
    primary_keys = ["id"]

    def parse_response(self, response: Any) -> Any:
        payload = response.json()
        tables = payload.get("tables", []) if isinstance(payload, dict) else []
        for table in tables:
            table_record = ensure_record_dict(table)
            table_id = table_record.get("id")
            for field in iter_table_fields(table_record):
                record = ensure_record_dict(field)
                record["table_id"] = table_id
                if "id" not in record:
                    record["id"] = stable_record_id("field", record)
                yield record

    def post_process(self, row: dict[str, Any], context: dict | None = None) -> dict[str, Any]:
        row["database_id"] = (context or {}).get("database_id")
        return row


class SegmentsStream(MetabaseStream):
    name = "segments"
    path = "segment"
    primary_keys = ["id"]


class PulsesStream(MetabaseStream):
    name = "pulses"
    path = "pulse"
    primary_keys = ["id"]
    soft_fail = True


class AlertsStream(MetabaseStream):
    name = "alerts"
    path = "alert"
    primary_keys = ["id"]
    soft_fail = True


class TimelinesStream(MetabaseStream):
    name = "timelines"
    path = "timeline"
    primary_keys = ["id"]
    soft_fail = True


class TimelineEventsStream(MetabaseStream):
    name = "timeline_events"
    path = "timeline-event"
    primary_keys = ["id"]
    replication_key = "timestamp"
    supports_pagination = True
    soft_fail = True


class TasksStream(MetabaseStream):
    name = "tasks"
    path = "task"
    primary_keys = ["id"]
    soft_fail = True
