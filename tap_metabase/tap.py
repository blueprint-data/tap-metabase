"""Singer tap class for tap-metabase."""

from __future__ import annotations

from typing import Any

from singer_sdk import Tap
from singer_sdk import Stream

from tap_metabase.streams import OPTIONAL_ENDPOINT_GROUPS
from tap_metabase.streams import ActivityStream
from tap_metabase.streams import AlertsStream
from tap_metabase.streams import CardDetailsStream
from tap_metabase.streams import CardsStream
from tap_metabase.streams import CollectionsStream
from tap_metabase.streams import DashboardCardsStream
from tap_metabase.streams import DashboardsStream
from tap_metabase.streams import DatabasesStream
from tap_metabase.streams import FieldsStream
from tap_metabase.streams import PermissionGroupsStream
from tap_metabase.streams import PermissionsGraphStream
from tap_metabase.streams import PulsesStream
from tap_metabase.streams import SegmentsStream
from tap_metabase.streams import TablesStream
from tap_metabase.streams import TasksStream
from tap_metabase.streams import TimelineEventsStream
from tap_metabase.streams import TimelinesStream
from tap_metabase.streams import UsersStream
from tap_metabase.streams import build_optional_group_streams


class TapMetabase(Tap):
    """Metabase tap implementation."""

    name = "tap-metabase"

    config_jsonschema = {
        "type": "object",
        "required": ["host", "api_key"],
        "properties": {
            "host": {
                "type": "string",
                "title": "Metabase Host",
                "description": "Base URL for the Metabase instance.",
            },
            "api_key": {
                "type": "string",
                "title": "Metabase API Key",
                "secret": True,
            },
            "start_date": {
                "type": "string",
                "format": "date-time",
                "description": "Optional start date for incremental streams.",
            },
            "endpoint_groups": {
                "type": "array",
                "description": "Optional endpoint groups to include in discovery/sync.",
                "items": {
                    "type": "string",
                    "enum": sorted(OPTIONAL_ENDPOINT_GROUPS.keys()),
                },
                "default": [],
            },
            "timeout_seconds": {
                "type": "integer",
                "default": 30,
                "minimum": 1,
            },
            "max_retries": {
                "type": "integer",
                "default": 5,
                "minimum": 1,
            },
            "backoff_factor": {
                "type": "integer",
                "default": 2,
                "minimum": 1,
            },
            "verify_ssl": {
                "type": "boolean",
                "default": True,
            },
        },
        "additionalProperties": True,
    }

    def discover_streams(self) -> list[Stream]:
        """Return discovered streams for the tap."""
        streams: list[Stream] = [
            UsersStream(self),
            ActivityStream(self),
            PermissionGroupsStream(self),
            PermissionsGraphStream(self),
            CollectionsStream(self),
            DashboardsStream(self),
            DashboardCardsStream(self),
            CardsStream(self),
            CardDetailsStream(self),
            DatabasesStream(self),
            TablesStream(self),
            FieldsStream(self),
            SegmentsStream(self),
            PulsesStream(self),
            AlertsStream(self),
            TimelinesStream(self),
            TimelineEventsStream(self),
            TasksStream(self),
        ]

        raw_groups = self.config.get("endpoint_groups", [])
        enabled_groups = {group for group in raw_groups if group in OPTIONAL_ENDPOINT_GROUPS}
        streams.extend(build_optional_group_streams(self, enabled_groups))

        unknown_groups = sorted(set(raw_groups) - enabled_groups)
        if unknown_groups:
            self.logger.warning(
                "Ignoring unknown endpoint_groups values: %s",
                ", ".join(unknown_groups),
            )

        return streams


def cli() -> None:
    """Tap CLI entrypoint."""
    TapMetabase.cli()


if __name__ == "__main__":
    cli()
