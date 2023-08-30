""" This script will list all the audit actions for an organization. """
import os
import csv
import requests


# Load environment variables from the .env file if it exists
def load_env_vars(env_path):
    """
    Loads environment variables from a .env file if it exists.
    """
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as file:
            for line in file:
                key, value = line.strip().split("=", 1)
                os.environ[key] = value


load_env_vars(os.path.join(os.path.dirname(__file__), ".env"))

ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")


def remove_user_access(account_id, access_token):
    """
    Removes a user's access using the Atlassian API.
    """
    url = (
        f"https://api.atlassian.com/users/{account_id}/manage/lifecycle/"
        f"delete"
    )

    headers = {"Authorization": f"Bearer {access_token}",
               "Content-Type": "application/json"}

    response = requests.post(url, headers=headers, timeout=30)

    return response.status_code, response.text


def main():
    """
    Main function that will read the CSV file and call the remove_user_access
    function.
    """
    with open("accounts.csv", "r", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            account_id = row["atlassian account id"]
            status_code, response_text = remove_user_access(
                account_id, ACCESS_TOKEN
            )

            # Print the status and response for each request
            print(
                f"Account ID: {account_id}, Status Code: {status_code},"
                f"Response: {response_text}"
            )


if __name__ == "__main__":
    main()
