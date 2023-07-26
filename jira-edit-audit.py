"""This script exports the audit logs for the last 30 days to a CSV file."""
import csv
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import json
import os
import queue
import requests

# Check if the .env var exists and load the environment variables
env_path = os.path.join(os.path.dirname(__file__), '.', '.env')
if os.path.exists(env_path):
    with open(env_path, encoding="utf-8") as file:
        for line in file:
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

# Set the necessary parameters
ORG_ID = os.environ.get('ORG_ID')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
BASE_URL = "https://api.atlassian.com/admin/v1/orgs"

# Set the date range for the last 30 days
to_date = int(datetime.now().timestamp()) * 1000
from_date = int((datetime.now() - timedelta(days=30)).timestamp()) * 1000

# Ask user for the action type
print("Please select the action type:")
print("1. jira_issue_viewed")
print("2. jira_issue_updated")
action_choice = input("Enter your choice (1 or 2): ")

# Set the ACTION based on user's choice
if action_choice == "1":
    ACTION = "jira_issue_viewed"
elif action_choice == "2":
    ACTION = "jira_issue_updated"
else:
    print("Invalid choice. Defaulting to jira_issue_updated")
    ACTION = "jira_issue_updated"

# API endpoint URL
url = f"{BASE_URL}/{ORG_ID}/events"

headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

# Initialize an empty list to store the audit log events
audit_logs = []

# Thread safe queue to store page URLs
pages_queue = queue.Queue()
pages_queue.put(url)


def fetch_page(page_url):
    """Function to fetch the audit log events for a given page URL"""
    response = requests.get(page_url, headers=headers,
                            params={"from": from_date, "to": to_date,
                                    "action": ACTION}, timeout=30)
    print(json.dumps(json.loads(response.text), sort_keys=True, indent=4,
          separators=(",", ": ")))
    if response.status_code == 200:
        data = response.json()
        audit_logs.extend(data["data"])
        # Check if there's a next page and update the URL
        next_page = data["links"].get("next")
        if next_page:
            pages_queue.put(next_page)
    else:
        print(f"Error retrieving audit log events: {response.status_code}")


# Start thread pool executor with 10 threads
with ThreadPoolExecutor(max_workers=160) as executor:
    futures = {executor.submit(fetch_page, pages_queue.get())}
    while futures:
        done, futures = (
                concurrent.futures.wait(
                    futures, return_when=concurrent.futures.FIRST_COMPLETED
                    )
                )

        for future in done:
            # Here you can add error handling on exception
            if future.exception() is not None:
                print(f"Error retrieving audit log events: \
                        {future.exception()}")
            else:
                print("Page processed successfully")
        while not pages_queue.empty():
            futures.add(executor.submit(fetch_page, pages_queue.get()))

# Export the audit log events to a CSV file
OUTPUT_FILE = "audit_logs.csv"

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Time", "Action", "Actor Name", "Actor Email",
                     "Issue Key"])

    for log in audit_logs:
        attributes = log["attributes"]
        time = attributes["time"]
        action = attributes["action"]
        actor_name = attributes["actor"]["name"]
        actor_email = attributes["actor"]["email"]
        # assuming that attributes["container"] is a list of dictionaries
        for container in attributes["container"]:
            issue_key = container["attributes"]["issueKeyOrId"]
            writer.writerow([time, action, actor_name, actor_email, issue_key])

print(f"Audit logs exported to {OUTPUT_FILE}")
