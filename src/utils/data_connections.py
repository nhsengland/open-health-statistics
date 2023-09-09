"""
Purpose of script: handles reading data in and writing data back out.
"""
import sqlalchemy as sa
import os
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def read_sql_file(sql_file_path: str, sql_file_name: str, database, schema, table) -> str:
    """Reads a SQL file and replaces placeholders with given fields.

    Parameters:
        sql_file_name: .sql file name
        database: database name
        table: table name
        schema: schema name
        sql folder: location of sql file (relative to root directory)

    Returns:
        string
    """
    logger.info(f"Reading in SQL script: {sql_file_name} from: {sql_file_path}.")

    with open(os.path.join(sql_file_path, sql_file_name), 'r') as sql_file:
        sql_query = sql_file.read()

    sql_params = {'database': database, 'schema': schema, 'table': table}

    new_sql_query = sql_query.format(**sql_params)

    return new_sql_query

def make_database_connection(server, database):
    """Creates SQL Server connection.
    """
    conn = sa.create_engine(f"mssql+pyodbc://{server}/{database}?driver=SQL+Server&trusted_connection=yes", 
                                fast_executemany=True)
    
    return conn

def get_df_from_server(conn, server, database, query) -> pd.DataFrame:
    """Constructs a pandas DataFrame from running a SQL query on a given SQL server using SQL Alchemy .
       Requires mssql and pyodbc packages.

    Parameters:
        server: server name
        database: database name
        query: string containing a sql query

    Returns:
        pandas Dataframe
    """
    logger.info("Reading in dataframe from SQL Server.")
    conn.execution_options(autocommit=True)
    logger.info(f"Getting dataframe from SQL database {database}")
    logger.info(f"Running query:\n\n {query}")
    df = pd.read_sql_query(query, conn)
    return df

def write_df_to_server(conn, server, database, df_to_write, table_name) -> None:
    """Writes a pandas DataFrame to a table on a given SQL server using SQL Alchemy.
       Requires mssql and pyodbc packages.

    Parameters:
        database: database name
        df_to_write: df to write to a SQL Server table
        table_name: SQL Server table name

    Returns
        Write to a SQL Server table.
    """
    logger.info(f"Writing dataframe to SQL Server designated {table_name}.")
    conn.execution_options(autocommit=True)
    df_to_write.to_sql(name=table_name, con=conn, if_exists='fail', index=False)
