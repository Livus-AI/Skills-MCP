"""
Create a page (a standalone page, or a row in a data source).
Part of the `notion` skill. Additive create; flows freely.

Best practice: search.py first to avoid duplicates, and get_data_source.py to match
the target schema before building `properties`.
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _notion import get_token, api, title_of, NotionError


def run(params: dict = None) -> dict:
    """
    Params (exactly one parent is required):
        parent_data_source_id (str): Create a row in this data source.
        parent_page_id (str): Create a subpage under this page.
        properties (dict): Notion properties object (must match the schema for a
            data-source row; for a subpage, at minimum the title property).
        children (list): Optional block objects for initial page content.
        token (str): Optional override for NOTION_TOKEN.
    """
    params = params or {}
    token = get_token(params)
    if not token:
        return {"status": "error", "message": "NOTION_TOKEN not set (or pass 'token' param)"}

    ds_id = params.get("parent_data_source_id")
    page_id = params.get("parent_page_id")
    if bool(ds_id) == bool(page_id):
        return {"status": "error",
                "message": "Provide exactly one of 'parent_data_source_id' or 'parent_page_id'"}
    if not params.get("properties"):
        return {"status": "error", "message": "'properties' is required (include the title property)"}

    if ds_id:
        parent = {"type": "data_source_id", "data_source_id": ds_id}
    else:
        parent = {"type": "page_id", "page_id": page_id}

    body = {"parent": parent, "properties": params["properties"]}
    if params.get("children"):
        body["children"] = params["children"]

    try:
        page = api("POST", "/pages", token, body=body)
    except NotionError as exc:
        return {"status": "error", "message": str(exc)}

    return {
        "status": "success",
        "id": page.get("id"),
        "title": title_of(page),
        "url": page.get("url"),
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
