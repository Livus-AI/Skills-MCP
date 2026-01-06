"""
AI Query Clarification Module

Evaluates if a search query is too vague and generates targeted
clarifying questions to improve search precision.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CLARIFICATION_PROMPT = """You are a B2B lead research assistant. Analyze the user's search query and determine if it needs clarification to produce quality leads.

A query needs clarification if it's missing important specifics like:
- Geographic location/region
- Industry or sector
- Company size (startup, SMB, enterprise)
- Seniority level (if not obvious from title)

Respond with a JSON object:
{{
  "needs_clarification": boolean,
  "reason": "Brief explanation of why clarification is needed (or not)",
  "questions": [
    {{
      "id": "location",
      "question": "What geographic region are you targeting?",
      "options": ["United States", "Europe", "Brazil", "Global", "Other"]
    }}
  ],
  "parsed_so_far": {{
    "titles": ["extracted titles if any"],
    "location": "extracted location if mentioned",
    "industry": "extracted industry if mentioned"
  }}
}}

Rules:
- Maximum 3 questions (prioritize most impactful)
- If query already specifies location, industry, AND title clearly, set needs_clarification: false
- Include relevant options for each question based on query context
- Be concise with questions

User Query: "{query}"
"""


def assess_query(query: str) -> Dict[str, Any]:
    """
    Assess if a query needs clarification before search.
    
    Returns:
        {
            "needs_clarification": bool,
            "reason": str,
            "questions": [...],
            "parsed_so_far": {...}
        }
    """
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        logger.warning("OPENAI_API_KEY not set, skipping clarification")
        return {"needs_clarification": False, "reason": "API key not configured"}
    
    import urllib.request
    
    prompt = CLARIFICATION_PROMPT.format(query=query)
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that responds only in valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "response_format": {"type": "json_object"}
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        
        content = result["choices"][0]["message"]["content"]
        assessment = json.loads(content)
        
        logger.info(f"Query assessment: needs_clarification={assessment.get('needs_clarification')}")
        
        return assessment
        
    except Exception as e:
        logger.error(f"Error assessing query: {e}")
        return {"needs_clarification": False, "reason": f"Error: {str(e)}"}


def enrich_query_with_answers(
    original_query: str, 
    answers: Dict[str, str]
) -> str:
    """
    Combine original query with user's answers to clarifying questions.
    
    Args:
        original_query: The user's original search query
        answers: Dict of question_id -> answer_value
        
    Returns:
        Enriched query string
    """
    parts = [original_query]
    
    # Add answers as context
    if answers.get("location"):
        parts.append(f"in {answers['location']}")
    
    if answers.get("industry"):
        parts.append(f"in {answers['industry']} industry")
    
    if answers.get("company_size"):
        parts.append(f"at {answers['company_size']} companies")
    
    if answers.get("seniority"):
        parts.append(f"with {answers['seniority']} level")
    
    enriched = " ".join(parts)
    logger.info(f"Enriched query: {enriched}")
    
    return enriched


# CLI test
if __name__ == "__main__":
    import sys
    from dotenv import load_dotenv
    load_dotenv()
    
    test_query = sys.argv[1] if len(sys.argv) > 1 else "marketing directors"
    result = assess_query(test_query)
    print(json.dumps(result, indent=2))
