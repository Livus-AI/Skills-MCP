"""
Fetch Leads from Apollo.io API

Uses the /v1/mixed_people/search endpoint to fetch leads based on ICP filters.
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

# Apollo API configuration
APOLLO_API_BASE = "https://api.apollo.io/v1"
APOLLO_API_KEY = os.environ.get("APOLLO_API_KEY", "")

# Import db module
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from db import upsert_lead, create_run, update_run, complete_run


def load_icp_config(icp_name: str) -> Dict[str, Any]:
    """Load ICP configuration from file."""
    config_path = os.path.join(SCRIPT_DIR, "icp_configs", f"{icp_name}.json")
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"ICP config not found: {config_path}")
    
    with open(config_path, "r") as f:
        return json.load(f)


def make_request(url: str, data: Dict[str, Any], retries: int = 3) -> Dict[str, Any]:
    """Make HTTP POST request with retries and exponential backoff."""
    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "X-Api-Key": APOLLO_API_KEY
    }
    
    for attempt in range(retries):
        try:
            req = Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
            
            with urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
                
        except HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else ""
            logger.warning(f"HTTP {e.code} on attempt {attempt + 1}: {error_body[:200]}")
            
            if e.code == 429:  # Rate limited
                wait_time = (2 ** attempt) * 5  # Longer wait for rate limits
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


def search_people(icp_config: Dict[str, Any], page: int = 1, per_page: int = 25) -> Dict[str, Any]:
    """Search for people using Apollo API."""
    url = f"{APOLLO_API_BASE}/mixed_people/search"
    
    filters = icp_config.get("filters", {})
    apollo_params = icp_config.get("apollo_params", {})
    
    # Build request payload
    payload = {
        "page": page,
        "per_page": min(per_page, 100),  # Apollo max is 100
        **filters,
        **apollo_params
    }
    
    # Remove nested apollo_params if present
    payload.pop("apollo_params", None)
    payload.pop("scoring_weights", None)
    
    logger.info(f"Searching Apollo API (page {page}, per_page {per_page})...")
    return make_request(url, payload)


def normalize_apollo_person(person: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize Apollo person data to our lead schema."""
    org = person.get("organization", {}) or {}
    
    # Determine company size range
    employees = org.get("estimated_num_employees")
    if employees:
        if employees <= 50:
            company_size = "1-50"
        elif employees <= 200:
            company_size = "51-200"
        elif employees <= 500:
            company_size = "201-500"
        elif employees <= 1000:
            company_size = "501-1000"
        else:
            company_size = "1000+"
    else:
        company_size = None
    
    return {
        "email": person.get("email", ""),
        "first_name": person.get("first_name"),
        "last_name": person.get("last_name"),
        "full_name": person.get("name"),
        "title": person.get("title"),
        "seniority": person.get("seniority"),
        "company_name": org.get("name"),
        "company_domain": org.get("primary_domain") or org.get("website_url"),
        "company_size": company_size,
        "company_industry": org.get("industry"),
        "location": person.get("city") or person.get("state") or person.get("country"),
        "city": person.get("city"),
        "state": person.get("state"),
        "country": person.get("country"),
        "linkedin_url": person.get("linkedin_url"),
        "email_verified": person.get("email_status") == "verified",
        "phone": (person.get("phone_numbers") or [{}])[0].get("sanitized_number") if person.get("phone_numbers") else None,
        "source": "apollo_api",
        "raw_data": person
    }


def fetch_leads(
    icp_name: str,
    limit: int = 100,
    run_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch leads from Apollo API based on ICP configuration.
    
    Args:
        icp_name: Name of ICP config file (without .json)
        limit: Maximum number of leads to fetch
        run_id: Optional existing run ID to use
    
    Returns:
        dict with status, leads fetched, and run_id
    """
    if not APOLLO_API_KEY:
        return {
            "status": "error",
            "message": "APOLLO_API_KEY environment variable not set"
        }
    
    try:
        # Load ICP config
        icp_config = load_icp_config(icp_name)
        logger.info(f"Loaded ICP config: {icp_name}")
        
        # Create or use existing run
        if not run_id:
            run_id = create_run(icp_name, icp_config, "apollo_api")
            logger.info(f"Created pipeline run: {run_id}")
        
        leads_fetched = 0
        page = 1
        per_page = min(limit, 25)
        all_leads = []
        
        while leads_fetched < limit:
            try:
                response = search_people(icp_config, page=page, per_page=per_page)
                
                people = response.get("people", [])
                if not people:
                    logger.info("No more results from Apollo")
                    break
                
                for person in people:
                    if leads_fetched >= limit:
                        break
                    
                    # Skip if no email
                    if not person.get("email"):
                        continue
                    
                    # Normalize and store
                    lead_data = normalize_apollo_person(person)
                    lead_id = upsert_lead(lead_data, run_id)
                    all_leads.append({"id": lead_id, **lead_data})
                    leads_fetched += 1
                
                logger.info(f"Fetched {leads_fetched}/{limit} leads from Apollo")
                
                # Check if there are more pages
                pagination = response.get("pagination", {})
                if page >= pagination.get("total_pages", 1):
                    break
                
                page += 1
                time.sleep(0.5)  # Rate limiting courtesy
                
            except Exception as e:
                logger.error(f"Error fetching page {page}: {e}")
                break
        
        # Update run stats
        update_run(run_id, leads_fetched=leads_fetched)
        
        return {
            "status": "success",
            "run_id": run_id,
            "leads_fetched": leads_fetched,
            "icp_name": icp_name,
            "message": f"Fetched {leads_fetched} leads from Apollo API"
        }
        
    except FileNotFoundError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        logger.exception("Failed to fetch leads")
        if run_id:
            complete_run(run_id, status="failed", error_message=str(e))
        return {"status": "error", "message": str(e)}


def run(params: dict = None) -> dict:
    """Entry point for MCP execution."""
    params = params or {}
    
    icp_name = params.get("icp", "icp_v1")
    limit = params.get("limit", 100)
    run_id = params.get("run_id")
    
    return fetch_leads(icp_name=icp_name, limit=limit, run_id=run_id)


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
