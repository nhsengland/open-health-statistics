"""
Python notebook source
-------------------------------------------------------------------------
Copyright (c) 2023 NHS Python Community. All rights reserved.
Licensed under the MIT License. See license.txt in the project root for
license information.
-------------------------------------------------------------------------

FILE:           github_api_call.py
DESCRIPTION:    Query GitHub API

CONTRIBUTORS:   Craig R. Shenton
CONTACT:        craig.shenton@nhs.net
CREATED:        10 May 2023
VERSION:        0.2.0

-------------------------------------------------------------------------
"""
import requests
import time
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def fetch_public_repos(org_name: str, page: int = 1, results_per_page: int = 100) -> dict:
    """
    Fetches public GitHub repositories for a given organisation and returns the raw JSON data.

    Args:
        org_name (str): The name of the GitHub organisation to fetch repositories for.
        page (int, optional): The page of results to fetch. Defaults to 1.
        results_per_page (int, optional): The number of results to fetch per page. Defaults to 100.

    Returns:
        dict: A dictionary containing the JSON data returned by the GitHub API.
    """
    url = f"https://api.github.com/orgs/{org_name}/repos"
    headers = {"Accept": "application/vnd.github.v3+json"}
    params = {"page": page, "per_page": results_per_page}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    return response.json()

def parse_github_repos(raw_data: pd.DataFrame) -> pd.DataFrame:
    """
    Parses raw GitHub repository JSON data into a Pandas DataFrame.

    Args:
        raw_data (dict): A dictionary containing the raw JSON data returned by the GitHub API.

    Returns:
        pd.DataFrame: A Pandas DataFrame containing repository information.
    """
    data = [repo for repo in raw_data if not repo["private"]]
    data = [repo for repo in data if not repo["fork"]]
    return pd.json_normalize(data)

def query_org_repos(github_org_dict: dict, max_retries: int = 3) -> pd.DataFrame:
    """
    Pulls raw GitHub repository data for multiple organisations and returns a consolidated DataFrame.

    Args:
        github_org_dict (dict): A dictionary containing GitHub organisations to fetch repositories for.
            Values should be organisation names.
        max_retries (int, optional): The maximum number of times to retry the API request if a rate limit is encountered.
            Defaults to 3.

    Returns:
        pd.DataFrame: A Pandas DataFrame containing information about repositories for all specified organisations.
    """
    df = pd.DataFrame()

    for org in github_org_dict.values():
        page = 1
        retries = 0
        while True:
            try:
                raw_data = fetch_public_repos(org, page=page)
                repos_count = len(raw_data)
                logger.info(f"{org} repo count = {repos_count}")

                if repos_count == 0:
                    break

                parsed_data = parse_github_repos(raw_data)
                df = pd.concat([df, parsed_data], axis=0)

                # check if there are more pages
                if repos_count < 100:
                    break
                else:
                    page += 1

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403:
                    logger.info(f"Rate limit exceeded for organisation {org}.")
                    if retries >= max_retries:
                        logger.info(f"Max retries exceeded for organisation {org}. Moving on.")
                        break
                    reset_time = int(e.response.headers.get("X-RateLimit-Reset"))
                    wait_time = reset_time - time.time() + 1
                    logger.info(f"Waiting {wait_time} seconds until rate limit is reset.")
                    time.sleep(wait_time)
                    retries += 1
                else:
                    print(f"Error fetching data for {org}: {e}")
                    break

    return df