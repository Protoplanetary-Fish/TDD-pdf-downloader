# tests/test_file_request.py
import pytest
from pathlib import Path
from app.data_parser import ExcelReader, is_valid_url

def test_read_excel() -> None:
    r = ExcelReader("data/in/GRI_2017_2020.xlsx")
    assert not r.data.empty

def test_find_url_columns_excel() -> None:
    r = ExcelReader("data/in/GRI_2017_2020.xlsx")
    url_found = False
    for column in r.data.columns:
        for value in r.data[column]:
            if is_valid_url(str(value)):
                url_found = True
                break
        if url_found:
            break
    assert url_found, "No URLs found in the DataFrame"