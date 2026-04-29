"""Core Metabase streams enabled by default."""

from __future__ import annotations

from typing import Any

from tap_metabase.client import ensure_record_dict
from tap_metabase.client import iter_table_fields
from tap_metabase.client import stable_record_id
from tap_metabase.schemas import ACTIVITY_SCHEMA
from tap_metabase.schemas import ALERTS_SCHEMA
from tap_metabase.schemas import CARD_DETAILS_SCHEMA
from tap_metabase.schemas import CARDS_SCHEMA
from tap_metabase.schemas import COLLECTIONS_SCHEMA
from tap_metabase.schemas import DASHBOARD_CARDS_SCHEMA
from tap_metabase.schemas import DASHBOARDS_SCHEMA
from tap_metabase.schemas import DATABASES_SCHEMA
from tap_metabase.schemas import FIELDS_SCHEMA
from tap_metabase.schemas import PERMISSION_GROUPS_SCHEMA
from tap_metabase.schemas import PERMISSIONS_GRAPH_SCHEMA
from tap_metabase.schemas import PULSES_SCHEMA
from tap_metabase.schemas import SEGMENTS_SCHEMA
from tap_metabase.schemas import TABLES_SCHEMA
from tap_metabase.schemas import TASKS_SCHEMA
from tap_metabase.schemas import TIMELINE_EVENTS_SCHEMA
from tap_metabase.schemas import TIMELINES_SCHEMA
from tap_metabase.schemas import USERS_SCHEMA
from tap_metabase.streams.base import MetabaseSingletonStream
from tap_metabase.streams.base import MetabaseStream


class UsersStream(MetabaseStream):
    name = "users"
    path = "user"
    schema = USERS_SCHEMA
    primary_keys = ["id"]


class ActivityStream(MetabaseStream):
    name = "activity"
    path = "activity"
    schema = ACTIVITY_SCHEMA
    primary_keys = ["id"]
    replication_key = "timestamp"
    supports_pagination = True
    soft_fail = True


class PermissionGroupsStream(MetabaseStream):
    name = "permission_groups"
    path = "permissions/group"
    schema = PERMISSION_GROUPS_SCHEMA
    primary_keys = ["id"]


class PermissionsGraphStream(MetabaseSingletonStream):
    name = "permissions_graph"
    path = "permissions/graph"
    schema = PERMISSIONS_GRAPH_SCHEMA
    primary_keys = ["_record_id"]


class CollectionsStream(MetabaseStream):
    name = "collections"
    path = "collection"
    schema = COLLECTIONS_SCHEMA
    primary_keys = ["id"]


class DashboardsStream(MetabaseStream):
    name = "dashboards"
    path = "dashboard"
    schema = DASHBOARDS_SCHEMA
    primary_keys = ["id"]

    def get_child_context(
        self,
        record: dict[str, Any],
        context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        return {"dashboard_id": record.get("id")}

    def post_process(self, row: dict[str, Any], context: dict | None = None) -> dict[str, Any]:
        # /api/dashboard list returns collection_name directly; only derive from
        # nested object when the field is absent (older API versions or detail endpoints).
        if "collection_name" not in row:
            collection = row.get("collection") or {}
            row["collection_name"] = collection.get("name") if isinstance(collection, dict) else None
        return row


class DashboardCardsStream(MetabaseStream):
    name = "dashboard_cards"
    path = "dashboard/{dashboard_id}"
    schema = DASHBOARD_CARDS_SCHEMA
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
    schema = CARDS_SCHEMA
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
    schema = CARD_DETAILS_SCHEMA
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
        if "database_name" not in row:
            database = row.get("database") or {}
            row["database_name"] = database.get("name") if isinstance(database, dict) else None
        if "collection_name" not in row:
            collection = row.get("collection") or {}
            row["collection_name"] = collection.get("name") if isinstance(collection, dict) else None
        return row


class DatabasesStream(MetabaseStream):
    name = "databases"
    path = "database"
    schema = DATABASES_SCHEMA
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
    schema = TABLES_SCHEMA
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
    schema = FIELDS_SCHEMA
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
    schema = SEGMENTS_SCHEMA
    primary_keys = ["id"]


class PulsesStream(MetabaseStream):
    name = "pulses"
    path = "pulse"
    schema = PULSES_SCHEMA
    primary_keys = ["id"]
    soft_fail = True


class AlertsStream(MetabaseStream):
    name = "alerts"
    path = "alert"
    schema = ALERTS_SCHEMA
    primary_keys = ["id"]
    soft_fail = True


class TimelinesStream(MetabaseStream):
    name = "timelines"
    path = "timeline"
    schema = TIMELINES_SCHEMA
    primary_keys = ["id"]
    soft_fail = True


class TimelineEventsStream(MetabaseStream):
    name = "timeline_events"
    path = "timeline-event"
    schema = TIMELINE_EVENTS_SCHEMA
    primary_keys = ["id"]
    replication_key = "timestamp"
    supports_pagination = True
    soft_fail = True


class TasksStream(MetabaseStream):
    name = "tasks"
    path = "task"
    schema = TASKS_SCHEMA
    primary_keys = ["id"]
    soft_fail = True
