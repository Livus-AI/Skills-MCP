"""
SQLite Storage Layer for Lead Generation Pipeline

Provides persistent storage for leads, enrichments, and pipeline runs.
"""

import sqlite3
import json
import os
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

# Database path relative to skill directory
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "leads.db")


def get_db_path() -> str:
    """Get database path, creating directory if needed."""
    os.makedirs(DB_DIR, exist_ok=True)
    return DB_PATH


@contextmanager
def get_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Initialize database tables."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Leads table - raw lead data from Apollo
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE,
                first_name TEXT,
                last_name TEXT,
                full_name TEXT,
                title TEXT,
                seniority TEXT,
                company_name TEXT,
                company_domain TEXT,
                company_size TEXT,
                company_industry TEXT,
                location TEXT,
                city TEXT,
                state TEXT,
                country TEXT,
                linkedin_url TEXT,
                email_verified INTEGER DEFAULT 0,
                phone TEXT,
                source TEXT DEFAULT 'apollo',
                raw_data TEXT,
                run_id TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Enrichments table - Clay enrichment results
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS enrichments (
                id TEXT PRIMARY KEY,
                lead_id TEXT NOT NULL,
                enrichment_source TEXT DEFAULT 'clay',
                enrichment_data TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lead_id) REFERENCES leads(id)
            )
        """)
        
        # Pipeline runs table - run metadata
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_runs (
                id TEXT PRIMARY KEY,
                icp_name TEXT,
                icp_config TEXT,
                source TEXT,
                status TEXT DEFAULT 'running',
                leads_fetched INTEGER DEFAULT 0,
                leads_enriched INTEGER DEFAULT 0,
                leads_scored INTEGER DEFAULT 0,
                leads_exported INTEGER DEFAULT 0,
                error_message TEXT,
                started_at TEXT DEFAULT CURRENT_TIMESTAMP,
                completed_at TEXT
            )
        """)
        
        # Scores table - lead scoring results
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scores (
                id TEXT PRIMARY KEY,
                lead_id TEXT NOT NULL,
                run_id TEXT,
                fit_score INTEGER,
                score_reasons TEXT,
                icp_name TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lead_id) REFERENCES leads(id)
            )
        """)
        
        # Create indexes for common queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_run_id ON leads(run_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_scores_lead_id ON scores(lead_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_scores_run_id ON scores(run_id)")


def generate_id() -> str:
    """Generate a unique ID."""
    return str(uuid.uuid4())[:8]


# ============ Lead Operations ============

def upsert_lead(lead_data: Dict[str, Any], run_id: str) -> str:
    """Insert or update a lead by email. Returns lead ID."""
    init_db()
    
    lead_id = lead_data.get("id") or generate_id()
    email = lead_data.get("email", "").lower().strip()
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Check if lead exists by email
        cursor.execute("SELECT id FROM leads WHERE email = ?", (email,))
        existing = cursor.fetchone()
        
        if existing:
            lead_id = existing["id"]
            cursor.execute("""
                UPDATE leads SET
                    first_name = COALESCE(?, first_name),
                    last_name = COALESCE(?, last_name),
                    full_name = COALESCE(?, full_name),
                    title = COALESCE(?, title),
                    seniority = COALESCE(?, seniority),
                    company_name = COALESCE(?, company_name),
                    company_domain = COALESCE(?, company_domain),
                    company_size = COALESCE(?, company_size),
                    company_industry = COALESCE(?, company_industry),
                    location = COALESCE(?, location),
                    city = COALESCE(?, city),
                    state = COALESCE(?, state),
                    country = COALESCE(?, country),
                    linkedin_url = COALESCE(?, linkedin_url),
                    email_verified = COALESCE(?, email_verified),
                    phone = COALESCE(?, phone),
                    raw_data = ?,
                    run_id = ?,
                    updated_at = ?
                WHERE id = ?
            """, (
                lead_data.get("first_name"),
                lead_data.get("last_name"),
                lead_data.get("full_name"),
                lead_data.get("title"),
                lead_data.get("seniority"),
                lead_data.get("company_name"),
                lead_data.get("company_domain"),
                lead_data.get("company_size"),
                lead_data.get("company_industry"),
                lead_data.get("location"),
                lead_data.get("city"),
                lead_data.get("state"),
                lead_data.get("country"),
                lead_data.get("linkedin_url"),
                1 if lead_data.get("email_verified") else 0,
                lead_data.get("phone"),
                json.dumps(lead_data.get("raw_data", {})),
                run_id,
                datetime.now().isoformat(),
                lead_id
            ))
        else:
            cursor.execute("""
                INSERT INTO leads (
                    id, email, first_name, last_name, full_name, title, seniority,
                    company_name, company_domain, company_size, company_industry,
                    location, city, state, country, linkedin_url, email_verified,
                    phone, source, raw_data, run_id, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                lead_id,
                email,
                lead_data.get("first_name"),
                lead_data.get("last_name"),
                lead_data.get("full_name"),
                lead_data.get("title"),
                lead_data.get("seniority"),
                lead_data.get("company_name"),
                lead_data.get("company_domain"),
                lead_data.get("company_size"),
                lead_data.get("company_industry"),
                lead_data.get("location"),
                lead_data.get("city"),
                lead_data.get("state"),
                lead_data.get("country"),
                lead_data.get("linkedin_url"),
                1 if lead_data.get("email_verified") else 0,
                lead_data.get("phone"),
                lead_data.get("source", "apollo"),
                json.dumps(lead_data.get("raw_data", {})),
                run_id,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
    
    return lead_id


def get_leads_by_run(run_id: str) -> List[Dict[str, Any]]:
    """Get all leads for a pipeline run."""
    init_db()
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leads WHERE run_id = ?", (run_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_lead_by_id(lead_id: str) -> Optional[Dict[str, Any]]:
    """Get a lead by ID."""
    init_db()
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


# ============ Enrichment Operations ============

def save_enrichment(lead_id: str, enrichment_data: Dict[str, Any], status: str = "completed") -> str:
    """Save enrichment data for a lead."""
    init_db()
    
    enrichment_id = generate_id()
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO enrichments (id, lead_id, enrichment_data, status, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            enrichment_id,
            lead_id,
            json.dumps(enrichment_data),
            status,
            datetime.now().isoformat()
        ))
    
    return enrichment_id


def get_enrichment_by_lead(lead_id: str) -> Optional[Dict[str, Any]]:
    """Get enrichment data for a lead."""
    init_db()
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM enrichments WHERE lead_id = ? ORDER BY created_at DESC LIMIT 1",
            (lead_id,)
        )
        row = cursor.fetchone()
        if row:
            result = dict(row)
            result["enrichment_data"] = json.loads(result["enrichment_data"] or "{}")
            return result
        return None


# ============ Score Operations ============

def save_score(lead_id: str, run_id: str, fit_score: int, score_reasons: List[str], icp_name: str) -> str:
    """Save scoring results for a lead."""
    init_db()
    
    score_id = generate_id()
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO scores (id, lead_id, run_id, fit_score, score_reasons, icp_name, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            score_id,
            lead_id,
            run_id,
            fit_score,
            json.dumps(score_reasons),
            icp_name,
            datetime.now().isoformat()
        ))
    
    return score_id


def get_scores_by_run(run_id: str) -> List[Dict[str, Any]]:
    """Get all scores for a pipeline run."""
    init_db()
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.*, l.email, l.full_name, l.title, l.company_name
            FROM scores s
            JOIN leads l ON s.lead_id = l.id
            WHERE s.run_id = ?
            ORDER BY s.fit_score DESC
        """, (run_id,))
        rows = cursor.fetchall()
        results = []
        for row in rows:
            result = dict(row)
            result["score_reasons"] = json.loads(result["score_reasons"] or "[]")
            results.append(result)
        return results


# ============ Pipeline Run Operations ============

def create_run(icp_name: str, icp_config: Dict[str, Any], source: str) -> str:
    """Create a new pipeline run record."""
    init_db()
    
    run_id = generate_id()
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO pipeline_runs (id, icp_name, icp_config, source, status, started_at)
            VALUES (?, ?, ?, ?, 'running', ?)
        """, (
            run_id,
            icp_name,
            json.dumps(icp_config),
            source,
            datetime.now().isoformat()
        ))
    
    return run_id


def update_run(run_id: str, **kwargs):
    """Update pipeline run with stats."""
    init_db()
    
    allowed_fields = [
        "status", "leads_fetched", "leads_enriched", "leads_scored",
        "leads_exported", "error_message", "completed_at"
    ]
    
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
    if not updates:
        return
    
    set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
    values = list(updates.values()) + [run_id]
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE pipeline_runs SET {set_clause} WHERE id = ?", values)


def get_run(run_id: str) -> Optional[Dict[str, Any]]:
    """Get pipeline run by ID."""
    init_db()
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pipeline_runs WHERE id = ?", (run_id,))
        row = cursor.fetchone()
        if row:
            result = dict(row)
            result["icp_config"] = json.loads(result["icp_config"] or "{}")
            return result
        return None


def complete_run(run_id: str, status: str = "completed", error_message: str = None):
    """Mark a pipeline run as completed."""
    update_run(
        run_id,
        status=status,
        error_message=error_message,
        completed_at=datetime.now().isoformat()
    )


# ============ Utility ============

def run(params: dict = None) -> dict:
    """Entry point for MCP execution - initialize database."""
    params = params or {}
    action = params.get("action", "init")
    
    if action == "init":
        init_db()
        return {"status": "success", "message": "Database initialized", "db_path": get_db_path()}
    
    elif action == "get_run":
        run_id = params.get("run_id")
        if not run_id:
            return {"status": "error", "message": "run_id required"}
        run_data = get_run(run_id)
        if run_data:
            return {"status": "success", "run": run_data}
        return {"status": "error", "message": "Run not found"}
    
    elif action == "get_leads":
        run_id = params.get("run_id")
        if not run_id:
            return {"status": "error", "message": "run_id required"}
        leads = get_leads_by_run(run_id)
        return {"status": "success", "leads": leads, "count": len(leads)}
    
    return {"status": "error", "message": f"Unknown action: {action}"}


if __name__ == "__main__":
    import sys
    
    params = {}
    if len(sys.argv) > 1:
        try:
            params = json.loads(sys.argv[1])
        except json.JSONDecodeError:
            print(json.dumps({"status": "error", "message": "Invalid JSON params"}))
            sys.exit(1)
    
    result = run(params)
    print(json.dumps(result, indent=2, default=str))
