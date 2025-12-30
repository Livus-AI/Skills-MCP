"""
Workflow: example_hello_world
Description: A simple example workflow that demonstrates the basic structure
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
    A simple hello world workflow.
    
    Args:
        params: Optional dictionary with:
            - name (str): Name to greet (default: "World")
            - uppercase (bool): Whether to uppercase the greeting (default: False)
    
    Returns:
        dict: The greeting result
    """
    params = params or {}
    
    name = params.get("name", "World")
    uppercase = params.get("uppercase", False)
    
    greeting = f"Hello, {name}!"
    
    if uppercase:
        greeting = greeting.upper()
    
    return {
        "status": "success",
        "greeting": greeting,
        "timestamp": datetime.now().isoformat(),
        "params_received": params
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
