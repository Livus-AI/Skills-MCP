"""
Retrieve a data source's schema (its property names and types).
Part of the `notion` skill. Read-only; flows freely.

ALWAYS call this before creating or updating rows so you match property names and
types exactly. Get the data_source_id from get_database.py or search.py.
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _notion import get_token, api, title_of, NotionError


def run(params: dict = None) -> dict:
    """
    Params:
        data_source_id (str): Required. The data source ID.
        token (str): Optional override for NOTION_TOKEN.
    """
    params = params or {}
    token = get_token(params)
    if not token:
        return {"status": "error", "message": "NOTION_TOKEN not set (or pass 'token' param)"}

    data_source_id = params.get("data_source_id")
    if not data_source_id:
        return {"status": "error", "message": "'data_source_id' is required"}

    try:
        data = api("GET", f"/data_sources/{data_source_id}", token)
    except NotionError as exc:
        return {"status": "error", "message": str(exc)}

    schema = {
        name: {"type": prop.get("type"), "id": prop.get("id")}
        for name, prop in data.get("properties", {}).items()
    }
    return {
        "status": "success",
        "id": data.get("id"),
        "title": title_of(data),
        "parent": data.get("parent"),
        "properties": schema,
        "property_count": len(schema),
    }


if __name__ == "__main__":
    p = {}
    if len(sys.argv) > 1:
        try:
            p = json.loads(sys.argv[1])
        except json.JSONDecodeError:
            print(json.dumps({"status": "error", "message": "Could not parse params as JSON"}))
            sys.exit(1)
    print(json.dumps(run(p), indent=2, default=str))
