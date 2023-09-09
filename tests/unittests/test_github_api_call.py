"""
Python notebook source
-------------------------------------------------------------------------
Copyright (c) 2023 NHS Python Community. All rights reserved.
Licensed under the MIT License. See license.txt in the project root for
license information.
-------------------------------------------------------------------------

FILE:           test_github_api_call.py
DESCRIPTION:    pytest of query GitHub API functions

CONTRIBUTORS:   Craig R. Shenton
CONTACT:        craig.shenton@nhs.net
CREATED:        10 May 2023
VERSION:        0.2.0

To run this test requires the following step:
        1) Open terminal and set the directory to the project folder
        2) Enter:
            >pytest 
        and run

-------------------------------------------------------------------------
"""
import time
import logging
import pytest
import responses
import requests
import pandas as pd
from pandas.testing import assert_frame_equal

from src.ingestion.github_api_call import fetch_public_repos, parse_github_repos, query_org_repos

@responses.activate
def test_fetch_public_repos():
    test_url = "https://api.github.com/orgs/test_org/repos"
    test_response = [{"id": 1, "private": False, "fork": False}]
    responses.add(responses.GET, test_url, json=test_response, status=200)

    result = fetch_public_repos("test_org")
    assert result == test_response

@responses.activate
def test_fetch_public_repos_http_error():
    test_url = "https://api.github.com/orgs/test_org/repos"
    responses.add(responses.GET, test_url, status=403)

    with pytest.raises(requests.exceptions.HTTPError):
        fetch_public_repos("test_org")

def test_parse_github_repos():
    raw_data = [{"id": 1, "private": False, "fork": False, "name": "repo1"}, {"id": 2, "private": True, "fork": False, "name": "repo2"}]
    expected_output = pd.json_normalize([{"id": 1, "private": False, "fork": False, "name": "repo1"}])

    result = parse_github_repos(raw_data)
    assert_frame_equal(result, expected_output)

@responses.activate
def test_query_org_repos():
    test_org_dict = {"org1": "test_org1", "org2": "test_org2"}
    test_url1 = "https://api.github.com/orgs/test_org1/repos"
    test_url2 = "https://api.github.com/orgs/test_org2/repos"
    test_response1 = [{"id": 1, "private": False, "fork": False, "name": "repo1"}]
    test_response2 = [{"id": 2, "private": False, "fork": False, "name": "repo2"}]
    responses.add(responses.GET, test_url1, json=test_response1, status=200)
    responses.add(responses.GET, test_url2, json=test_response2, status=200)

    result = query_org_repos(test_org_dict)
    expected_output = pd.concat([pd.json_normalize(test_response1), pd.json_normalize(test_response2)], axis=0)

    assert_frame_equal(result, expected_output)

@responses.activate
def test_fetch_public_repos_rate_limit_handling(caplog):
    caplog.set_level(logging.INFO)

    test_url = "https://api.github.com/orgs/test_org/repos"
    rate_limit_reset = int(time.time()) + 1
    responses.add(
        responses.GET,
        test_url,
        status=403,
        headers={
            "X-RateLimit-Reset": str(rate_limit_reset)
        }
    )
    responses.add(responses.GET, test_url, json=[{"id": 1}], status=200)

    result = fetch_public_repos("test_org")
    assert result == [{"id": 1}]
    
    assert "Rate limit exceeded" in caplog.text
    assert "Waiting 1 seconds until rate limit is reset" in caplog.text

@responses.activate
def test_query_org_repos_rate_limit_handling_and_retry_logic(caplog):
    caplog.set_level(logging.INFO)

    test_org_dict = {"org1": "test_org1"}
    test_url1 = "https://api.github.com/orgs/test_org1/repos"
    rate_limit_reset = int(time.time()) + 1
    responses.add(
        responses.GET,
        test_url1,
        status=403,
        headers={
            "X-RateLimit-Reset": str(rate_limit_reset)
        }
    )
    responses.add(responses.GET, test_url1, json=[{"id": 1}], status=200)

    result = query_org_repos(test_org_dict)
    expected_output = pd.json_normalize([{"id": 1}])

    pd.testing.assert_frame_equal(result, expected_output)
    assert "Rate limit exceeded for organisation test_org1" in caplog.text
    assert "Waiting 1 seconds until rate limit is reset" in caplog.text
    assert "Max retries exceeded for organisation" not in caplog.text

@responses.activate
def test_query_org_repos_error_handling(caplog):
    caplog.set_level(logging.INFO)

    test_org_dict = {"org1": "test_org1"}
    test_url1 = "https://api.github.com/orgs/test_org1/repos"
    responses.add(responses.GET, test_url1, status=500)

    with pytest.raises(requests.exceptions.HTTPError):
        result = query_org_repos(test_org_dict)

    assert "Error fetching data for test_org1" in caplog.text
