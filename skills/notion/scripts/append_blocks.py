"""
Append block content to a page (or another block).
Part of the `notion` skill. Additive content edit; flows freely.

This is the SAFE way to add content: it appends, it does not overwrite existing
content. To replace or remove existing content, that is destructive — handle it
deliberately and confirm with the user first (see SKILL.md safety gates).
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _notion import get_token, api, NotionError


def run(params: dict = None) -> dict:
    """
    Params:
        block_id (str): Required. The page ID or parent block ID to append under.
        children (list): Required. Array of Notion block objects to append.
        token (str): Optional override for NOTION_TOKEN.
    """
    params = params or {}
    token = get_token(params)
    if not token:
        return {"status": "error", "message": "NOTION_TOKEN not set (or pass 'token' param)"}

    block_id = params.get("block_id")
    children = params.get("children")
    if not block_id:
        return {"status": "error", "message": "'block_id' is required"}
    if not isinstance(children, list) or not children:
        return {"status": "error", "message": "'children' must be a non-empty list of block objects"}

    try:
        data = api("PATCH", f"/blocks/{block_id}/children", token, body={"children": children})
    except NotionError as exc:
        return {"status": "error", "message": str(exc)}

    appended = data.get("results", [])
    return {"status": "success", "appended_count": len(appended), "block_id": block_id}


if __name__ == "__main__":
    p = {}
    if len(sys.argv) > 1:
        try:
            p = json.loads(sys.argv[1])
        except json.JSONDecodeError:
            print(json.dumps({"status": "error", "message": "Could not parse params as JSON"}))
            sys.exit(1)
    print(json.dumps(run(p), indent=2, default=str))
