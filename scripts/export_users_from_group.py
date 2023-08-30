"""Module to export users from a specified Jira group to a CSV file."""
import csv
import os
import sys
import requests
from requests.auth import HTTPBasicAuth

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
EXPORT_GROUP_NAME = os.environ.get("EXPORT_GROUP_NAME")

auth = HTTPBasicAuth(USER_EMAIL, API_TOKEN)
headers = {"Accept": "application/json"}

# Get all users from the group
url = f"{JIRA_URL}/rest/api/3/group/member"
query = {"groupname": EXPORT_GROUP_NAME, "startAt": 0, "maxResults": 50}

response = requests.get(
    url, headers=headers, params=query, auth=auth, timeout=30
)

# Check the HTTP status code
if response.status_code != 200:
    print(f"Failed to fetch data. HTTP Status Code: {response.status_code}")
    print(response.text)
    sys.exit()

# Parse the response as JSON
group_data = response.json()

users = group_data.get("values", [])

# If users are empty, exit early
if not users:
    print("No users found for the provided group.")
    sys.exit()

# If there are more pages, handle pagination
all_users = users
while group_data.get("isLast", False) is False:
    query["startAt"] += query["maxResults"]
    response = requests.get(
        url, headers=headers, params=query, auth=auth, timeout=30
    )
    group_data = response.json()
    all_users.extend(group_data.get("values", []))

# Create or open a CSV file named 'jira_users_from_group.csv' in write mode
with open(
    "jira_users_from_group.csv", "w", newline="", encoding="utf-8"
) as file:
    writer = csv.writer(file)
    # Write the headers
    writer.writerow(
        [
            "Account ID",
            "User Display Name",
            "User Email Address",
            "Active Status",
        ]
    )
    # Go through each user
    for user in all_users:
        # Write user data to the CSV file
        writer.writerow(
            [
                user["accountId"],
                user["displayName"],
                user.get("emailAddress", "N/A"),
                user["active"],
            ]
        )
