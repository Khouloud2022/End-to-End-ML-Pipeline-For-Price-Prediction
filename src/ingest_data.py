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
        there. If omitted, files are extracted to `data/processed` under the
        project root (created automatically) so outputs are easy to find.
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

        # Default extraction directory: repository/data/processed
        # If the caller provides an explicit `extract_dir` we use it and leave
        # the extracted files in place. When `extract_dir` is None we ensure
        # `data/processed` exists at the project root and extract there.
        if extract_dir is None:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            # Extract each archive into its own subfolder under data/processed
            target_dir = os.path.join(project_root, "data", "processed", base_name)
            os.makedirs(target_dir, exist_ok=True)
            temp_dir_ctx = None
        else:
            target_dir = extract_dir
            temp_dir_ctx = None

        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(target_dir)

            extracted_files = os.listdir(target_dir)

            # Support CSV and TSV files inside archives. TSVs are common for
            # datasets; we detect the extension and pass a suitable sep to
            # pandas.read_csv.
            data_files = [f for f in extracted_files if f.lower().endswith(('.csv', '.tsv'))]
            if len(data_files) == 0:
                raise ValueError("No CSV/TSV files found in the zip archive.")

            data_paths = [os.path.join(target_dir, f) for f in data_files]
            if len(data_paths) == 1:
                p = data_paths[0]
                if p.lower().endswith('.tsv'):
                    df = pd.read_csv(p, sep='\t')
                else:
                    df = pd.read_csv(p)
                return df

            # multiple files: either concatenate or raise based on concat flag
            if not concat:
                raise ValueError(
                    "Multiple data files found in the zip archive; set concat=True to concatenate them."
                )

            dfs = []
            for p in data_paths:
                if p.lower().endswith('.tsv'):
                    dfs.append(pd.read_csv(p, sep='\t'))
                else:
                    dfs.append(pd.read_csv(p))

            df = pd.concat(dfs, ignore_index=True)
            return df
        

class DataIngestionFactory:
    """Factory to obtain an appropriate DataIngestor for a given file.

    Usage example:
        ingestor = DataIngestionFactory.get_ingestor_for_path('data/raw/archive.zip')
        df = ingestor.ingest('data/raw/archive.zip')
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