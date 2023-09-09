"""
Purpose of the script: Load the list of NHS GitHub organisations from a YAML file.
"""
import yaml
import logging

logger = logging.getLogger(__name__)

def load_yaml(path: str) -> list:
    """
    Load a list from a YAML file.
    
    Parameters:
        path (str): The path to the YAML file
        
    Returns:
        list: A list of dictionaries
    """
    logger.info(f"Load yaml from {path}.")
    with open(path, "r") as f:
        return yaml.load(f, Loader=yaml.FullLoader)