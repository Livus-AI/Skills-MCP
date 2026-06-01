"""
Update a page's properties, and/or archive (trash) it.
Part of the `notion` skill.

SAFETY GATE: archiving is destructive and requires confirm=true. Overwriting
existing property values is also destructive in spirit — read the page first
(get_page.py) and confirm with the user before changing values they already set.
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _notion import get_token, api, title_of, NotionError


def run(params: dict = None) -> dict:
    """
    Params:
        page_id (str): Required. The page ID.
        properties (dict): Optional Notion properties object to set.
        archive (bool): Optional. True archives (trashes) the page. Requires confirm=true.
        unarchive (bool): Optional. True restores a trashed page.
        confirm (bool): Required when archive=true. Explicit user confirmation.
        token (str): Optional override for NOTION_TOKEN.
    """
    params = params or {}
    token = get_token(params)
    if not token:
        return {"status": "error", "message": "NOTION_TOKEN not set (or pass 'token' param)"}

    page_id = params.get("page_id")
    if not page_id:
        return {"status": "error", "message": "'page_id' is required"}

    body = {}
    if params.get("properties"):
        body["properties"] = params["properties"]
    if params.get("archive"):
        if not params.get("confirm"):
            return {"status": "error",
                    "message": "Archiving is destructive. Re-run with confirm=true after the "
                               "user explicitly approves archiving this page."}
        body["archived"] = True
    elif params.get("unarchive"):
        body["archived"] = False

    if not body:
        return {"status": "error",
                "message": "Nothing to update: provide 'properties', 'archive', or 'unarchive'"}

    try:
        page = api("PATCH", f"/pages/{page_id}", token, body=body)
    except NotionError as exc:
        return {"status": "error", "message": str(exc)}

    return {
        "status": "success",
        "id": page.get("id"),
        "title": title_of(page),
        "url": page.get("url"),
        "archived": page.get("archived", page.get("in_trash", False)),
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
