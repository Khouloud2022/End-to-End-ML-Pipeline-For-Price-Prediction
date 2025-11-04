import os
import zipfile

import pandas as pd
import pytest

from src.ingest_data import ZipDataIngestor


def _make_zip(tmp_path, files: dict, zip_name: str = "test.zip") -> str:
    """Helper to create a zip at tmp_path containing files (name->content)."""
    zip_path = tmp_path / zip_name
    with zipfile.ZipFile(zip_path, "w") as z:
        for name, content in files.items():
            z.writestr(name, content)
    return str(zip_path)


def test_single_csv_ingest(tmp_path):
    csv = "a,b\n1,2\n3,4\n"
    zip_path = _make_zip(tmp_path, {"data.csv": csv}, "single.zip")

    ingestor = ZipDataIngestor()
    df = ingestor.ingest(zip_path)

    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 2)
    assert list(df.columns) == ["a", "b"]
    assert df.iloc[0]["a"] == 1


def test_multiple_csvs_concat(tmp_path):
    csv1 = "x,y\n10,100\n20,200\n"
    csv2 = "x,y\n30,300\n40,400\n"
    zip_path = _make_zip(tmp_path, {"one.csv": csv1, "two.csv": csv2}, "multi.zip")

    ingestor = ZipDataIngestor()
    df = ingestor.ingest(zip_path)  # concat is True by default

    assert isinstance(df, pd.DataFrame)
    # two files, each with 2 rows -> 4 rows total
    assert df.shape[0] == 4
    # columns preserved
    assert list(df.columns) == ["x", "y"]


def test_multiple_csvs_no_concat_raises(tmp_path):
    csv1 = "c,d\n1,2\n"
    csv2 = "c,d\n3,4\n"
    zip_path = _make_zip(tmp_path, {"a.csv": csv1, "b.csv": csv2}, "multi_no_concat.zip")

    ingestor = ZipDataIngestor()
    with pytest.raises(ValueError):
        _ = ingestor.ingest(zip_path, concat=False)


def test_extract_dir_keeps_files(tmp_path):
    csv = "m,n\n5,6\n"
    zip_path = _make_zip(tmp_path, {"keep.csv": csv}, "keep.zip")

    extract_dir = tmp_path / "extracted"
    extract_dir_path = str(extract_dir)

    ingestor = ZipDataIngestor()
    df = ingestor.ingest(zip_path, extract_dir=extract_dir_path)

    # The extracted directory should exist and contain the CSV file
    assert os.path.isdir(extract_dir_path)
    files = os.listdir(extract_dir_path)
    assert any(f.lower().endswith(".csv") for f in files)
    assert df.shape == (1, 2)
