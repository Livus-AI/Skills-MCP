"""
Shared Notion API helper for the `notion` skill.

Not a runnable skill script (no run()). Imported by the other scripts in this
directory. Handles auth, the Notion-Version header, requests, pagination, and
title extraction so each script stays small.

API version: 2025-09-03 (data-source model).
"""

import os
import requests

NOTION_VERSION = "2025-09-03"
BASE_URL = "https://api.notion.com/v1"
TIMEOUT = 30


class NotionError(Exception):
    """Raised when the Notion API returns a non-2xx response or auth is missing."""


def get_token(params: dict) -> str | None:
    """Resolve the integration token from params, then env, then a nearby .env."""
    token = (params or {}).get("token") or os.environ.get("NOTION_TOKEN")
    if token:
        return token
    return _token_from_dotenv()


def _token_from_dotenv() -> str | None:
    """Minimal fallback: look for NOTION_TOKEN in .env files near the skill/project.

    Avoids a hard dependency on python-dotenv. Checks the skill dir, the current
    working directory, and up to three parent directories (project root).
    """
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(here, ".env"),
        os.path.join(here, "..", ".env"),
        os.path.join(os.getcwd(), ".env"),
    ]
    root = here
    for _ in range(3):
        root = os.path.dirname(root)
        candidates.append(os.path.join(root, ".env"))
    for path in candidates:
        try:
            with open(path, "r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line.startswith("NOTION_TOKEN=") and not line.startswith("#"):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val:
                            return val
        except OSError:
            continue
    return None


def _headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def api(method: str, path: str, token: str, body: dict = None, query: dict = None) -> dict:
    """Make one Notion API call. Returns parsed JSON or raises NotionError."""
    url = BASE_URL + path
    try:
        resp = requests.request(
            method, url, headers=_headers(token), json=body, params=query, timeout=TIMEOUT
        )
    except requests.RequestException as exc:
        raise NotionError(f"Request to {path} failed: {exc}") from exc

    if resp.status_code < 200 or resp.status_code >= 300:
        detail = resp.text
        try:
            payload = resp.json()
            detail = payload.get("message", detail)
        except ValueError:
            pass
        raise NotionError(f"Notion API {resp.status_code} on {method} {path}: {detail}")

    if not resp.text:
        return {}
    return resp.json()


def paginate(method: str, path: str, token: str, body: dict = None, query: dict = None,
             page_size: int = 100, fetch_all: bool = False, start_cursor: str = None) -> dict:
    """Fetch one page (or all pages) of a list endpoint.

    Returns {"results": [...], "has_more": bool, "next_cursor": str|None}.
    For POST endpoints (query) the cursor/page_size go in the body; for GET
    endpoints (block children) they go in the query string.
    """
    results = []
    cursor = start_cursor
    has_more = True
    next_cursor = None

    while has_more:
        if method.upper() == "GET":
            q = dict(query or {})
            q["page_size"] = page_size
            if cursor:
                q["start_cursor"] = cursor
            data = api(method, path, token, query=q)
        else:
            b = dict(body or {})
            b["page_size"] = page_size
            if cursor:
                b["start_cursor"] = cursor
            data = api(method, path, token, body=b)

        results.extend(data.get("results", []))
        has_more = bool(data.get("has_more"))
        next_cursor = data.get("next_cursor")
        cursor = next_cursor
        if not fetch_all:
            break

    return {"results": results, "has_more": has_more, "next_cursor": next_cursor}


def title_of(obj: dict) -> str:
    """Best-effort plain-text title for a page / data source / database object."""
    # Data sources and databases expose a top-level `title` rich-text array.
    if isinstance(obj.get("title"), list):
        text = "".join(part.get("plain_text", "") for part in obj["title"])
        if text:
            return text
    # Pages expose the title inside whichever property has type == "title".
    props = obj.get("properties", {})
    for prop in props.values():
        if isinstance(prop, dict) and prop.get("type") == "title":
            return "".join(part.get("plain_text", "") for part in prop.get("title", []))
    return ""
