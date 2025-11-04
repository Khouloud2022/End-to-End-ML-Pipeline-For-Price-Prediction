import os
import zipfile

import pandas as pd
import pytest

from pathlib import Path

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
    # use an explicit temp extract dir in tests to avoid polluting the repo
    df = ingestor.ingest(zip_path, extract_dir=str(tmp_path))

    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 2)
    assert list(df.columns) == ["a", "b"]
    assert df.iloc[0]["a"] == 1


def test_multiple_csvs_concat(tmp_path):
    csv1 = "x,y\n10,100\n20,200\n"
    csv2 = "x,y\n30,300\n40,400\n"
    zip_path = _make_zip(tmp_path, {"one.csv": csv1, "two.csv": csv2}, "multi.zip")

    ingestor = ZipDataIngestor()
    df = ingestor.ingest(zip_path, extract_dir=str(tmp_path))  # concat is True by default

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
        _ = ingestor.ingest(zip_path, extract_dir=str(tmp_path), concat=False)


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


def test_default_extracts_to_data_processed(tmp_path):
    """Verify that calling ingest without extract_dir writes into data/processed by default."""
    csv = "p,q\n7,8\n"
    zip_path = _make_zip(tmp_path, {"default_keep.csv": csv}, "default.zip")

    ingestor = ZipDataIngestor()

    repo_root = Path(__file__).resolve().parents[1]
    expected_dir = repo_root / "data" / "processed"
    existed_before = expected_dir.exists()

    # Ensure consistent start
    if not existed_before:
        expected_dir.mkdir(parents=True, exist_ok=True)

    # With the new behavior each archive is extracted into its own
    # subdirectory under data/processed named after the archive stem.
    archive_stem = "default"
    archive_dir = expected_dir / archive_stem
    target_file = archive_dir / "default_keep.csv"
    if target_file.exists():
        target_file.unlink()

    try:
        df = ingestor.ingest(zip_path)  # default behavior

        assert df.shape == (1, 2)
        assert target_file.exists()
    finally:
        # Clean up what we created in data/processed
        if target_file.exists():
            target_file.unlink()
        # If the directory didn't exist before the test and is now empty, remove it
        if not existed_before:
            # remove the archive subdirectory if it is empty
            try:
                next(archive_dir.iterdir())
            except (StopIteration, FileNotFoundError):
                try:
                    archive_dir.rmdir()
                except OSError:
                    pass
