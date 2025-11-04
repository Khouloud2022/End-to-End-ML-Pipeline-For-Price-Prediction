import os
import zipfile
import tempfile
from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd


class DataIngestor(ABC):
    """Abstract base class for data ingestors.

    Concrete implementations should implement the `ingest` method which
    takes a path to an input file (e.g. a ZIP archive) and returns a
    pandas.DataFrame.
    """

    @abstractmethod
    def ingest(self, file_path: str, extract_dir: Optional[str] = None, *, concat: bool = True) -> pd.DataFrame:
        """Ingest data from `file_path` and return a pandas DataFrame.

        If `extract_dir` is provided, any extracted files will be placed
        there; otherwise a temporary directory will be used and cleaned up
        automatically.
        """
        raise NotImplementedError


class ZipDataIngestor(DataIngestor):
    """Ingestor for ZIP archives that contain one or more CSV files.

    This implementation extracts the ZIP to a temporary directory (by
    default), finds CSV files, reads them with pandas and returns the
    resulting DataFrame. If multiple CSV files are present they are
    concatenated by default; pass `concat=False` to raise instead.
    """

    def ingest(self, file_path: str, extract_dir: Optional[str] = None, *, concat: bool = True) -> pd.DataFrame:
        # Basic validation: ensure the path exists and is a zip file
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")
        if not zipfile.is_zipfile(file_path):
            raise ValueError(f"The file at {file_path} is not a valid zip file.")

        # Use a temporary directory unless an explicit extract_dir is given
        temp_dir_ctx = tempfile.TemporaryDirectory() if extract_dir is None else None
        target_dir = temp_dir_ctx.name if temp_dir_ctx is not None else extract_dir

        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(target_dir)

            extracted_files = os.listdir(target_dir)
            csv_files = [f for f in extracted_files if f.lower().endswith('.csv')]
            if len(csv_files) == 0:
                raise ValueError("No CSV files found in the zip archive.")

            # If there are multiple CSVs we either concatenate them or raise
            # depending on the `concat` flag. Concatenation is the default
            # behavior and will vertically stack all CSVs (resetting the
            # index).
            csv_paths = [os.path.join(target_dir, f) for f in csv_files]
            if len(csv_paths) == 1:
                df = pd.read_csv(csv_paths[0])
                return df

            # multiple CSVs
            if not concat:
                raise ValueError(
                    "Multiple CSV files found in the zip archive; set concat=True to concatenate them."
                )

            # Read and concatenate all CSVs. This assumes compatible columns
            # across files; if schemas differ you may wish to provide more
            # robust merging/aligning logic.
            dfs = [pd.read_csv(p) for p in csv_paths]
            df = pd.concat(dfs, ignore_index=True)
            return df
        finally:
            # Clean up the temporary directory if we created one. If an
            # explicit extract_dir was provided we leave it alone so the
            # caller can inspect extracted files.
            if temp_dir_ctx is not None:
                temp_dir_ctx.cleanup()


class DataIngestionFactory:
    """Factory to obtain an appropriate DataIngestor for a given file.

    Usage example:
        ingestor = DataIngestionFactory.get_ingestor_for_path('data/archive.zip')
        df = ingestor.ingest('data/archive.zip')
    """

    @staticmethod
    def get_ingestor(file_extension: str) -> DataIngestor:
        if file_extension == ".zip":
            return ZipDataIngestor()
        raise ValueError(f"No ingestor available for the file type of {file_extension}")

    @staticmethod
    def get_ingestor_for_path(file_path: str) -> DataIngestor:
        """Choose an ingestor based on the file extension of `file_path`."""
        _, ext = os.path.splitext(file_path)
        return DataIngestionFactory.get_ingestor(ext.lower())


def _example_cli():
    """Small CLI helper demonstrating how to use the ingestor.

    Run the module as a script to extract and print a short summary of the
    CSV inside a ZIP file.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Ingest CSV data from a ZIP file")
    parser.add_argument("zip_path", help="Path to the zip archive containing a single CSV file")
    parser.add_argument("--keep-extracted", action="store_true", help="Keep extracted files in ./extracted_data instead of using a temp dir")
    args = parser.parse_args()

    target_extract_dir = "extracted_data" if args.keep_extracted else None
    ingestor = DataIngestionFactory.get_ingestor_for_path(args.zip_path)
    df = ingestor.ingest(args.zip_path, extract_dir=target_extract_dir)

    print(f"Loaded DataFrame with shape: {df.shape}")
    print("Column names:", list(df.columns))


if __name__ == "__main__":
    _example_cli()