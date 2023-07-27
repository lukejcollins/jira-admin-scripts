![Jira](https://img.shields.io/badge/Jira-Service%20Management-blue?style=flat&logo=Jira&logoColor=blue) ![Jira](https://img.shields.io/badge/Jira-Software-blue?style=flat&logo=Jira%20Software&logoColor=blue) ![Python](https://img.shields.io/badge/Python-Scripts-blue?style=flat&logo=python&logoColor=yellow)

# Jira Administration Scripts

This repository contains a collection of Python scripts for various administrative tasks related to Jira. They interact with the Atlassian REST API to fetch and export data into CSV files or display it in the console. These scripts are multi-threaded where applicable, using Python ThreadPoolExecutor to fetch multiple pages of data concurrently from the API.

## Scripts

1. **Jira Audit Log Exporter:** Fetches audit logs for the last 30 days from an Atlassian organisation and exports them into a CSV file.
2. **Jira Audit Actions Listing:** Lists all the audit actions for a specific organization.
3. **Jira Cloud Projects Exporter:** Exports all projects from your Jira Cloud instance into a CSV file.
4. **Jira Service Management Changelog Exporter:** Fetches the changelogs of issues from a JIRA Service Management project that have been updated within the last 30 days and exports them to a CSV file.

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
    - `JIRA_DOMAIN`: Your Jira domain URL. For example, `https://your-domain.atlassian.net`.
    - `JIRA_EMAIL`: The email address of your Jira account.
    - `JIRA_TOKEN`: The API token for your Jira account.

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
