"""This script will export all projects from your Jira Cloud instance. """
import csv
import os
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

auth = HTTPBasicAuth(USER_EMAIL, API_TOKEN)

headers = {"Accept": "application/json"}

# Get all projects
response = requests.get(
    f"{JIRA_URL}/rest/api/3/project", headers=headers, auth=auth, timeout=30
)

# Parse the response as JSON
projects = response.json()

# Create or open a CSV file named 'jira_projects.csv' in write mode
with open("jira_projects.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    # Write the headers
    writer.writerow(
        ["Project ID", "Project Key", "Project Name", "Project Type"]
    )
    # Go through each project
    for project in projects:
        # Write project data to the CSV file
        writer.writerow(
            [
                project["id"],
                project["key"],
                project["name"],
                project["projectTypeKey"],
            ]
        )
