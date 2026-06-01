"""
Retrieve a Notion database and resolve its data source(s).
Part of the `notion` skill. Read-only; flows freely.

A database can expose multiple data sources (API 2025-09-03). You query / create
rows against a DATA SOURCE, not the database directly — use this first to get the
data_source_id, then get_data_source.py to inspect its schema.
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _notion import get_token, api, title_of, NotionError


def run(params: dict = None) -> dict:
    """
    Params:
        database_id (str): Required. The database ID.
        token (str): Optional override for NOTION_TOKEN.
    """
    params = params or {}
    token = get_token(params)
    if not token:
        return {"status": "error", "message": "NOTION_TOKEN not set (or pass 'token' param)"}

    database_id = params.get("database_id")
    if not database_id:
        return {"status": "error", "message": "'database_id' is required"}

    try:
        data = api("GET", f"/databases/{database_id}", token)
    except NotionError as exc:
        return {"status": "error", "message": str(exc)}

    data_sources = [
        {"id": ds.get("id"), "name": ds.get("name")}
        for ds in data.get("data_sources", [])
    ]
    return {
        "status": "success",
        "id": data.get("id"),
        "title": title_of(data),
        "url": data.get("url"),
        "data_sources": data_sources,
        "data_source_count": len(data_sources),
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
