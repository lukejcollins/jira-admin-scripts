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
    url = f"https://api.atlassian.com/admin/v1/orgs/{org_id}/directory/users/{account_id}"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.request("DELETE", url, headers=headers)
    
    # Check if the request was successful
    if response.status_code == 204:
        print(f"Successfully deleted user {account_id}")
    else:
        print(f"Failed to delete user {account_id}. Status code: {response.status_code}, Response: {response.text}")

def process_users_csv(file_path):
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            account_id = row['atlassian account id']
            delete_atlassian_user(account_id)

# Specify the path to your CSV file
csv_file_path = 'accounts.csv'
process_users_csv(csv_file_path)
