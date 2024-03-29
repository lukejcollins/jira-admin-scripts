![Jira](https://img.shields.io/badge/Jira-Service%20Management-blue?style=flat&logo=Jira&logoColor=blue) ![Jira](https://img.shields.io/badge/Jira-Software-blue?style=flat&logo=Jira%20Software&logoColor=blue) ![Python](https://img.shields.io/badge/Python-Scripts-blue?style=flat&logo=python&logoColor=yellow) ![Python Lint](https://github.com/lukejcollins/jira-admin-scripts/actions/workflows/linting.yaml/badge.svg)

# Jira Administration Scripts

This repository contains a collection of Python scripts for various administrative tasks related to Jira. They interact with the Atlassian REST API to fetch and export data into CSV files or display it in the console. These scripts are multi-threaded where applicable, using Python ThreadPoolExecutor to fetch multiple pages of data concurrently from the API.

## Scripts

1. ```jira_edit_audit.py```: Fetches audit logs for the last 30 days from an Atlassian organisation and exports them into a CSV file.
2. ```jira_action_audit_list.py```: Lists all the audit actions for a specific organization.
3. ```project_export.py```: Exports all projects from your Jira Cloud instance into a CSV file.
4. ```jira_service_management_audit.py```: Fetches the changelogs of issues from a JIRA Service Management project that have been updated within the last 30 days and exports them to a CSV file.
5. ```atlassian_access_deactivate.py```: This script reads a CSV containing Atlassian account IDs and uses the Atlassian API to remove those user's access from the specified organization.
6. ```remove_users_from_group.py```: This script reads a CSV file containing usernames and removes these users from a specified Jira group.
7. ```export_users_from_group.py```: This script takes a Jira group name and exports all the users from that group to a CSV.
8. ```atlassian_deactivate.py```: This script reads a CSV containing Atlassian account IDs and uses the Atlassian API to deactivate those users from the Atlassian directory.
9. ```force_sla_reconstruction.py```: This script reads a CSV containing Jira issue IDs and uses the Jira API to force SLA re-construction on those issues.

## Requirements

- Python 3.6+
- `requests` library

## Setup

1. Clone this repository:
    ```bash
    git clone https://github.com/lukejcollins/jira-scripts.git
    ```
2. Go into the cloned directory:
    ```bash
    cd jira-scripts
    ```
3. Ensure that the necessary environment variables are defined in your system. These are:

    - `ORG_ID`: The organization ID of your Atlassian organisation.
    - `ACCESS_TOKEN`: The API access token.
    - `JIRA_URL`: Your Jira domain URL. For example, `https://your-domain.atlassian.net`.
    - `USER_EMAIL`: The email address of your Jira account.
    - `API_TOKEN`: The API token for your Jira account.
    - `REMOVAL_GROUP_NAME`: The name of the Jira group you wish to remove users from.
    - `EXPORT_GROUP_NAME`: The name of the Jira group you wish to export users from.

## Usage

Run the script you wish to use:
```bash
python script_name.py
```
Replace `script_name.py` with the name of the script you wish to run. 

## Note

Please be aware that these scripts are dependent on Atlassian's APIs, so any changes they make could impact the functionality of these scripts. Ensure your API credentials are valid and have the necessary permissions to fetch the respective data.

## Contributing

Feel free to create an issue or make a pull request if you find any bugs or have some suggestions to improve these scripts.

## Show your support

Give a ⭐️ if this project helped you!
