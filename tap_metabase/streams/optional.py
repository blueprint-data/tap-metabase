"""Optional Metabase streams, enabled via endpoint groups config."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tap_metabase.streams.base import OptionalEndpointStream


@dataclass(frozen=True)
class OptionalEndpointSpec:
    """Configuration for one optional endpoint stream."""

    stream_name: str
    endpoint_path: str
    primary_keys: list[str] | None = None
    replication_key: str | None = None
    supports_pagination: bool = False


class OptionalConfiguredStream(OptionalEndpointStream):
    """Optional stream with configurable replication and pagination."""

    def __init__(
        self,
        tap: Any,
        stream_name: str,
        endpoint_path: str,
        primary_keys: list[str] | None = None,
        replication_key: str | None = None,
        supports_pagination: bool = False,
    ) -> None:
        self.replication_key = replication_key
        self.supports_pagination = supports_pagination
        super().__init__(
            tap=tap,
            stream_name=stream_name,
            endpoint_path=endpoint_path,
            primary_keys=primary_keys,
        )


OPTIONAL_ENDPOINT_GROUPS: dict[str, list[OptionalEndpointSpec]] = {
    "content_management": [
        OptionalEndpointSpec("revisions", "revision", replication_key="timestamp"),
        OptionalEndpointSpec("bookmarks", "bookmark"),
        OptionalEndpointSpec("search", "search"),
        OptionalEndpointSpec("serialization", "serialization"),
    ],
    "platform_admin": [
        OptionalEndpointSpec("login_history", "login-history", replication_key="timestamp"),
        OptionalEndpointSpec("settings", "setting"),
        OptionalEndpointSpec("email_settings", "email"),
        OptionalEndpointSpec("notify", "notify"),
        OptionalEndpointSpec("routes", "routes"),
        OptionalEndpointSpec("util", "util"),
        OptionalEndpointSpec("premium_features", "premium-features"),
    ],
    "embedding_public": [
        OptionalEndpointSpec("public", "public"),
        OptionalEndpointSpec("embed", "embed"),
        OptionalEndpointSpec("preview_embed", "preview-embed"),
    ],
    "niche_experimental": [
        OptionalEndpointSpec("actions", "action"),
        OptionalEndpointSpec("channels", "channel"),
        OptionalEndpointSpec("tiles", "tiles"),
        OptionalEndpointSpec("stale", "stale"),
        OptionalEndpointSpec("model_index", "model-index"),
        OptionalEndpointSpec("native_query_snippets", "native-query-snippet"),
        OptionalEndpointSpec("metabot", "metabot"),
        OptionalEndpointSpec("llm", "llm"),
        OptionalEndpointSpec("persist", "persist"),
        OptionalEndpointSpec("cloud_migration", "cloud-migration"),
        OptionalEndpointSpec("scim", "scim"),
        OptionalEndpointSpec("sso_saml", "sso-saml"),
        OptionalEndpointSpec("google", "google"),
        OptionalEndpointSpec("ldap", "ldap"),
        OptionalEndpointSpec("geojson", "geojson"),
        OptionalEndpointSpec("cache", "cache"),
        OptionalEndpointSpec("api_keys", "api-key"),
        OptionalEndpointSpec("automagic_dashboards", "automagic-dashboards"),
    ],
}


def build_optional_group_streams(tap: Any, enabled_groups: set[str]) -> list[Any]:
    """Build optional streams from enabled group names."""
    streams: list[Any] = []
    for group in sorted(enabled_groups):
        for spec in OPTIONAL_ENDPOINT_GROUPS.get(group, []):
            streams.append(
                OptionalConfiguredStream(
                    tap=tap,
                    stream_name=spec.stream_name,
                    endpoint_path=spec.endpoint_path,
                    primary_keys=spec.primary_keys,
                    replication_key=spec.replication_key,
                    supports_pagination=spec.supports_pagination,
                )
            )
    return streams
