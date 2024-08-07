"""
This module exports managed accounts data from the Atlassian API to a CSV file.
It includes functions to fetch data from the API, process accounts, and write
the data to a CSV file.
"""

import csv
import os
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from queue import Queue
from typing import Any, Dict, Optional, Set, Tuple
from urllib.parse import parse_qs, urlparse

import requests
from ratelimit import limits, sleep_and_retry  # type: ignore
from unidecode import unidecode

# Check if the .env var exists and load the environment variables
env_path = os.path.join(os.path.dirname(__file__), ".", ".env")
if os.path.exists(env_path):
    with open(env_path, encoding="utf-8") as file:
        for line in file:
            key, value = line.strip().split("=", 1)
            os.environ[key] = value

# Usage example
ORG_ID = os.environ.get("ORG_ID")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
JIRA_URL_WITHOUT_HTTPS = os.environ.get("JIRA_URL_WITHOUT_HTTPS")
OUTPUT_FILE = "managed_accounts.csv"
MAX_WORKERS = 5


# Rate limit decorator
@sleep_and_retry
@limits(calls=500, period=300)  # 500 calls per 300 seconds (5 minutes)
def make_request(
    url: str, headers: Dict[str, str], params: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Make a GET request to the given URL with the provided headers and
    parameters."""
    response = requests.get(url, headers=headers, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def writer_worker(output_file: str, queue: Queue) -> None:
    """Worker function to write rows to a CSV file."""
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "account_id",
            "account_type",
            "account_status",
            "name",
            "email",
            "access_billable",
            "last_active",
            "product_access_key",
            "product_access_name",
            "product_url",
            "product_access_last_active",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        while True:
            row = queue.get()
            if row is None:
                break
            writer.writerow(row)
            queue.task_done()


def process_account(account, queue, seen_combinations, jira_url_without_https):
    """Process an individual account and add valid rows to the queue."""
    if account.get("account_status") != "active":
        print(f"Skipping inactive account: {account}")
        return

    print(f"Processing active account: {account}")
    for product in account["product_access"]:
        print(f"Processing product: {product}")
        product_url = unidecode(product.get("url", ""))
        if product_url != jira_url_without_https:
            print(f"Skipping product URL: {product_url}")
            continue

        combination = (account["account_id"], product["key"])
        if combination in seen_combinations:
            print(f"Skipping duplicate combination: {combination}")
            continue
        seen_combinations.add(combination)

        row = {
            "account_id": unidecode(account.get("account_id", "")),
            "account_type": unidecode(account.get("account_type", "")),
            "account_status": unidecode(account.get("account_status", "")),
            "name": unidecode(account.get("name", "")),
            "email": unidecode(account.get("email", "")),
            "access_billable": account.get("access_billable", ""),
            "last_active": unidecode(account.get("last_active", "")),
            "product_access_key": unidecode(product.get("key", "")),
            "product_access_name": unidecode(product.get("name", "")),
            "product_url": product_url,
            "product_access_last_active": unidecode(product.get("last_active", "")),
        }

        add_row_to_queue(queue, row)


def add_row_to_queue(queue, row):
    """Add a row to the queue, handling duplicates and comparing dates."""
    existing_row = next(
        (
            r
            for r in queue.queue
            if r["account_id"] == row["account_id"]
            and r["product_access_key"] == row["product_access_key"]
        ),
        None,
    )
    if existing_row:
        if (
            row["product_access_last_active"]
            and existing_row["product_access_last_active"]
        ):
            row_date = datetime.strptime(
                row["product_access_last_active"], "%Y-%m-%dT%H:%M:%S.%fZ"
            )
            existing_date = datetime.strptime(
                existing_row["product_access_last_active"], "%Y-%m-%dT%H:%M:%S.%fZ"
            )
            if row_date > existing_date:
                queue.queue.remove(existing_row)
                queue.put(row)
        else:
            if random.random() < 0.5:
                queue.queue.remove(existing_row)
                queue.put(row)
    else:
        queue.put(row)


def fetch_page_data(url, headers, cursor):
    """Fetch a page of data from the API."""
    params = {"cursor": cursor} if cursor else None
    response_data = make_request(url, headers, params)
    if not isinstance(response_data, dict):
        raise ValueError("Expected response_data to be a dictionary")
    return response_data


def process_response_data(
    response_data, executor, queue, seen_combinations, jira_url_without_https
):
    """Process the response data and submit tasks to the executor."""
    futures = []
    for account in response_data["data"]:
        futures.append(
            executor.submit(
                process_account,
                account,
                queue,
                seen_combinations,
                jira_url_without_https,
            )
        )
    return futures


def update_cursor(response_data):
    """Update the cursor for pagination."""
    if "next" not in response_data["links"]:
        return None
    next_url = response_data["links"]["next"]
    parsed_url = urlparse(next_url)
    return parse_qs(parsed_url.query)["cursor"][0]


def get_managed_accounts(
    org_id: str, access_token: str, output_file: str, max_workers: int = 5
) -> None:
    """Fetch managed accounts from Atlassian API and write to a CSV file."""
    if not org_id or not access_token or not output_file:
        raise ValueError(
            "org_id, access_token, output_file must be provided and not None."
        )

    url = f"https://api.atlassian.com/admin/v1/orgs/{org_id}/users"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {access_token}"}

    queue: Queue = Queue()
    writer_thread = threading.Thread(target=writer_worker, args=(output_file, queue))
    writer_thread.start()

    cursor = None
    page_count = 1
    # Track seen account_id and product_access_key combinations
    seen_combinations: Set[Tuple[str, str]] = set()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        while True:
            print(f"Fetching page {page_count}...")
            response_data = fetch_page_data(url, headers, cursor)

            if "data" not in response_data:
                print("No more data found. Exiting.")
                break

            futures = process_response_data(
                response_data,
                executor,
                queue,
                seen_combinations,
                JIRA_URL_WITHOUT_HTTPS,
            )

            # Wait for all the processing tasks to complete
            for future in as_completed(futures):
                future.result()

            cursor = update_cursor(response_data)
            if cursor is None:
                print("Reached the end of the pages.")
                break

            page_count += 1

    # Signal the writer thread to stop
    queue.put(None)
    writer_thread.join()

    print(f"Data exported to {output_file} successfully.")


if ORG_ID and ACCESS_TOKEN and OUTPUT_FILE:
    get_managed_accounts(ORG_ID, ACCESS_TOKEN, OUTPUT_FILE, MAX_WORKERS)
else:
    print("Please provide valid ORG_ID, ACCESS_TOKEN, and OUTPUT_FILE.")
