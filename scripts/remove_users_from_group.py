"""
Jira Cloud REST API example using Python 3 demonstrating how to remove users
from a Jira group using a CSV file containing email addresses.
"""

import csv
from concurrent.futures import ThreadPoolExecutor
import logging
import os
import requests
from requests.auth import HTTPBasicAuth

logging.basicConfig(level=logging.INFO)


def load_env_vars(env_path):
    """
    Loads environment variables from a .env file if it exists.
    """
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as file:
            for line in file:
                key, value = line.strip().split("=", 1)
                os.environ[key] = value
                logging.debug("Loaded environment variable: %s", key)


load_env_vars(os.path.join(os.path.dirname(__file__), ".env"))

JIRA_URL = os.environ.get("JIRA_URL")
API_TOKEN = os.environ.get("API_TOKEN")
USER_EMAIL = os.environ.get("USER_EMAIL")
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}
AUTH = HTTPBasicAuth(USER_EMAIL, API_TOKEN)
GROUP_NAME = os.environ.get("GROUP_NAME")
CSV_FILE = "users.csv"
NUM_WORKERS = 10


def get_account_id(email):
    """
    Fetches the account ID for the given email address.
    """
    logging.debug("Fetching account ID for email: %s", email)

    endpoint = f"{JIRA_URL}/rest/api/3/user/search"
    params = {"query": email}

    response = requests.get(
        endpoint, headers=HEADERS, params=params, auth=AUTH, timeout=30
    )

    if response.status_code != 200:
        logging.error(
            "Failed to fetch user info for email: %s. Status Code: %s, "
            "Response: %s",
            email,
            response.status_code,
            response.text,
        )
        return None

    try:
        users = response.json()
        if not users:  # No user found matching the email
            return None
        user = users[0]
    except (ValueError, IndexError):
        logging.error("Failed to parse JSON response or user not found.")
        return None

    # Extract account ID based on the response structure
    account_id = user.get("accountId")

    logging.info("Found account ID %s for email %s", account_id, email)
    return account_id


def remove_user_from_group(account_id):
    """
    Removes a user from a Jira group.
    """
    logging.debug(
        "Trying to remove account %s from group %s", account_id, GROUP_NAME
    )
    endpoint = (
        f"{JIRA_URL}/rest/api/3/group/user?groupname={GROUP_NAME}&"
        f"accountId={account_id}"
    )
    response = requests.delete(
        endpoint, headers=HEADERS, auth=AUTH, timeout=30
    )
    if response.status_code == 200:
        logging.info(
            "Successfully removed user %s from group %s.",
            account_id,
            GROUP_NAME,
        )
    else:
        logging.error(
            "Failed to remove user %s from group %s. Response: %s, Status: %s",
            account_id,
            GROUP_NAME,
            response.text,
            response.status_code
        )


def main():
    """
    Main function.
    """
    logging.info("Starting the script")
    emails = []

    logging.info("Reading emails from %s", CSV_FILE)
    with open(CSV_FILE, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file)
        emails = [row[0] for row in reader]
    logging.info("Loaded %s emails from %s", len(emails), CSV_FILE)

    with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        logging.info("Fetching account IDs from emails")
        account_ids = list(executor.map(get_account_id, emails))

        logging.info("Removing users from Jira group")
        list(executor.map(remove_user_from_group, account_ids))
    logging.info("Script finished successfully")


if __name__ == "__main__":
    main()
