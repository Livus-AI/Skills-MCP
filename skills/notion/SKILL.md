---
name: notion
description: Read, search, query, create, edit, and report on content in a Notion workspace via the Notion API. Use when the user wants to find, read, create, file, update, summarize, or report on Notion pages or databases, or mentions Notion. Discovers structure live (search and inspect before acting) and gates destructive or structural changes behind explicit confirmation.
license: MIT
compatibility: Requires NOTION_TOKEN env var (Notion internal integration secret, ntn_...). The integration only sees pages/databases explicitly shared with it.
metadata:
  author: Livus
  version: "1.0"
---

# Notion

Operate on a Notion workspace through the Notion REST API (version `2025-09-03`,
data-source model). Generic and workspace-agnostic: it discovers structure at
runtime rather than hardcoding databases.

Three rules govern everything:

1. **Discover before you act** — search and inspect the live workspace; never assume structure.
2. **Match what exists** — read current state and schemas before writing.
3. **Confirm before you destroy or restructure** — reads and additive creates flow freely; archiving, deleting, and structural schema changes require explicit user approval.

## Prerequisites

Set `NOTION_TOKEN` in the project `.env` (or pass `token` to any script):

1. Create an internal integration at https://www.notion.so/profile/integrations
2. Optionally restrict it to "Read content" only (least privilege).
3. **Share the specific pages/databases with the integration** — it sees nothing until you do.
4. Copy the secret (`ntn_…`) into `NOTION_TOKEN`.

Every script returns `{"status": "success", ...}` or `{"status": "error", "message": ...}`.

## Available scripts

| Script | Operation | Safety |
|--------|-----------|--------|
| `search.py` | Find pages/data sources by title | read — free |
| `get_database.py` | Resolve a database's data source(s) | read — free |
| `get_data_source.py` | Inspect a data source's property schema | read — free |
| `query_data_source.py` | Query rows with filter/sorts + pagination | read — free |
| `get_page.py` | Read a page's properties and (optional) content | read — free |
| `create_page.py` | Create a page or data-source row | additive — free |
| `append_blocks.py` | Append content blocks to a page | additive — free |
| `update_page.py` | Update properties; archive (trash) a page | archive needs `confirm=true` |
| `update_data_source.py` | Add/rename/remove properties; rename | structural — needs `confirm=true` |

## Discover-first workflow

Never operate blind:

| Before you... | First call... |
|---------------|---------------|
| Create or query a row | `get_database.py` → `get_data_source.py` (resolve data source + schema) |
| Create a row / page | `search.py` (avoid duplicates), then match the schema |
| Edit a page | `get_page.py` (read current state) |
| Change structure | `get_data_source.py` (know exactly what you're altering) |

A database can expose **multiple data sources**; you query and create rows against a
**data source**, not the database. Resolve the `data_source_id` first.

## Safety gates (REQUIRED)

**Flow freely:** `search`, `get_*`, `query_data_source`, `create_page`, `append_blocks`.

**Require explicit user confirmation first** (and `confirm=true` on the script):
- Archiving / trashing a page (`update_page.py` with `archive=true`).
- Structural schema changes — add/rename/**remove** properties (`update_data_source.py`). Removing a property deletes its data on every row.
- Overwriting existing page content or property values. Prefer `append_blocks.py` over replacing; before overwriting values, read them first and confirm.

**Confirmation protocol:** state the exact target (name + id), show `before → after`
(or precisely what will be removed), ask, and act only on an explicit "yes." Do not
batch destructive operations behind one vague approval. When unsure whether something
is destructive, treat it as destructive.

## How to use

```python
# 1. Discover
execute_skill_script("notion", "search.py", {"query": "Projects", "filter": "data_source"})
execute_skill_script("notion", "get_database.py", {"database_id": "<db_id>"})
execute_skill_script("notion", "get_data_source.py", {"data_source_id": "<ds_id>"})

# 2. Read / query
execute_skill_script("notion", "query_data_source.py", {
    "data_source_id": "<ds_id>",
    "filter": {"property": "Status", "status": {"equals": "Done"}},
    "fetch_all": True
})
execute_skill_script("notion", "get_page.py", {"page_id": "<page_id>", "include_content": True})

# 3. Create (additive — free)
execute_skill_script("notion", "create_page.py", {
    "parent_data_source_id": "<ds_id>",
    "properties": {
        "Name": {"title": [{"text": {"content": "Ship Q3 report"}}]},
        "Due": {"date": {"start": "2026-06-05"}}
    }
})

# 4. Append content (additive — free)
execute_skill_script("notion", "append_blocks.py", {
    "block_id": "<page_id>",
    "children": [{"object": "block", "type": "paragraph",
                  "paragraph": {"rich_text": [{"text": {"content": "Notes..."}}]}}]
})

# 5. Destructive — ONLY after the user approves
execute_skill_script("notion", "update_page.py", {
    "page_id": "<page_id>", "archive": True, "confirm": True
})
execute_skill_script("notion", "update_data_source.py", {
    "data_source_id": "<ds_id>", "properties": {"Old Owner": None}, "confirm": True
})
```

## Reporting back

After any write, tell the user exactly what changed — created/edited/archived, where,
and the page URL or ID. Only claim success the script actually returned.

## Common mistakes

- Creating duplicates by not searching first.
- Writing rows with property names/types that don't match the schema (inspect first).
- Querying a database ID instead of its data source ID.
- Overwriting content instead of appending.
- Forgetting `fetch_all` and treating one page of results as complete.
- Archiving or removing properties without `confirm=true` and user approval.
