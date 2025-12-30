"""
Workflow: example_slack_message
Description: Example workflow that posts a message to Slack via webhook
Created: 2024-12-30 00:00:00
"""

import os
import sys
import json
import requests
from datetime import datetime
from typing import Any, Dict, Optional

def run(params: dict = None) -> dict:
    """
    Post a message to Slack using a webhook URL.
    
    Args:
        params: Dictionary with:
            - webhook_url (str): Slack webhook URL (or set SLACK_WEBHOOK_URL env var)
            - message (str): The message to post
            - channel (str): Optional channel override
            - username (str): Optional username override
    
    Returns:
        dict: Status of the Slack post operation
    """
    params = params or {}
    
    # Get webhook URL from params or environment
    webhook_url = params.get("webhook_url") or os.environ.get("SLACK_WEBHOOK_URL")
    
    if not webhook_url:
        return {
            "status": "error",
            "message": "No webhook_url provided and SLACK_WEBHOOK_URL not set"
        }
    
    message = params.get("message", "Hello from Workflows MCP!")
    
    # Build the payload
    payload = {
        "text": message
    }
    
    if params.get("channel"):
        payload["channel"] = params["channel"]
    
    if params.get("username"):
        payload["username"] = params["username"]
    
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            return {
                "status": "success",
                "message": "Message posted to Slack successfully",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "error",
                "message": f"Slack API returned status {response.status_code}",
                "response": response.text
            }
    except requests.RequestException as e:
        return {
            "status": "error",
            "message": f"Failed to post to Slack: {str(e)}"
        }

if __name__ == "__main__":
    # Allow passing params as JSON via command line
    params = {}
    if len(sys.argv) > 1:
        try:
            params = json.loads(sys.argv[1])
        except json.JSONDecodeError:
            print("Warning: Could not parse params as JSON")
    
    result = run(params)
    print(json.dumps(result, indent=2, default=str))
