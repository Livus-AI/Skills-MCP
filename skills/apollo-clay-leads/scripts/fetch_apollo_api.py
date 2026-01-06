"""
Fetch Leads from Apollo.io API

Uses the /v1/mixed_people/search endpoint to fetch leads based on ICP filters
or natural language query.
"""

import sys
import json
import os
import time
import logging
import re
from typing import Dict, Any, List, Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# Auto-load .env file
def _load_env():
    """Load environment variables from .env file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    for path in [
        os.path.join(script_dir, "..", "..", "..", ".env"),  # Project root
        os.path.join(script_dir, "..", ".env"),  # Skill dir
    ]:
        env_path = os.path.abspath(path)
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, _, value = line.partition("=")
                        value = value.strip().strip('"').strip("'")
                        if key and value and key not in os.environ:
                            os.environ[key] = value
            break

_load_env()

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


def parse_query_to_filters(query: str) -> Dict[str, Any]:
    """
    Parse a natural language query into Apollo API filters using LLM.
    
    Uses OpenAI to intelligently understand the query and extract
    relevant Apollo API filter parameters.
    
    Args:
        query: Natural language search query
    
    Returns:
        dict with Apollo API filter fields
    """
    from parse_query import parse_query_with_llm
    return parse_query_with_llm(query)


def make_request(url: str, data: Dict[str, Any], retries: int = 3) -> Dict[str, Any]:
    """Make HTTP POST request with retries and exponential backoff."""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Cache-Control": "no-cache",
        "X-Api-Key": APOLLO_API_KEY,
        # Browser-like headers to avoid Cloudflare blocking
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://app.apollo.io",
        "Referer": "https://app.apollo.io/"
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


def search_people(filters: Dict[str, Any], page: int = 1, per_page: int = 25) -> Dict[str, Any]:
    """Search for people using Apollo API."""
    url = f"{APOLLO_API_BASE}/mixed_people/search"
    
    # Build request payload
    payload = {
        "page": page,
        "per_page": min(per_page, 100),  # Apollo max is 100
        **filters
    }
    
    # Remove non-API fields
    payload.pop("scoring_weights", None)
    payload.pop("apollo_params", None)
    
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
    icp_name: Optional[str] = None,
    query: Optional[str] = None,
    limit: int = 100,
    run_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch leads from Apollo API based on ICP configuration or natural language query.
    
    Args:
        icp_name: Name of ICP config file (without .json)
        query: Natural language query string (alternative to icp_name)
        limit: Maximum number of leads to fetch
        run_id: Optional existing run ID to use
    
    Returns:
        dict with status, leads fetched, and run_id
    """
    # Build filters from query or ICP
    if query:
        filters = parse_query_to_filters(query)
        icp_config = {"name": "query", "description": query, "filters": filters}
        logger.info(f"Parsed query into filters: {json.dumps(filters, indent=2)}")
    elif icp_name:
        icp_config = load_icp_config(icp_name)
        filters = icp_config.get("filters", {})
        logger.info(f"Loaded ICP config: {icp_name}")
    else:
        return {"status": "error", "message": "Either icp_name or query required"}
    
    # Create run if needed
    if not run_id:
        source = "apollo_api"
        run_id = create_run(icp_config.get("name", "query"), icp_config, source)
        logger.info(f"Created pipeline run: {run_id}")
    
    # Require API key
    if not APOLLO_API_KEY:
        raise ValueError("APOLLO_API_KEY not set. Add it to your .env file.")
    
    try:
        leads_fetched = 0
        page = 1
        per_page = min(limit, 25)
        
        while leads_fetched < limit:
            response = search_people(filters, page=page, per_page=per_page)
            
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
                upsert_lead(lead_data, run_id)
                leads_fetched += 1
            
            logger.info(f"Fetched {leads_fetched}/{limit} leads from Apollo")
            
            # Check if there are more pages
            pagination = response.get("pagination", {})
            if page >= pagination.get("total_pages", 1):
                break
            
            page += 1
            time.sleep(0.5)  # Rate limiting courtesy
        
        # Update run stats
        update_run(run_id, leads_fetched=leads_fetched)
        
        return {
            "status": "success",
            "run_id": run_id,
            "leads_fetched": leads_fetched,
            "source": "apollo_api",
            "message": f"Fetched {leads_fetched} leads from Apollo API"
        }
        
    except Exception as e:
        logger.exception("Failed to fetch leads")
        if run_id:
            complete_run(run_id, status="failed", error_message=str(e))
        return {"status": "error", "message": str(e)}


def enrich_person_with_apollo(lead: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enrich a single lead using Apollo's /v1/people/match endpoint.
    
    This endpoint works on Apollo's FREE tier (uses 1 credit per match).
    
    Args:
        lead: Lead dict with at least name+company or linkedin_url
    
    Returns:
        Enriched lead dict with email, phone, company data
    """
    if not APOLLO_API_KEY:
        raise ValueError("APOLLO_API_KEY not set. Add it to your .env file.")
    
    url = f"{APOLLO_API_BASE}/people/match"
    
    # Build payload - Apollo accepts various identifiers
    payload = {
        "api_key": APOLLO_API_KEY,
        "reveal_personal_emails": False,
        "reveal_phone_number": True
    }
    
    # Prefer LinkedIn URL if available (most accurate)
    if lead.get("linkedin_url"):
        payload["linkedin_url"] = lead["linkedin_url"]
    else:
        # Fall back to name + company
        if lead.get("first_name"):
            payload["first_name"] = lead["first_name"]
        if lead.get("last_name"):
            payload["last_name"] = lead["last_name"]
        if lead.get("company_name"):
            payload["organization_name"] = lead["company_name"]
        if lead.get("company_domain"):
            payload["domain"] = lead["company_domain"]
    
    try:
        response = make_request(url, payload)
        person = response.get("person", {})
        
        if not person:
            logger.warning(f"No match found for {lead.get('full_name', 'unknown')}")
            return lead  # Return original lead if no match
        
        # Merge Apollo data into lead
        org = person.get("organization", {})
        
        enriched = {
            **lead,
            "email": person.get("email") or lead.get("email"),
            "email_verified": person.get("email_status") == "verified",
            "phone": None,
            "seniority": person.get("seniority"),
            "title": person.get("title") or lead.get("title"),
            "company_name": org.get("name") or lead.get("company_name"),
            "company_domain": org.get("primary_domain") or lead.get("company_domain"),
            "company_industry": org.get("industry"),
            "company_size": _normalize_employee_count(org.get("estimated_num_employees")),
            "city": person.get("city"),
            "state": person.get("state"),
            "country": person.get("country"),
            "apollo_id": person.get("id"),
            "enriched": True
        }
        
        # Extract phone if available
        phones = person.get("phone_numbers", [])
        if phones:
            enriched["phone"] = phones[0].get("sanitized_number")
        
        logger.info(f"Enriched: {enriched.get('full_name')} -> {enriched.get('email')}")
        return enriched
        
    except HTTPError as e:
        if e.code == 404:
            logger.warning(f"No Apollo match for {lead.get('full_name', 'unknown')}")
            return lead
        raise


def enrich_leads_with_apollo(
    leads: List[Dict[str, Any]],
    run_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Enrich multiple leads using Apollo's /v1/people/match endpoint.
    
    Uses Apollo FREE tier (1 credit per lead, 100 credits/month free).
    
    Args:
        leads: List of leads to enrich (from Apify or other source)
        run_id: Optional pipeline run ID for database storage
    
    Returns:
        dict with status, enriched leads count, and leads list
    """
    if not APOLLO_API_KEY:
        raise ValueError("APOLLO_API_KEY not set. Add it to your .env file.")
    
    enriched_leads = []
    enriched_count = 0
    failed_count = 0
    
    for i, lead in enumerate(leads):
        try:
            enriched = enrich_person_with_apollo(lead)
            
            if enriched.get("enriched"):
                enriched_count += 1
            
            # Store in database if run_id provided
            if run_id:
                upsert_lead(enriched, run_id)
            
            enriched_leads.append(enriched)
            
            # Rate limiting - Apollo allows ~50 requests/minute
            if (i + 1) % 10 == 0:
                logger.info(f"Enriched {i + 1}/{len(leads)} leads")
                time.sleep(1)
                
        except Exception as e:
            logger.warning(f"Failed to enrich lead {i}: {e}")
            failed_count += 1
            enriched_leads.append(lead)  # Keep original
    
    # Update run stats if provided
    if run_id:
        update_run(run_id, leads_fetched=len(enriched_leads))
    
    return {
        "status": "success",
        "leads": enriched_leads,
        "enriched_count": enriched_count,
        "failed_count": failed_count,
        "total_count": len(enriched_leads),
        "message": f"Enriched {enriched_count}/{len(leads)} leads with Apollo"
    }


def _normalize_employee_count(count: Optional[int]) -> Optional[str]:
    """Convert employee count to range string."""
    if not count:
        return None
    if count <= 50:
        return "1-50"
    elif count <= 200:
        return "51-200"
    elif count <= 500:
        return "201-500"
    elif count <= 1000:
        return "501-1000"
    else:
        return "1000+"


def run(params: dict = None) -> dict:
    """Entry point for MCP execution."""
    params = params or {}
    
    # Check if this is an enrichment request
    if params.get("enrich") and params.get("leads"):
        return enrich_leads_with_apollo(
            leads=params.get("leads"),
            run_id=params.get("run_id")
        )
    
    return fetch_leads(
        icp_name=params.get("icp"),
        query=params.get("query"),
        limit=params.get("limit", 100),
        run_id=params.get("run_id")
    )


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

