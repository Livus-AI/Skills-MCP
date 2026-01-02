"""
Ingest Leads from Apollo CSV Export

Parses Apollo.io CSV exports and stores leads in the database.
"""

import sys
import json
import os
import csv
import logging
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
from db import upsert_lead, create_run, update_run, complete_run


# Apollo CSV column mappings (Apollo export format varies, handle common formats)
COLUMN_MAPPINGS = {
    # Email columns
    "email": ["email", "Email", "Email Address", "email_address", "Work Email"],
    "first_name": ["first_name", "First Name", "First", "firstName"],
    "last_name": ["last_name", "Last Name", "Last", "lastName"],
    "full_name": ["name", "Name", "Full Name", "fullName", "Person Name"],
    "title": ["title", "Title", "Job Title", "jobTitle", "Position"],
    "seniority": ["seniority", "Seniority", "Level"],
    "company_name": ["company", "Company", "Company Name", "Organization", "organization_name"],
    "company_domain": ["company_domain", "Domain", "Website", "Company Domain", "website"],
    "company_size": ["employees", "Employees", "Company Size", "# Employees", "employee_count"],
    "company_industry": ["industry", "Industry", "Company Industry"],
    "city": ["city", "City", "Person City"],
    "state": ["state", "State", "Region", "Person State"],
    "country": ["country", "Country", "Person Country"],
    "linkedin_url": ["linkedin", "LinkedIn", "LinkedIn URL", "linkedin_url", "Person Linkedin Url"],
    "phone": ["phone", "Phone", "Phone Number", "Direct Phone", "Mobile Phone"],
}


def find_column(headers: List[str], possible_names: List[str]) -> Optional[int]:
    """Find column index by checking possible names."""
    headers_lower = [h.lower().strip() for h in headers]
    for name in possible_names:
        name_lower = name.lower().strip()
        if name_lower in headers_lower:
            return headers_lower.index(name_lower)
    return None


def parse_company_size(value: str) -> Optional[str]:
    """Parse company size from various formats."""
    if not value:
        return None
    
    value = str(value).strip().lower()
    
    # Handle numeric values
    try:
        num = int(value.replace(",", "").replace("+", ""))
        if num <= 50:
            return "1-50"
        elif num <= 200:
            return "51-200"
        elif num <= 500:
            return "201-500"
        elif num <= 1000:
            return "501-1000"
        else:
            return "1000+"
    except ValueError:
        pass
    
    # Handle range strings
    if "1-10" in value or "1-50" in value:
        return "1-50"
    elif "11-50" in value or "51-200" in value:
        return "51-200"
    elif "51-200" in value or "201-500" in value:
        return "201-500"
    elif "201-500" in value or "501-1000" in value:
        return "501-1000"
    elif "500+" in value or "1000+" in value:
        return "1000+"
    
    return value


def ingest_csv(
    csv_path: str,
    icp_name: str = "csv_import",
    run_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Ingest leads from an Apollo CSV export.
    
    Args:
        csv_path: Path to the CSV file
        icp_name: ICP name to associate with this import
        run_id: Optional existing run ID to use
    
    Returns:
        dict with status, leads ingested, and run_id
    """
    if not os.path.exists(csv_path):
        return {
            "status": "error",
            "message": f"CSV file not found: {csv_path}"
        }
    
    try:
        # Create run if not provided
        if not run_id:
            run_id = create_run(icp_name, {"source": "csv", "file": csv_path}, "csv_import")
            logger.info(f"Created pipeline run: {run_id}")
        
        leads_ingested = 0
        skipped = 0
        errors = []
        
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            # Try to detect delimiter
            sample = f.read(4096)
            f.seek(0)
            
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
            except csv.Error:
                dialect = csv.excel
            
            reader = csv.reader(f, dialect)
            headers = next(reader)
            
            # Build column index map
            column_indices = {}
            for field, possible_names in COLUMN_MAPPINGS.items():
                idx = find_column(headers, possible_names)
                if idx is not None:
                    column_indices[field] = idx
            
            logger.info(f"Found columns: {list(column_indices.keys())}")
            
            # Check for required email column
            if "email" not in column_indices:
                return {
                    "status": "error",
                    "message": "Could not find email column in CSV",
                    "headers_found": headers[:20]
                }
            
            # Process rows
            for row_num, row in enumerate(reader, start=2):
                try:
                    # Extract values using column indices
                    def get_value(field: str) -> Optional[str]:
                        idx = column_indices.get(field)
                        if idx is not None and idx < len(row):
                            val = row[idx].strip()
                            return val if val else None
                        return None
                    
                    email = get_value("email")
                    if not email or "@" not in email:
                        skipped += 1
                        continue
                    
                    # Build lead data
                    first_name = get_value("first_name")
                    last_name = get_value("last_name")
                    full_name = get_value("full_name")
                    
                    # Construct full_name if not present
                    if not full_name and (first_name or last_name):
                        full_name = " ".join(filter(None, [first_name, last_name]))
                    
                    # Build location string
                    city = get_value("city")
                    state = get_value("state")
                    country = get_value("country")
                    location = ", ".join(filter(None, [city, state, country]))
                    
                    lead_data = {
                        "email": email.lower().strip(),
                        "first_name": first_name,
                        "last_name": last_name,
                        "full_name": full_name,
                        "title": get_value("title"),
                        "seniority": get_value("seniority"),
                        "company_name": get_value("company_name"),
                        "company_domain": get_value("company_domain"),
                        "company_size": parse_company_size(get_value("company_size")),
                        "company_industry": get_value("company_industry"),
                        "location": location if location else None,
                        "city": city,
                        "state": state,
                        "country": country,
                        "linkedin_url": get_value("linkedin_url"),
                        "email_verified": True,  # Assume verified from Apollo export
                        "phone": get_value("phone"),
                        "source": "apollo_csv",
                        "raw_data": {"row_number": row_num, "file": os.path.basename(csv_path)}
                    }
                    
                    upsert_lead(lead_data, run_id)
                    leads_ingested += 1
                    
                    if leads_ingested % 100 == 0:
                        logger.info(f"Ingested {leads_ingested} leads...")
                    
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
                    if len(errors) > 10:
                        break
        
        # Update run stats
        update_run(run_id, leads_fetched=leads_ingested)
        
        result = {
            "status": "success",
            "run_id": run_id,
            "leads_ingested": leads_ingested,
            "skipped": skipped,
            "message": f"Ingested {leads_ingested} leads from CSV"
        }
        
        if errors:
            result["errors"] = errors[:10]
            result["message"] += f" ({len(errors)} errors)"
        
        logger.info(result["message"])
        return result
        
    except Exception as e:
        logger.exception("Failed to ingest CSV")
        if run_id:
            complete_run(run_id, status="failed", error_message=str(e))
        return {"status": "error", "message": str(e)}


def run(params: dict = None) -> dict:
    """Entry point for MCP execution."""
    params = params or {}
    
    csv_path = params.get("csv_path")
    if not csv_path:
        return {"status": "error", "message": "csv_path parameter required"}
    
    icp_name = params.get("icp", "csv_import")
    run_id = params.get("run_id")
    
    return ingest_csv(csv_path=csv_path, icp_name=icp_name, run_id=run_id)


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
