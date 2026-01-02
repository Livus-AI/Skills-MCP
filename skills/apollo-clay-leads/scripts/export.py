"""
Export Leads to CSV and JSON Artifacts

Generates output files:
- output/leads_<YYYY-MM-DD>.csv
- output/run_<run_id>.json
"""

import sys
import json
import os
import csv
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import db module
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from db import get_leads_by_run, get_scores_by_run, get_run, update_run

# Output directory - relative to skill directory
OUTPUT_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "..", "..", "..", "output")


def get_output_dir() -> str:
    """Get output directory path, creating if needed."""
    output_dir = os.path.abspath(OUTPUT_DIR)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def export_csv(run_id: str, filename: Optional[str] = None) -> str:
    """
    Export leads with scores to CSV.
    
    Args:
        run_id: Pipeline run ID
        filename: Optional custom filename
    
    Returns:
        Path to exported CSV file
    """
    leads = get_leads_by_run(run_id)
    scores = get_scores_by_run(run_id)
    
    # Create score lookup by lead_id
    score_map = {s["lead_id"]: s for s in scores}
    
    # Merge leads with scores
    merged = []
    for lead in leads:
        lead_score = score_map.get(lead["id"], {})
        merged.append({
            **lead,
            "fit_score": lead_score.get("fit_score", 0),
            "score_reasons": "; ".join(lead_score.get("score_reasons", [])),
        })
    
    # Sort by fit_score descending
    merged.sort(key=lambda x: x.get("fit_score", 0), reverse=True)
    
    # Define CSV columns
    columns = [
        "email", "full_name", "first_name", "last_name", "title", "seniority",
        "company_name", "company_domain", "company_size", "company_industry",
        "city", "state", "country", "linkedin_url", "phone",
        "fit_score", "score_reasons", "email_verified", "source"
    ]
    
    # Generate filename
    if not filename:
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"leads_{date_str}.csv"
    
    filepath = os.path.join(get_output_dir(), filename)
    
    # Write CSV
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(merged)
    
    logger.info(f"Exported {len(merged)} leads to {filepath}")
    return filepath


def export_run_json(run_id: str) -> str:
    """
    Export run metadata and stats to JSON.
    
    Args:
        run_id: Pipeline run ID
    
    Returns:
        Path to exported JSON file
    """
    run_data = get_run(run_id)
    if not run_data:
        raise ValueError(f"Run not found: {run_id}")
    
    leads = get_leads_by_run(run_id)
    scores = get_scores_by_run(run_id)
    
    # Calculate stats
    score_values = [s["fit_score"] for s in scores if s.get("fit_score")]
    
    stats = {
        "total_leads": len(leads),
        "scored_leads": len(scores),
        "high_fit_leads": len([s for s in scores if s.get("fit_score", 0) >= 70]),
        "medium_fit_leads": len([s for s in scores if 40 <= s.get("fit_score", 0) < 70]),
        "low_fit_leads": len([s for s in scores if s.get("fit_score", 0) < 40]),
        "avg_score": round(sum(score_values) / len(score_values), 1) if score_values else 0,
        "max_score": max(score_values) if score_values else 0,
        "min_score": min(score_values) if score_values else 0,
    }
    
    # Get top leads
    top_leads = sorted(scores, key=lambda x: x.get("fit_score", 0), reverse=True)[:10]
    
    export_data = {
        "run_id": run_id,
        "icp_name": run_data.get("icp_name"),
        "source": run_data.get("source"),
        "status": run_data.get("status"),
        "started_at": run_data.get("started_at"),
        "completed_at": run_data.get("completed_at"),
        "stats": stats,
        "top_leads": [
            {
                "email": l.get("email"),
                "full_name": l.get("full_name"),
                "title": l.get("title"),
                "company_name": l.get("company_name"),
                "fit_score": l.get("fit_score"),
                "score_reasons": l.get("score_reasons", [])[:3]  # Top 3 reasons
            }
            for l in top_leads
        ],
        "icp_config": run_data.get("icp_config", {}),
        "exported_at": datetime.now().isoformat()
    }
    
    filename = f"run_{run_id}.json"
    filepath = os.path.join(get_output_dir(), filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, default=str)
    
    logger.info(f"Exported run metadata to {filepath}")
    return filepath


def export_all(run_id: str) -> Dict[str, Any]:
    """
    Export both CSV and JSON artifacts.
    
    Args:
        run_id: Pipeline run ID
    
    Returns:
        dict with paths to exported files
    """
    try:
        csv_path = export_csv(run_id)
        json_path = export_run_json(run_id)
        
        # Count exported
        leads = get_leads_by_run(run_id)
        update_run(run_id, leads_exported=len(leads))
        
        return {
            "status": "success",
            "run_id": run_id,
            "csv_path": csv_path,
            "json_path": json_path,
            "leads_exported": len(leads),
            "message": f"Exported {len(leads)} leads to {csv_path}"
        }
        
    except Exception as e:
        logger.exception("Failed to export")
        return {"status": "error", "message": str(e)}


def run(params: dict = None) -> dict:
    """Entry point for MCP execution."""
    params = params or {}
    
    run_id = params.get("run_id")
    if not run_id:
        return {"status": "error", "message": "run_id parameter required"}
    
    export_type = params.get("type", "all")
    
    if export_type == "csv":
        try:
            csv_path = export_csv(run_id, params.get("filename"))
            return {"status": "success", "csv_path": csv_path}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    elif export_type == "json":
        try:
            json_path = export_run_json(run_id)
            return {"status": "success", "json_path": json_path}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    else:  # all
        return export_all(run_id)


if __name__ == "__main__":
    params = {}
    if len(sys.argv) > 1:
        try:
            params = json.loads(sys.argv[1])
        except json.JSONDecodeError:
            print(json.dumps({"status": "error", "message": "Invalid JSON params"}))
            sys.exit(1)
    
    result = run(params)
    print(json.dumps(result, indent=2, default=str))
