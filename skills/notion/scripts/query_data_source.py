"""
Query a data source's entries with optional filter and sorts.
Part of the `notion` skill. Read-only; flows freely.

Prefer a filter over fetching everything. Set fetch_all=true to follow pagination
to completion; otherwise one page is returned with next_cursor for the caller.
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _notion import get_token, paginate, title_of, NotionError


def run(params: dict = None) -> dict:
    """
    Params:
        data_source_id (str): Required. The data source ID to query.
        filter (dict): Optional Notion filter object.
        sorts (list): Optional Notion sorts array.
        page_size (int): Optional rows per page (default 100, max 100).
        start_cursor (str): Optional cursor to resume pagination.
        fetch_all (bool): Optional, follow pagination to the end (default false).
        token (str): Optional override for NOTION_TOKEN.
    """
    params = params or {}
    token = get_token(params)
    if not token:
        return {"status": "error", "message": "NOTION_TOKEN not set (or pass 'token' param)"}

    data_source_id = params.get("data_source_id")
    if not data_source_id:
        return {"status": "error", "message": "'data_source_id' is required"}

    body = {}
    if params.get("filter"):
        body["filter"] = params["filter"]
    if params.get("sorts"):
        body["sorts"] = params["sorts"]

    try:
        page = paginate(
            "POST",
            f"/data_sources/{data_source_id}/query",
            token,
            body=body,
            page_size=min(int(params.get("page_size", 100)), 100),
            fetch_all=bool(params.get("fetch_all", False)),
            start_cursor=params.get("start_cursor"),
        )
    except NotionError as exc:
        return {"status": "error", "message": str(exc)}

    rows = [
        {"id": row.get("id"), "title": title_of(row), "url": row.get("url"),
         "properties": row.get("properties", {})}
        for row in page["results"]
    ]
    return {
        "status": "success",
        "count": len(rows),
        "results": rows,
        "has_more": page["has_more"],
        "next_cursor": page["next_cursor"],
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
