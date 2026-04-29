"""Explicit JSON Schema definitions for each core stream."""

from __future__ import annotations

_STR = {"type": ["string", "null"]}
_INT = {"type": ["integer", "string", "null"]}
_INTV = {"type": ["integer", "null"]}
_BOOL = {"type": ["boolean", "null"]}
_OBJ = {"type": ["object", "null"]}
_ARR = {"type": ["array", "null"]}

USERS_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": True,
    "properties": {
        "_record_id": _STR,
        "id": _INT,
        "email": _STR,
        "first_name": _STR,
        "last_name": _STR,
        "common_name": _STR,
        "date_joined": _STR,
        "last_login": _STR,
        "is_active": _BOOL,
        "is_superuser": _BOOL,
        "is_staff": _BOOL,
        "locale": _STR,
        "group_ids": _ARR,
    },
}

ACTIVITY_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": True,
    "properties": {
        "_record_id": _STR,
        "id": _INT,
        "topic": _STR,
        "timestamp": _STR,
        "model": _STR,
        "model_id": _STR,
        "model_exists": _BOOL,
        "user_id": _INTV,
        "user": _OBJ,
        "details": _OBJ,
    },
}

PERMISSION_GROUPS_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": True,
    "properties": {
        "_record_id": _STR,
        "id": _INT,
        "name": _STR,
        "member_count": _INTV,
    },
}

PERMISSIONS_GRAPH_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": True,
    "properties": {
        "_record_id": _STR,
        "groups": _OBJ,
        "revision": _INTV,
    },
}

COLLECTIONS_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": True,
    "properties": {
        "_record_id": _STR,
        "id": _INT,
        "name": _STR,
        "description": _STR,
        "archived": _BOOL,
        "color": _STR,
        "slug": _STR,
        "location": _STR,
        "personal_owner_id": _INTV,
        "namespace": _STR,
        "created_at": _STR,
    },
}

DASHBOARDS_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": True,
    "properties": {
        "_record_id": _STR,
        "id": _INT,
        "name": _STR,
        "description": _STR,
        "created_at": _STR,
        "updated_at": _STR,
        "archived": _BOOL,
        "collection_id": _INTV,
        "collection_position": _INTV,
        "collection": _OBJ,
        "collection_name": _STR,
        "creator_id": _INTV,
        "view_count": _INTV,
        "favorite": _BOOL,
    },
}

DASHBOARD_CARDS_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": True,
    "properties": {
        "_record_id": _STR,
        "id": _INT,
        "dashboard_id": _INTV,
        "card_id": _INTV,
        "col": _INTV,
        "row": _INTV,
        "size_x": _INTV,
        "size_y": _INTV,
        "parameter_mappings": _ARR,
        "visualization_settings": _OBJ,
        "created_at": _STR,
        "updated_at": _STR,
    },
}

CARDS_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": True,
    "properties": {
        "_record_id": _STR,
        "id": _INT,
        "name": _STR,
        "description": _STR,
        "created_at": _STR,
        "updated_at": _STR,
        "archived": _BOOL,
        "collection_id": _INTV,
        "collection_position": _INTV,
        "creator_id": _INTV,
        "database_id": _INTV,
        "table_id": _INTV,
        "view_count": _INTV,
        "display": _STR,
        "query_type": _STR,
        "type": _STR,
        "dataset": _BOOL,
    },
}

CARD_DETAILS_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": True,
    "properties": {
        "_record_id": _STR,
        "id": _INT,
        "name": _STR,
        "description": _STR,
        "created_at": _STR,
        "updated_at": _STR,
        "archived": _BOOL,
        "collection_id": _INTV,
        "collection_position": _INTV,
        "collection": _OBJ,
        "collection_name": _STR,
        "creator_id": _INTV,
        "creator": _OBJ,
        "database_id": _INTV,
        "database": _OBJ,
        "database_name": _STR,
        "table_id": _INTV,
        "view_count": _INTV,
        "display": _STR,
        "query_type": _STR,
        "dataset_query": _OBJ,
        "result_metadata": _ARR,
        "visualization_settings": _OBJ,
        "type": _STR,
        "dataset": _BOOL,
    },
}

DATABASES_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": True,
    "properties": {
        "_record_id": _STR,
        "id": _INT,
        "name": _STR,
        "description": _STR,
        "created_at": _STR,
        "updated_at": _STR,
        "engine": _STR,
        "is_full_sync": _BOOL,
        "is_on_demand": _BOOL,
        "is_sample": _BOOL,
        "native_permissions": _STR,
        "dbms_version": _OBJ,
        "features": _ARR,
    },
}

TABLES_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": True,
    "properties": {
        "_record_id": _STR,
        "id": _INT,
        "name": _STR,
        "description": _STR,
        "created_at": _STR,
        "updated_at": _STR,
        "display_name": _STR,
        "entity_type": _STR,
        "schema": _STR,
        "db_id": _INTV,
        "active": _BOOL,
        "visibility_type": _STR,
        "field_order": _STR,
        "database_id": _INTV,
    },
}

FIELDS_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": True,
    "properties": {
        "_record_id": _STR,
        "id": _INT,
        "name": _STR,
        "description": _STR,
        "created_at": _STR,
        "updated_at": _STR,
        "display_name": _STR,
        "base_type": _STR,
        "effective_type": _STR,
        "semantic_type": _STR,
        "table_id": _INTV,
        "database_id": _INTV,
        "active": _BOOL,
        "visibility_type": _STR,
        "has_field_values": _STR,
        "position": _INTV,
    },
}

SEGMENTS_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": True,
    "properties": {
        "_record_id": _STR,
        "id": _INT,
        "name": _STR,
        "description": _STR,
        "created_at": _STR,
        "updated_at": _STR,
        "table_id": _INTV,
        "creator_id": _INTV,
        "archived": _BOOL,
        "definition": _OBJ,
        "definition_description": _STR,
    },
}

PULSES_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": True,
    "properties": {
        "_record_id": _STR,
        "id": _INT,
        "name": _STR,
        "created_at": _STR,
        "updated_at": _STR,
        "creator_id": _INTV,
        "collection_id": _INTV,
        "archived": _BOOL,
        "cards": _ARR,
        "channels": _ARR,
        "collection_position": _INTV,
        "skip_if_empty": _BOOL,
    },
}

ALERTS_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": True,
    "properties": {
        "_record_id": _STR,
        "id": _INT,
        "created_at": _STR,
        "updated_at": _STR,
        "creator_id": _INTV,
        "card": _OBJ,
        "channels": _ARR,
        "alert_condition": _STR,
        "alert_first_only": _BOOL,
        "archived": _BOOL,
    },
}

TIMELINES_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": True,
    "properties": {
        "_record_id": _STR,
        "id": _INT,
        "name": _STR,
        "description": _STR,
        "created_at": _STR,
        "updated_at": _STR,
        "creator_id": _INTV,
        "collection_id": _INTV,
        "archived": _BOOL,
        "icon": _STR,
        "default": _BOOL,
    },
}

TIMELINE_EVENTS_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": True,
    "properties": {
        "_record_id": _STR,
        "id": _INT,
        "name": _STR,
        "description": _STR,
        "created_at": _STR,
        "updated_at": _STR,
        "timestamp": _STR,
        "creator_id": _INTV,
        "timeline_id": _INTV,
        "archived": _BOOL,
        "icon": _STR,
        "time_matters": _BOOL,
    },
}

TASKS_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": True,
    "properties": {
        "_record_id": _STR,
        "id": _INT,
        "task": _STR,
        "status": _STR,
        "started_at": _STR,
        "ended_at": _STR,
        "duration": _INTV,
        "db_id": _INTV,
        "task_details": _OBJ,
    },
}
