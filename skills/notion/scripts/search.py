"""
Search the Notion workspace for pages or data sources by title text.
Part of the `notion` skill. Read-only; flows freely.
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _notion import get_token, api, title_of, NotionError


def run(params: dict = None) -> dict:
    """
    Params:
        query (str): Optional text to search titles for. Omit to list everything.
        filter (str): Optional "page" or "data_source" to restrict object type.
        page_size (int): Optional max results (default 25).
        token (str): Optional override for NOTION_TOKEN.
    """
    params = params or {}
    token = get_token(params)
    if not token:
        return {"status": "error", "message": "NOTION_TOKEN not set (or pass 'token' param)"}

    body = {"page_size": params.get("page_size", 25)}
    if params.get("query"):
        body["query"] = params["query"]
    if params.get("filter") in ("page", "data_source"):
        body["filter"] = {"property": "object", "value": params["filter"]}

    try:
        data = api("POST", "/search", token, body=body)
    except NotionError as exc:
        return {"status": "error", "message": str(exc)}

    items = [
        {
            "id": obj.get("id"),
            "object": obj.get("object"),
            "title": title_of(obj),
            "url": obj.get("url"),
        }
        for obj in data.get("results", [])
    ]
    return {
        "status": "success",
        "count": len(items),
        "results": items,
        "has_more": bool(data.get("has_more")),
        "next_cursor": data.get("next_cursor"),
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
