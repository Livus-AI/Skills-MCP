
import os
import sys
import logging
from urllib.request import Request, urlopen
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load env manually to avoid relative import issues
script_dir = os.path.dirname(os.path.abspath(__file__))
env_paths = [
    os.path.join(script_dir, "..", ".env"),
    os.path.join(script_dir, "..", "..", "..", ".env")
]

for env_path in env_paths:
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    os.environ[k] = v.strip('"').strip("'")
        break

APIFY_API_KEY = os.environ.get("APIFY_API_KEY")

def fetch_logs(run_id):
    if not APIFY_API_KEY:
        print("Error: APIFY_API_KEY not found in env")
        return
        
    url = f"https://api.apify.com/v2/actor-runs/{run_id}/log?token={APIFY_API_KEY}"
    try:
        req = Request(url)
        with urlopen(req) as response:
            print(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error fetching logs: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 fetch_logs.py <run_id>")
    else:
        fetch_logs(sys.argv[1])
