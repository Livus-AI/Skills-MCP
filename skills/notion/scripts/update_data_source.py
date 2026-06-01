"""
Change a data source's structure: rename it, or add/rename/remove properties.
Part of the `notion` skill.

SAFETY GATE: this is a STRUCTURAL change and requires confirm=true. Removing a
property deletes its data on every row and is effectively irreversible. Inspect
the current schema (get_data_source.py) and show the user the exact before/after
before calling this.

To remove a property, set it to null in `properties`, e.g. {"Old Owner": null}.
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
        properties (dict): Optional. Property schema changes (null value removes).
        title (str|list): Optional. New title (string or Notion rich-text array).
        confirm (bool): Required. Explicit user confirmation for the structural change.
        token (str): Optional override for NOTION_TOKEN.
    """
    params = params or {}
    token = get_token(params)
    if not token:
        return {"status": "error", "message": "NOTION_TOKEN not set (or pass 'token' param)"}

    data_source_id = params.get("data_source_id")
    if not data_source_id:
        return {"status": "error", "message": "'data_source_id' is required"}

    if not params.get("properties") and not params.get("title"):
        return {"status": "error", "message": "Provide 'properties' and/or 'title' to change"}

    if not params.get("confirm"):
        return {"status": "error",
                "message": "Structural changes are gated. Show the user the exact before/after "
                           "(especially any property removals, which delete data on all rows), "
                           "then re-run with confirm=true after they approve."}

    body = {}
    if params.get("properties"):
        body["properties"] = params["properties"]
    if params.get("title") is not None:
        title = params["title"]
        if isinstance(title, str):
            title = [{"type": "text", "text": {"content": title}}]
        body["title"] = title

    try:
        data = api("PATCH", f"/data_sources/{data_source_id}", token, body=body)
    except NotionError as exc:
        return {"status": "error", "message": str(exc)}

    schema = {name: prop.get("type") for name, prop in data.get("properties", {}).items()}
    return {
        "status": "success",
        "id": data.get("id"),
        "title": title_of(data),
        "properties": schema,
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
