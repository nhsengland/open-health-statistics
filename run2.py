"""
Python notebook source
-------------------------------------------------------------------------
Copyright (c) 2023 NHS Python Community. All rights reserved.
Licensed under the MIT License. See license.txt in the project root for
license information.
-------------------------------------------------------------------------

FILE:           run.py
DESCRIPTION:    Process GitHub API data

CONTRIBUTORS:   Craig R. Shenton
CONTACT:        craig.shenton@nhs.net
CREATED:        10 May 2023
VERSION:        0.2.0

-------------------------------------------------------------------------
"""
import pandas as pd
import timeit 
from pathlib import Path
import logging
from src.ingestion.github_api_call import query_org_repos
from src.processing.data_processing import tidy_raw_df, add_missing_values_and_filter
from src.utils.file_paths import get_config
from src.utils.load_yaml import load_yaml
from src.utils.logging_config import configure_logging

logger = logging.getLogger(__name__)

def main():
    # load config, here we load our project's parameters from the config.toml file
    config = get_config("config.toml") 
    raw_sink = Path(config['raw_sink'])
    agg_sink = Path(config['agg_sink'])
    org_list = Path(config['org_list'])
    log_dir = Path(config['log_dir'])

    # configure logging
    configure_logging(log_dir, config)
    logger.info(f"Configured logging with log folder: {log_dir}.")

    # run data pipeline
    yaml_file = load_yaml(org_list)
    raw_github_df = query_org_repos(github_org_dict = yaml_file["github_org_dict"], max_retries=3)
    raw_github_df.to_csv(raw_sink, index=False)
    logger.info(f"Saved raw data in folder: {raw_sink}.")
    #raw_github_df = pd.read_csv(raw_sink) # for testing
    agg_github_df = add_missing_values_and_filter(tidy_raw_df(raw_github_df))
    agg_github_df.to_csv(agg_sink, index=False)
    logger.info(f"Saved aggregate data in folder: {agg_sink}.")

if __name__ == "__main__":
    print("Running processing script")
    start_time = timeit.default_timer()
    main()
    total_time = timeit.default_timer() - start_time
    print(f"Running time of processing script: {int(total_time / 60)} minutes and {round(total_time%60)} seconds.\n")
