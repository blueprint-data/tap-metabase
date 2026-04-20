# tap-metabase

Singer/Meltano tap for extracting Metabase metadata through the non-enterprise API surface (`/api/*`, excluding `/api/ee/*`).

## What This Tap Extracts

`tap-metabase` is metadata-focused in v1. It extracts admin and analytics entities (users, cards, dashboards, collections, databases, tables, fields, permissions, etc.) and does **not** run query-result extraction streams (`/api/dataset`, saved question row pulls).

## Installation

### Local (editable)

```bash
python3 -m pip install -e ".[dev]"
```

### Meltano project usage

This repository includes a local `meltano.yml` extractor definition with:

- plugin name: `tap-metabase`
- executable: `tap-metabase`
- pip URL: `-e .`

## Configuration

Required settings:

- `host`: Metabase base URL, e.g. `https://company.metabaseapp.com`
- `api_key`: Metabase API key (`x-api-key` auth)

Optional settings:

- `start_date`: Start date for incremental-capable streams
- `endpoint_groups`: Optional endpoint families to enable
- `timeout_seconds`: HTTP timeout (default `30`)
- `max_retries`: Retry attempts for transient errors (default `5`)
- `backoff_factor`: Exponential backoff factor (default `2`)
- `verify_ssl`: TLS cert verification (default `true`)

### Config JSON example

```json
{
  "host": "https://company.metabaseapp.com",
  "api_key": "mb_xxx",
  "endpoint_groups": ["content_management", "platform_admin"],
  "timeout_seconds": 30,
  "max_retries": 5,
  "backoff_factor": 2,
  "verify_ssl": true
}
```

## Streams

### Core streams (default enabled)

- `users` (`/api/user`)
- `activity` (`/api/activity`) - incremental by `timestamp`, soft-skips if unavailable
- `permission_groups` (`/api/permissions/group`)
- `permissions_graph` (`/api/permissions/graph`)
- `collections` (`/api/collection`)
- `dashboards` (`/api/dashboard`)
- `dashboard_cards` (`/api/dashboard/{dashboard_id}`)
- `cards` (`/api/card`)
- `card_details` (`/api/card/{card_id}`)
- `databases` (`/api/database`)
- `tables` (`/api/database/{database_id}/metadata`)
- `fields` (`/api/database/{database_id}/metadata`)
- `segments` (`/api/segment`)
- `pulses` (`/api/pulse`) - soft-skips if unavailable
- `alerts` (`/api/alert`) - soft-skips if unavailable
- `timelines` (`/api/timeline`) - soft-skips if unavailable
- `timeline_events` (`/api/timeline-event`) - incremental by `timestamp`, soft-skips if unavailable
- `tasks` (`/api/task`) - soft-skips if unavailable

### Optional endpoint groups (`endpoint_groups`)

- `content_management`: `revisions`, `bookmarks`, `search`, `serialization`
- `platform_admin`: `login_history`, `settings`, `email_settings`, `notify`, `routes`, `util`, `premium_features`
- `embedding_public`: `public`, `embed`, `preview_embed`
- `niche_experimental`: `actions`, `channels`, `tiles`, `stale`, `model_index`, `native_query_snippets`, `metabot`, `llm`, `persist`, `cloud_migration`, `scim`, `sso_saml`, `google`, `ldap`, `geojson`, `cache`, `api_keys`, `automagic_dashboards`

Optional streams are configured to gracefully skip common unavailable statuses (`400/403/404/405`).

## Usage

### About

```bash
tap-metabase --config config.json --about
```

### Discover

```bash
tap-metabase --config config.json --discover > catalog.json
```

### Sync

```bash
tap-metabase --config config.json --catalog catalog.json > output.jsonl
```

## Development

Run tests:

```bash
pytest
```

Compile smoke check:

```bash
python3 -m compileall tap_metabase
```

## Troubleshooting

- `401/403`: Check API key scope and permissions group assignment.
- `404` on some streams: Endpoint may not exist on your Metabase version; optional/soft-fail streams will be skipped.
- Long runtimes: `card_details`, `dashboard_cards`, and metadata child streams can generate many API calls. Limit catalog selections during smoke tests.
- Proxy/TLS issues: tune `verify_ssl`, `timeout_seconds`, and network/proxy settings in your runtime environment.

## Notes & Limitations

- No `/api/ee/*` endpoints are implemented.
- No query-result row extraction in v1 (metadata-only design).
- Metabase API is not versioned; endpoint behavior can vary by instance/version.

## References

- [Metabase API documentation](https://www.metabase.com/docs/latest/api)
- [Working with the Metabase API](https://www.metabase.com/learn/metabase-basics/administration/administration-and-operation/metabase-api)
