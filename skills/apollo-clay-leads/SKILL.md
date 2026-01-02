---
name: apollo-clay-leads
description: Lead generation pipeline that fetches leads from Apollo.io, enriches via Clay webhooks, and scores with explainable reasoning. Use when generating B2B leads, running outbound campaigns, or building prospect lists.
license: MIT
compatibility: Requires APOLLO_API_KEY env var. Optional CLAY_API_KEY and CLAY_WEBHOOK_URL for enrichment.
metadata:
  author: Livus
  version: "1.0"
---

# Apollo-Clay Lead Generation Pipeline

End-to-end lead generation: fetch from Apollo → enrich via Clay → score → export.

## Prerequisites

Set these environment variables in `.env`:

| Variable | Required | Description |
|----------|----------|-------------|
| `APOLLO_API_KEY` | Yes | Apollo.io API key |
| `CLAY_API_KEY` | No | Clay API key (for future use) |
| `CLAY_WEBHOOK_URL` | No | Clay table webhook URL for enrichment |

## Quick Start

Run the full pipeline:
```bash
python skills/apollo-clay-leads/scripts/run_pipeline.py --icp icp_v1
```

Or use a CSV export from Apollo:
```bash
python skills/apollo-clay-leads/scripts/run_pipeline.py --icp icp_v1 --csv path/to/apollo_export.csv
```

## Available Scripts

| Script | Purpose |
|--------|---------|
| `run_pipeline.py` | Main orchestrator - runs the full pipeline |
| `fetch_apollo_api.py` | Fetch leads from Apollo.io API |
| `ingest_apollo_csv.py` | Parse Apollo CSV exports |
| `enrich_clay.py` | Enrich leads via Clay webhook |
| `score.py` | Score leads with explainable reasoning |
| `export.py` | Export to CSV and JSON artifacts |
| `db.py` | SQLite storage layer |

## Pipeline Flow

```
1. Load ICP config (icp_configs/<name>.json)
2. Ingest leads:
   - From Apollo API (default)
   - From CSV export (--csv flag)
3. Enrich via Clay webhook (if CLAY_WEBHOOK_URL set)
4. Score all leads (fit_score 0-100 + reasons)
5. Export artifacts:
   - output/leads_<YYYY-MM-DD>.csv
   - output/run_<run_id>.json
```

## ICP Configuration

Create custom ICPs in `scripts/icp_configs/<name>.json`:

```json
{
  "name": "my_icp",
  "description": "Target audience description",
  "filters": {
    "person_titles": ["CTO", "VP Engineering"],
    "person_seniorities": ["c_suite", "vp", "director"],
    "organization_locations": ["United States"],
    "organization_num_employees_ranges": ["51,200", "201,500"]
  },
  "scoring_weights": {
    "title_match": 25,
    "seniority_match": 20,
    "industry_match": 20,
    "company_size_match": 15,
    "location_match": 10,
    "verified_email": 5,
    "has_linkedin": 5
  }
}
```

## Output Artifacts

- **leads_<date>.csv**: Scored leads with columns: name, email, title, company, fit_score, score_reasons, etc.
- **run_<id>.json**: Run metadata including stats, ICP used, timestamp, counts

## Example Usage

```python
# Via MCP
execute_skill_script("apollo-clay-leads", "run_pipeline.py", {
    "icp": "icp_v1",
    "limit": 100
})

# Fetch only (no enrichment)
execute_skill_script("apollo-clay-leads", "fetch_apollo_api.py", {
    "icp": "icp_v1",
    "limit": 50
})

# Score existing leads
execute_skill_script("apollo-clay-leads", "score.py", {
    "run_id": "abc123"
})
```
