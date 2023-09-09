"""
Purpose of script: contains cleaning and formatting tailored to our publication
"""
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def convert_date_to_year(date: pd.Series, date_format: str = "%Y-%m-%d") -> pd.Series: 
    """Extracts the year from dates in a column (e.g. '2005-06-12' becomes '2005')

    Parameters: 
        date -> the column containing the dates
        date_format -> the current format of the dates, defaults to "%Y-%m-%d"

    Returns: 
        year -> pd.Series, the transformed column containing only year
    """
    logger.info("Converting date to year.")

    date = pd.to_datetime(date, format=date_format)

    year = pd.array(date.dt.year.copy(), dtype='Int64')
    #year = date.dt.year.copy().astype(int)

    return year

def calculate_years(filled_value: int, df: pd.DataFrame) -> pd.DataFrame:
    """Calculates the number of years that each GP has been active 
    and creates a column for that data
    
    Parameters: 
        df -> pd.dataframe
        
    Returns:
        df -> pd.dataframe, containing a 'YEARS ACTIVE' column
    """
    logger.info("Calculating number of active year per GP.")

    closed = df['CLOSED'].copy().fillna(filled_value)
    opened = pd.array(df['OPENED'], dtype='Int64')
    
    df['YEARS'] = closed - opened
    df['YEARS'] = pd.array(df['YEARS'], dtype='Int64')

    return df

def process_columns(df: pd.DataFrame, date_col_names: list, string_col_names: list) -> pd.DataFrame:
    """Performs necessary processing on columns:
    Converts date columns to YEAR int, and converts string columns to uppercase

    Parameters: 
        df -> pd.Dataframe
        date_col_names -> list of column names that we want to process as dates
        string_col_names -> list of column names that we want to process as strings

    Returns: 
        df -> pd.DataFrame, containing the transformed columns
    """
    logger.info("Applying column transformation.")

    for col_name in date_col_names:
        df[col_name] = convert_date_to_year(df[col_name])
    for col_name in string_col_names:
        df[col_name] = df[col_name].str.title()

    return df
