"""
Lead Generation Pipeline Orchestrator

Runs the full pipeline: ingest → enrich → score → export

Usage:
    # Apify + Apollo (recommended for free tier)
    python run_pipeline.py --query "administrators from farms in brazil" --apify --limit 30
    
    # Apollo API (requires paid plan)
    python run_pipeline.py --query "administrators from farms in brazil" --limit 30
    
    # From CSV export
    python run_pipeline.py --csv path/to/apollo.csv
"""

import sys
import json
import os
import argparse
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import pipeline modules
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from db import create_run, complete_run, get_run, init_db, upsert_lead
from fetch_apollo_api import fetch_leads, parse_query_to_filters, enrich_leads_with_apollo
from ingest_apollo_csv import ingest_csv
from enrich_clay import enrich_leads
from score import score_leads
from export import export_all


def load_icp_config(icp_name: str) -> Dict[str, Any]:
    """Load ICP configuration from file."""
    config_path = os.path.join(SCRIPT_DIR, "icp_configs", f"{icp_name}.json")
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"ICP config not found: {config_path}")
    
    with open(config_path, "r") as f:
        return json.load(f)


def run_pipeline(
    query: Optional[str] = None,
    icp_name: str = "icp_v1",
    csv_path: Optional[str] = None,
    limit: int = 100,
    use_apify: bool = False,
    skip_enrichment: bool = False,
    skip_export: bool = False
) -> Dict[str, Any]:
    """
    Run the full lead generation pipeline.
    
    Args:
        query: Natural language query (primary input method)
        icp_name: Name of ICP config to use (fallback if no query)
        csv_path: Path to Apollo CSV export (fallback)
        limit: Maximum leads to fetch from API
        use_apify: Use Apify LinkedIn + Apollo enrichment (free tier compatible)
        skip_enrichment: Skip Clay enrichment step
        skip_export: Skip export step
    
    Returns:
        dict with pipeline results
    """
    start_time = datetime.now()
    logger.info("=" * 60)
    logger.info("LEAD GENERATION PIPELINE")
    if use_apify:
        logger.info("🔗 Mode: Apify LinkedIn → Apollo Enrichment (Free Tier)")
    logger.info("=" * 60)
    
    try:
        # Initialize database
        init_db()
        logger.info("Database initialized")
        
        # Determine source and config
        if query:
            logger.info(f"Query: \"{query}\"")
            filters = parse_query_to_filters(query)
            logger.info(f"Parsed filters: {json.dumps(filters, indent=2)}")
            icp_config = {"name": "query", "description": query, "filters": filters}
            source = "apify_linkedin" if use_apify else "apollo_api"
        elif csv_path:
            icp_config = load_icp_config(icp_name)
            source = "csv_import"
            logger.info(f"CSV: {csv_path}")
        else:
            icp_config = load_icp_config(icp_name)
            source = "apollo_api"
            logger.info(f"ICP: {icp_name} - {icp_config.get('description', '')}")
        
        # Create pipeline run
        run_id = create_run(icp_config.get("name", icp_name), icp_config, source)
        logger.info(f"Pipeline run ID: {run_id}")
        logger.info("-" * 60)
        
        results = {
            "run_id": run_id,
            "query": query,
            "icp_name": icp_config.get("name", icp_name),
            "source": source,
            "steps": {}
        }
        
        # Step 1: Ingest leads
        logger.info("STEP 1: Ingesting leads...")
        
        if csv_path:
            # CSV import
            ingest_result = ingest_csv(csv_path=csv_path, icp_name=icp_name, run_id=run_id)
        elif use_apify and query:
            # Apify LinkedIn + Apollo enrichment flow
            from fetch_apify_linkedin import fetch_linkedin_leads
            
            logger.info("  → Fetching from LinkedIn via Apify...")
            apify_result = fetch_linkedin_leads(query=query, limit=limit, run_id=run_id)
            
            if apify_result.get("status") == "error":
                ingest_result = apify_result
            else:
                raw_leads = apify_result.get("leads", [])
                logger.info(f"  → Got {len(raw_leads)} leads from Apify")
                
                # Skip Apollo enrichment (API restricted on free plan)
                # logger.info("  → Enriching with Apollo (free tier)...")
                # enrich_result = enrich_leads_with_apollo(leads=raw_leads, run_id=run_id)
                
                ingest_result = {
                    "status": "success",
                    "leads_fetched": len(raw_leads),
                    "leads_ingested": len(raw_leads),
                    "source": "apify_linkedin",
                    "apify_run_id": apify_result.get("apify_run_id"),
                    "message": f"Fetched {len(raw_leads)} leads from Apify"
                }
        else:
            # Direct Apollo API (requires paid plan)
            ingest_result = fetch_leads(
                icp_name=icp_name if not query else None,
                query=query,
                limit=limit,
                run_id=run_id
            )
        
        results["steps"]["ingest"] = ingest_result
        
        if ingest_result.get("status") == "error":
            logger.error(f"Ingest failed: {ingest_result.get('message')}")
            complete_run(run_id, status="failed", error_message=ingest_result.get("message"))
            return {"status": "error", "step": "ingest", **results}
        
        leads_count = ingest_result.get("leads_fetched", 0) or ingest_result.get("leads_ingested", 0)
        logger.info(f"✓ Ingested {leads_count} leads")
        logger.info("-" * 60)
        
        # Step 2: Enrich via Clay (optional)
        if not skip_enrichment:
            logger.info("STEP 2: Enriching leads via Clay...")
            enrich_result = enrich_leads(run_id=run_id)
            results["steps"]["enrich"] = enrich_result
            
            if enrich_result.get("status") == "skipped":
                logger.warning(f"⚠ Enrichment skipped: {enrich_result.get('message')}")
            elif enrich_result.get("status") == "error":
                logger.error(f"Enrichment failed: {enrich_result.get('message')}")
            else:
                logger.info(f"✓ Enriched {enrich_result.get('leads_enriched', 0)} leads")
        else:
            logger.info("STEP 2: Enrichment skipped (--skip-enrichment)")
            results["steps"]["enrich"] = {"status": "skipped", "reason": "--skip-enrichment"}
        
        logger.info("-" * 60)
        
        # Step 3: Score leads
        logger.info("STEP 3: Scoring leads...")
        score_result = score_leads(run_id=run_id, icp_name=icp_name if not query else "query")
        results["steps"]["score"] = score_result
        
        if score_result.get("status") == "error":
            logger.error(f"Scoring failed: {score_result.get('message')}")
            complete_run(run_id, status="failed", error_message=score_result.get("message"))
            return {"status": "error", "step": "score", **results}
        
        distribution = score_result.get("distribution", {})
        logger.info(f"✓ Scored {score_result.get('leads_scored', 0)} leads")
        logger.info(f"  High fit (70+): {distribution.get('high', 0)}")
        logger.info(f"  Medium fit (40-69): {distribution.get('medium', 0)}")
        logger.info(f"  Low fit (<40): {distribution.get('low', 0)}")
        logger.info("-" * 60)
        
        # Step 4: Export artifacts
        if not skip_export:
            logger.info("STEP 4: Exporting artifacts...")
            export_result = export_all(run_id=run_id)
            results["steps"]["export"] = export_result
            
            if export_result.get("status") == "error":
                logger.error(f"Export failed: {export_result.get('message')}")
            else:
                logger.info(f"✓ Exported to:")
                logger.info(f"  CSV:      {export_result.get('csv_path')}")
                logger.info(f"  JSON:     {export_result.get('json_path')}")
                logger.info(f"  Markdown: {export_result.get('markdown_path')}")
        else:
            logger.info("STEP 4: Export skipped (--skip-export)")
            results["steps"]["export"] = {"status": "skipped"}
        
        # Complete run
        complete_run(run_id, status="completed")
        
        # Summary
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info("=" * 60)
        logger.info("PIPELINE COMPLETE")
        logger.info(f"Run ID: {run_id}")
        logger.info(f"Elapsed: {elapsed:.1f}s")
        logger.info(f"Leads processed: {leads_count}")
        logger.info("=" * 60)
        
        results["status"] = "success"
        results["elapsed_seconds"] = elapsed
        results["total_leads"] = leads_count
        
        return results
        
    except FileNotFoundError as e:
        logger.error(str(e))
        return {"status": "error", "message": str(e)}
    except ValueError as e:
        logger.error(str(e))
        return {"status": "error", "message": str(e)}
    except Exception as e:
        logger.exception("Pipeline failed")
        return {"status": "error", "message": str(e)}


def run(params: dict = None) -> dict:
    """Entry point for MCP execution."""
    params = params or {}
    
    return run_pipeline(
        query=params.get("query"),
        icp_name=params.get("icp", "icp_v1"),
        csv_path=params.get("csv_path") or params.get("csv"),
        limit=params.get("limit", 100),
        use_apify=params.get("apify", False),
        skip_enrichment=params.get("skip_enrichment", False),
        skip_export=params.get("skip_export", False)
    )


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Lead Generation Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Apify + Apollo (recommended for free tier)
  python run_pipeline.py --query "administrators from farms in brazil" --apify --limit 30

  # Apollo API direct (requires paid plan)
  python run_pipeline.py --query "administrators from farms in brazil" --limit 30

  # From CSV export
  python run_pipeline.py --csv path/to/apollo.csv
        """
    )
    
    # Input sources
    parser.add_argument("--query", "-q", help="Natural language query (primary method)")
    parser.add_argument("--csv", help="Path to Apollo CSV export (fallback)")
    parser.add_argument("--icp", default="icp_v1", help="ICP config name (default: icp_v1)")
    
    # Options
    parser.add_argument("--limit", "-n", type=int, default=100, help="Max leads to fetch (default: 100)")
    parser.add_argument("--apify", action="store_true", help="Use Apify LinkedIn + Apollo enrichment (free tier compatible)")
    
    # Skip flags
    parser.add_argument("--skip-enrichment", action="store_true", help="Skip Clay enrichment")
    parser.add_argument("--skip-export", action="store_true", help="Skip export step")
    
    # Output
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    
    args = parser.parse_args()
    
    result = run_pipeline(
        query=args.query,
        icp_name=args.icp,
        csv_path=args.csv,
        limit=args.limit,
        use_apify=args.apify,
        skip_enrichment=args.skip_enrichment,
        skip_export=args.skip_export
    )
    
    if args.json:
        print(json.dumps(result, indent=2, default=str))
    
    sys.exit(0 if result.get("status") == "success" else 1)


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1].startswith("{"):
        try:
            params = json.loads(sys.argv[1])
            result = run(params)
            print(json.dumps(result, indent=2, default=str))
        except json.JSONDecodeError:
            main()
    else:
        main()
