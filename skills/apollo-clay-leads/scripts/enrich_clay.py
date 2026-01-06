"""
Enrich Leads via Clay Webhook

Sends leads to Clay's table webhook for enrichment.
"""

import sys
import json
import os
import time
import logging
from typing import Dict, Any, List, Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Clay configuration
CLAY_WEBHOOK_URL = os.environ.get("CLAY_WEBHOOK_URL", "")
CLAY_API_KEY = os.environ.get("CLAY_API_KEY", "")

# Import db module
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from db import get_leads_by_run, save_enrichment, update_run


def make_request(url: str, data: Dict[str, Any], retries: int = 3) -> Dict[str, Any]:
    """Make HTTP POST request with retries and exponential backoff."""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Add API key if available
    if CLAY_API_KEY:
        headers["Authorization"] = f"Bearer {CLAY_API_KEY}"
    
    for attempt in range(retries):
        try:
            req = Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
            
            with urlopen(req, timeout=30) as response:
                response_text = response.read().decode("utf-8")
                if response_text:
                    try:
                        return json.loads(response_text)
                    except json.JSONDecodeError:
                        # Webhook might return plain text like "Accepted"
                        return {"status": "success", "message": response_text}
                return {"status": "accepted"}
                
        except HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else ""
            logger.warning(f"HTTP {e.code} on attempt {attempt + 1}: {error_body[:200]}")
            
            if e.code == 429:  # Rate limited
                wait_time = (2 ** attempt) * 2
                logger.info(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
            elif e.code >= 500:  # Server error, retry
                wait_time = 2 ** attempt
                time.sleep(wait_time)
            else:
                raise
                
        except URLError as e:
            logger.warning(f"Network error on attempt {attempt + 1}: {e.reason}")
            wait_time = 2 ** attempt
            time.sleep(wait_time)
    
    raise Exception(f"Failed after {retries} retries")


def send_to_clay_webhook(lead: Dict[str, Any], webhook_url: str) -> Dict[str, Any]:
    """Send a single lead to Clay webhook for enrichment."""
    # Prepare payload for Clay
    payload = {
        "email": lead.get("email"),
        "first_name": lead.get("first_name"),
        "last_name": lead.get("last_name"),
        "full_name": lead.get("full_name"),
        "title": lead.get("title"),
        "company": lead.get("company_name"),
        "company_domain": lead.get("company_domain"),
        "linkedin_url": lead.get("linkedin_url"),
        "lead_id": lead.get("id"),  # For callback correlation
    }
    
    return make_request(webhook_url, payload)


def enrich_leads(
    run_id: str,
    webhook_url: Optional[str] = None,
    batch_size: int = 10
) -> Dict[str, Any]:
    """
    Enrich leads via Clay webhook.
    
    Args:
        run_id: Pipeline run ID to get leads from
        webhook_url: Optional webhook URL (defaults to CLAY_WEBHOOK_URL env var)
        batch_size: Number of leads to process before pausing
    
    Returns:
        dict with status and enrichment counts
    """
    webhook_url = webhook_url or CLAY_WEBHOOK_URL
    
    if not webhook_url:
        logger.warning("No Clay webhook URL configured. Skipping enrichment.")
        return {
            "status": "skipped",
            "message": "No CLAY_WEBHOOK_URL configured. Set environment variable or pass webhook_url parameter.",
            "leads_enriched": 0
        }
    
    try:
        # Get leads for this run
        leads = get_leads_by_run(run_id)
        
        if not leads:
            return {
                "status": "success",
                "message": "No leads to enrich",
                "leads_enriched": 0
            }
        
        logger.info(f"Enriching {len(leads)} leads via Clay webhook...")
        
        enriched = 0
        failed = 0
        errors = []
        
        for i, lead in enumerate(leads):
            try:
                response = send_to_clay_webhook(lead, webhook_url)
                
                # Store enrichment record
                save_enrichment(
                    lead_id=lead["id"],
                    enrichment_data={
                        "webhook_response": response,
                        "sent_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                    },
                    status="pending"  # Clay enrichment is async
                )
                
                enriched += 1
                
                if enriched % batch_size == 0:
                    logger.info(f"Sent {enriched}/{len(leads)} leads to Clay")
                    time.sleep(0.5)  # Rate limiting courtesy
                
            except Exception as e:
                failed += 1
                errors.append({"lead_id": lead["id"], "error": str(e)})
                logger.warning(f"Failed to enrich lead {lead['id']}: {e}")
        
        # Update run stats
        update_run(run_id, leads_enriched=enriched)
        
        result = {
            "status": "success",
            "run_id": run_id,
            "leads_enriched": enriched,
            "failed": failed,
            "message": f"Sent {enriched} leads to Clay for enrichment"
        }
        
        if errors:
            result["errors"] = errors[:10]
        
        # Note: Clay enrichment is async - data comes back via callback
        result["note"] = "Clay enrichment is asynchronous. Configure a callback webhook in Clay to receive enriched data."
        
        logger.info(result["message"])
        return result
        
    except Exception as e:
        logger.exception("Failed to enrich leads")
        return {"status": "error", "message": str(e)}


def run(params: dict = None) -> dict:
    """Entry point for MCP execution."""
    params = params or {}
    
    run_id = params.get("run_id")
    if not run_id:
        return {"status": "error", "message": "run_id parameter required"}
    
    webhook_url = params.get("webhook_url")
    batch_size = params.get("batch_size", 10)
    
    return enrich_leads(run_id=run_id, webhook_url=webhook_url, batch_size=batch_size)


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
