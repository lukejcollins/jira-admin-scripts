import csv
import requests
from requests.auth import HTTPBasicAuth
import os

# Check if the .env var exists and load the environment variables
env_path = os.path.join(os.path.dirname(__file__), ".", ".env")
if os.path.exists(env_path):
    with open(env_path, encoding="utf-8") as file:
        for line in file:
            key, value = line.strip().split("=", 1)
            os.environ[key] = value

# Replace these with your actual Jira domain, email, and token
JIRA_URL = os.environ.get("JIRA_URL")
USER_EMAIL = os.environ.get("USER_EMAIL")
API_TOKEN = os.environ.get("API_TOKEN")

# Constants
csv_file_path = 'issues.csv'
url = f'{JIRA_URL}/rest/servicedesk/1/servicedesk/sla/admin/task/destructive/reconstruct?force=true'
auth = HTTPBasicAuth(USER_EMAIL, API_TOKEN)
content_type = 'application/json'

# Function to read issue keys from CSV
def read_issue_keys_from_csv(file_path):
    issue_keys = []
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            issue_keys.append(row['issue_key'])
    return issue_keys

# Function to make the POST request
def post_issue_keys(issue_keys):
    headers = {
        'Content-Type': content_type,
    }
    payload = issue_keys
    response = requests.post(url, json=payload, headers=headers,auth=auth)
    
    if response.ok:
        print('Request successful:', response.text)
    else:
        print('Request failed with status code:', response.status_code, 'and reason:', response.text)

# Main logic
if __name__ == '__main__':
    issue_keys = read_issue_keys_from_csv(csv_file_path)
    if issue_keys:
        post_issue_keys(issue_keys)
    else:
        print('No issue keys found in the CSV.')
