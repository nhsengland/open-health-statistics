"""
Purpose of the script:  to provide a starting point for the basis of your pipeline using example data from SQL server

The script loads Python packages but also internal modules (e.g. modules.helpers, helpers script from the modules folder).
It then loads various configuration variables and a logger, for more info on this find the RAP Community of Practice Repo on Github

Then, we call some basic SQL functions to load in our data, process it and write our outputs to an appropriate file type (e.g. CSV, Excel)
For more info on automated excel outputs, find the automated-excel-publications repo on Gitlab.
"""

# this part imports our Python packages, including our project's modules
import logging
import timeit 
from pathlib import Path
from src.utils.data_connections import read_sql_file, get_df_from_server, make_database_connection
from src.utils.file_paths import get_config
from src.utils.logging_config import configure_logging 
from src.processing.clean import calculate_years, process_columns
from src.processing.derive_fields import gp_count_by_region, calculate_mean_years

logger = logging.getLogger(__name__)

def main():
    
    # load config, here we load our project's parameters from the config.toml file
    config = get_config("config.toml") 
    server = config ['server']
    database = config['database']
    schema = config['schema']
    table = config['table']
    filled_value = config['filled_value']
    output_dir = Path(config['output_dir'])
    log_dir = Path(config['log_dir'])

    # configure logging
    configure_logging(log_dir, config)
    logger.info(f"Configured logging with log folder: {log_dir}.")

    # sets up database connection
    conn = make_database_connection(server, database)

    # load data, this part handles importing our data sources     
    query = read_sql_file('sql', 'example.sql', database, schema, table)
    gp_df = get_df_from_server(conn, server, database, query)

    # follow pre-processing steps  
    gp_df.rename(columns={'ADDRESS_LINE_5': 'REGION', 
                       'OPEN_DATE': 'OPENED', 
                       'CLOSE_DATE': 'CLOSED'}, inplace=True)
    
    gp_df = process_columns(gp_df, 
        date_col_names = ['OPENED', 'CLOSED'], 
        string_col_names= ['REGION', 'NAME']
        )

    gp_df = calculate_years(filled_value, gp_df)
        
    # prepare data for CSV
    publication_breakdowns = {}
    publication_breakdowns['gp_data'] = gp_df

    # follow data processing steps
    region_df = gp_count_by_region(gp_df)
    region_df = calculate_mean_years(region_df, gp_df)

    publication_breakdowns['region_data'] = region_df

    # produce outputs
    for table_name, df in publication_breakdowns.items():
        df.to_csv(output_dir / f'{table_name}.csv', index=False)
        logger.info('\n\n%s.csv created!\n', table_name)
    logger.info(f"Produced output(s) in folder: {output_dir}.")
    
if __name__ == "__main__":
    print(f"Running create_publication script")
    start_time = timeit.default_timer()
    main()
    total_time = timeit.default_timer() - start_time
    print(f"Running time of create_publication script: {int(total_time / 60)} minutes and {round(total_time%60)} seconds.\n")
