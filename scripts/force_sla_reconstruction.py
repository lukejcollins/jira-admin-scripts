"""
This script is designed to reconstruct the SLA (Service Level Agreement) for
a set of Jira Service Desk issues. It reads issue keys from a CSV file and
sends a POST request to the Jira API to trigger the SLA reconstruction
process for those issues.

The script starts by checking if a `.env` file exists in the same directory
as the script. If the file exists, it reads the environment variables from
the file and stores them in the `os.environ` dictionary. These environment
variables should contain the Jira URL, user email, and API token required for
authentication.

Next, the script defines the following constants:
- `csv_file_path`: The path to the CSV file containing the issue keys.
- `url`: The URL endpoint for the Jira API to reconstruct the SLA.
- `auth`: An instance of `HTTPBasicAuth` using the user email and API token
 for authentication.
- `content_type`: The content type for the API request (application/json).

The script includes two helper functions:
1. `read_issue_keys_from_csv(file_path)`: This function reads issue keys from
  the specified CSV file and returns a list of issue keys.
2. `post_issue_keys(issue_keys)`: This function sends a POST request to the
  Jira API with the provided list of issue keys as the payload. It prints a
  success or failure message based on the API response.

In the main logic, the script does the following:
1. Calls `read_issue_keys_from_csv` to get a list of issue keys from the CSV
  file.
2. If the list of issue keys is not empty, it calls `post_issue_keys` with the
  issue keys as the argument.
3. If the list of issue keys is empty, it prints a message indicating that no
  issue keys were found in the CSV.

This script should be executed when you need to reconstruct the SLA for a set
of Jira Service Desk issues. Make sure to provide the correct environment
variables (Jira URL, user email, and API token) in the `.env` file before
running the script.
"""
import csv
import os
import requests
from requests.auth import HTTPBasicAuth
from concurrent.futures import ThreadPoolExecutor, as_completed

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
CSV_FILE_PATH = 'issues.csv'
url = f'{JIRA_URL}/rest/servicedesk/1/servicedesk/sla/admin/task/destructive/reconstruct?force=true'
auth = HTTPBasicAuth(USER_EMAIL, API_TOKEN)
CONTENT_TYPE = 'application/json'
MAX_WORKERS = 50

def post_issue_key(issue_key):
    """
    Sends a POST request for a single issue key.

    Args:
       issue_key (str): The issue key to be included in the payload.
    """
    headers = {
        'Content-Type': CONTENT_TYPE,
    }
    payload = [issue_key]
    response = requests.post(url, json=payload, headers=headers, auth=auth, timeout=30)
    if response.ok:
        print(f'Request successful for issue key {issue_key}:', response.text)
    else:
        print(f'Request failed for issue key {issue_key} with status code:', response.status_code, 'and reason:', response.text)
    # Print the response text regardless of success or failure
    print(f'Response for issue key {issue_key}:', response.text)

def read_issue_keys_from_csv(file_path):
    """
    Reads issue keys from a CSV file.

    Args:
        file_path (str): Path to the CSV file containing issue keys.

    Returns:
        list: A list of issue keys extracted from the CSV file. The list will be empty if the CSV file is empty or contains no 'issue_key' column.
    """
    issue_keys = []
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            issue_keys.append(row['issue_key'])
    return issue_keys

# Main logic
if __name__ == '__main__':
    issue_keys_from_file = read_issue_keys_from_csv(CSV_FILE_PATH)
    if issue_keys_from_file:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [executor.submit(post_issue_key, issue_key) for issue_key in issue_keys_from_file]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as exc:
                    print(f'Generated an exception: {exc}')
    else:
        print('No issue keys found in the CSV.')
