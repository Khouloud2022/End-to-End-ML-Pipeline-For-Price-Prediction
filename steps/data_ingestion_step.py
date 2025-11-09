import pandas as pd 
from src.ingest_data import DataIngestionFactory
from zenml import step

@step
def data_ingestion_step(file_path: str) -> pd.DataFrame:
    """Ingest data from a specified file path using the appropriate data ingestor based on file extension.
    Args:
        file_path (str): The path to the data file.
    Returns:
        pd.DataFrame: The ingested data as a pandas DataFrame.
    """
    
    file_extension = ".zip"
    data_ingestor = DataIngestionFactory.get_data_ingestor(file_extension)
    df = data_ingestor.ingest_data(file_path)
    return df
