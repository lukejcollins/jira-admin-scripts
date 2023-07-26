""" This script will list all the audit actions for an organization. """
import json
import os
import requests

# Check if the .env var exists and load the environment variables
env_path = os.path.join(os.path.dirname(__file__), '.', '.env')
if os.path.exists(env_path):
    with open(env_path, encoding="utf-8") as file:
        for line in file:
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

ORG_ID = os.environ.get('ORG_ID')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')

url = f"https://api.atlassian.com/admin/v1/orgs/{ORG_ID}/event-actions"

print(url)

headers = {
  "Accept": "application/json",
  "Authorization": f"Bearer {ACCESS_TOKEN}",
}

response = requests.request(
   "GET",
   url,
   headers=headers,
   timeout=30
)

print(json.dumps(json.loads(response.text), sort_keys=True, indent=4,
                 separators=(",", ": ")))
