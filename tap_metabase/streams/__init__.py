"""Stream exports for tap-metabase."""

from tap_metabase.streams.core import ActivityStream
from tap_metabase.streams.core import AlertsStream
from tap_metabase.streams.core import CardDetailsStream
from tap_metabase.streams.core import CardsStream
from tap_metabase.streams.core import CollectionsStream
from tap_metabase.streams.core import DashboardCardsStream
from tap_metabase.streams.core import DashboardsStream
from tap_metabase.streams.core import DatabasesStream
from tap_metabase.streams.core import FieldsStream
from tap_metabase.streams.core import PermissionGroupsStream
from tap_metabase.streams.core import PermissionsGraphStream
from tap_metabase.streams.core import PulsesStream
from tap_metabase.streams.core import SegmentsStream
from tap_metabase.streams.core import TablesStream
from tap_metabase.streams.core import TasksStream
from tap_metabase.streams.core import TimelineEventsStream
from tap_metabase.streams.core import TimelinesStream
from tap_metabase.streams.core import UsersStream
from tap_metabase.streams.optional import OPTIONAL_ENDPOINT_GROUPS
from tap_metabase.streams.optional import build_optional_group_streams

__all__ = [
    "OPTIONAL_ENDPOINT_GROUPS",
    "ActivityStream",
    "AlertsStream",
    "CardDetailsStream",
    "CardsStream",
    "CollectionsStream",
    "DashboardCardsStream",
    "DashboardsStream",
    "DatabasesStream",
    "FieldsStream",
    "PermissionGroupsStream",
    "PermissionsGraphStream",
    "PulsesStream",
    "SegmentsStream",
    "TablesStream",
    "TasksStream",
    "TimelineEventsStream",
    "TimelinesStream",
    "UsersStream",
    "build_optional_group_streams",
]
