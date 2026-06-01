"""
Retrieve a page's properties and (optionally) its block content.
Part of the `notion` skill. Read-only; flows freely.

ALWAYS read a page before editing it, so edits are minimal and not blind overwrites.
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _notion import get_token, api, paginate, title_of, NotionError


def run(params: dict = None) -> dict:
    """
    Params:
        page_id (str): Required. The page ID.
        include_content (bool): Optional, also fetch top-level blocks (default false).
        token (str): Optional override for NOTION_TOKEN.
    """
    params = params or {}
    token = get_token(params)
    if not token:
        return {"status": "error", "message": "NOTION_TOKEN not set (or pass 'token' param)"}

    page_id = params.get("page_id")
    if not page_id:
        return {"status": "error", "message": "'page_id' is required"}

    try:
        page = api("GET", f"/pages/{page_id}", token)
        result = {
            "status": "success",
            "id": page.get("id"),
            "title": title_of(page),
            "url": page.get("url"),
            "archived": page.get("archived", page.get("in_trash", False)),
            "parent": page.get("parent"),
            "properties": page.get("properties", {}),
        }
        if params.get("include_content"):
            blocks = paginate("GET", f"/blocks/{page_id}/children", token, fetch_all=True)
            result["blocks"] = blocks["results"]
            result["block_count"] = len(blocks["results"])
    except NotionError as exc:
        return {"status": "error", "message": str(exc)}

    return result


if __name__ == "__main__":
    p = {}
    if len(sys.argv) > 1:
        try:
            p = json.loads(sys.argv[1])
        except json.JSONDecodeError:
            print(json.dumps({"status": "error", "message": "Could not parse params as JSON"}))
            sys.exit(1)
    print(json.dumps(run(p), indent=2, default=str))
