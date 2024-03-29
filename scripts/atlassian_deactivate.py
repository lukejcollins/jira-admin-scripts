"""
This script reads user account IDs from a CSV file and deletes the
corresponding Atlassian user accounts from an organization.

The script first checks for the presence of an ".env" file in the same
directory as the script. If the file exists, it reads the environment
variables from the file and stores them in the `os.environ` dictionary. The
environment variables should contain the access token and organization ID
required for authentication and API calls.

The script defines two functions:

1. `delete_atlassian_user(account_id)`:
   This function deletes an Atlassian user account with the given `account_id`
   from the specified organization. It makes a DELETE request to the Atlassian
   API and prints a success or failure message based on the response.

2. `process_users_csv(file_path)`:
   This function reads user account IDs from the specified CSV file and calls
   the `delete_atlassian_user` function for each account ID. The CSV file
   should have a column named "atlassian account id" containing the account
   IDs.

Finally, the script calls the `process_users_csv` function with the path to
the CSV file containing the user account IDs to be deleted.

Note: Make sure to replace the placeholders for the access token and
organization ID in the ".env" file with your actual values before running the
script.
"""

import csv
import os
import requests

# Check if the .env var exists and load the environment variables
env_path = os.path.join(os.path.dirname(__file__), ".", ".env")
if os.path.exists(env_path):
    with open(env_path, encoding="utf-8") as file:
        for line in file:
            key, value = line.strip().split("=", 1)
            os.environ[key] = value

# Replace these placeholders with your actual values
access_token = os.environ.get("ACCESS_TOKEN")
org_id = os.environ.get("ORG_ID")


def delete_atlassian_user(account_id):
    """
    Deletes an Atlassian user account with the given `account_id` from the
    specified organization.

    Args:
        account_id (str): The ID of the Atlassian account to delete.
    """
    url = f"https://api.atlassian.com/admin/v1/orgs/{org_id}/directory/" \
          f"users/{account_id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.request("DELETE", url, headers=headers, timeout=30)

    # Check if the request was successful
    if response.status_code == 204:
        print(f"Successfully deleted user {account_id}")
    else:
        print(f"Failed to delete user {account_id}. Status code: "
              f"{response.status_code}, Response: {response.text}")


def process_users_csv(file_path):
    """
    Reads user account IDs from the specified CSV file and calls the
    `delete_atlassian_user` function for each account ID.

    Args:
        file_path (str): The path to the CSV file containing user account IDs.
    """
    with open(file_path, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            account_id = row['atlassian account id']
            delete_atlassian_user(account_id)


# Specify the path to your CSV file
CSV_FILE_PATH = 'accounts.csv'
process_users_csv(CSV_FILE_PATH)
