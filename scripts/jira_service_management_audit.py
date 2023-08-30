"""Script to fetch issue changelogs from JIRA."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import os
import math
import requests
from requests.auth import HTTPBasicAuth

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(__file__), ".", ".env")
if os.path.exists(env_path):
    with open(env_path, encoding="utf-8") as file:
        for line in file:
            key, value = line.strip().split("=", 1)
            os.environ[key] = value

# Jira details
JIRA_URL = os.environ.get("JIRA_URL")
USER_EMAIL = os.environ.get("USER_EMAIL")
API_TOKEN = os.environ.get("API_TOKEN")

# Define JQL query
JQL_QUERY = "projectType = service_desk and updated >= -30d"

# Define headers
headers = {"Accept": "application/json"}

# Authenticate with JIRA API
auth = HTTPBasicAuth(USER_EMAIL, API_TOKEN)

MAX_THREADS = 10
MAX_RESULTS = 50


def get_issue_keys(start_at):
    """Fetch a page of issue keys starting at start_at."""
    try:
        response = requests.request(
            "GET",
            f"{JIRA_URL}/rest/api/3/search?jql={JQL_QUERY}"
            f"&startAt={start_at * MAX_RESULTS}&maxResults={MAX_RESULTS}",
            headers=headers,
            auth=auth,
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        print(
            f"Added {len(data['issues'])} issue keys, "
            f"total is now {start_at * MAX_RESULTS + len(data['issues'])}"
        )
        return [issue["key"] for issue in data["issues"]]
    except requests.HTTPError as http_err:
        print(f"Failed to get issue keys: {http_err}")
        return []


def get_total_issues():
    """Fetch the total number of issues to be fetched."""
    try:
        response = requests.request(
            "GET",
            f"{JIRA_URL}/rest/api/3/search?jql={JQL_QUERY}&maxResults=1",
            headers=headers,
            auth=auth,
            timeout=120,
        )
        response.raise_for_status()
        return response.json()["total"]
    except requests.HTTPError as http_err:
        print(f"Failed to get total issues: {http_err}")
        return 0


def get_issue_changelog(issue_key):
    """Fetch the changelog for a specific issue."""
    print(f"Fetching changelog for issue {issue_key}...")
    try:
        issue_response = requests.request(
            "GET",
            f"{JIRA_URL}/rest/api/3/issue/{issue_key}?expand=changelog",
            headers=headers,
            auth=auth,
            timeout=120,
        )
        issue_response.raise_for_status()

        issue_data = issue_response.json()
        changelog = issue_data.get("changelog", {})

        if not changelog.get("histories"):
            print(f"No changelog found for issue {issue_key}")
            return []

        return [
            (
                history.get("author", {}).get(
                    "emailAddress", "No email provided"
                ),
                issue_key,
                history["created"],
            )
            for history in changelog["histories"]
        ]
    except requests.HTTPError as http_err:
        print(f"Failed to get changelog for issue {issue_key}: {http_err}")
        return []


def run():
    """Main function to run the script."""
    print("Executing search query...")
    total_issues = get_total_issues()
    issue_keys = []
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = {
            executor.submit(get_issue_keys, start_at): start_at
            for start_at in range(math.ceil(total_issues / MAX_RESULTS))
        }
        for future in as_completed(futures):
            issue_keys += future.result()
    print(f"Collected {len(issue_keys)} issue keys.")

    print("Fetching changelogs...")
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = {
            executor.submit(get_issue_changelog, issue_key): issue_key
            for issue_key in issue_keys
        }
        with open(
            "changelog.csv", "w", newline="", encoding="UTF-8"
        ) as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Actor", "Issue", "Date"])
            for future in as_completed(futures):
                result = future.result()
                for row in result:
                    writer.writerow(row)
    print("Changelogs fetched and written to CSV.")


if __name__ == "__main__":
    run()
