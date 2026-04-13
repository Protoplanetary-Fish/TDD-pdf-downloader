# data_parser.py
import pandas as pd
from pathlib import Path
from urllib.parse import urlparse

def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


class ExcelReader:
    def __init__(self, path: Path | str) -> None:
        self.file_path = Path(path)
        self.data = pd.read_excel(self.file_path)

    def get_valid_urls(self):
        """
        Scan all columns and yield (url, BRnum) pairs.
        """
        if "BRnum" not in self.data.columns:
            raise ValueError("Excel must contain 'BRnum' column.")

        for _, row in self.data.iterrows():
            brnum = str(row["BRnum"])

            for col in self.data.columns:
                value = str(row[col])

                if is_valid_url(value):
                    yield value, brnum