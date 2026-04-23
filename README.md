# PDF Downloader

**A tool for downloading and validating PDFs from URLs listed in an Excel file, with automatic blacklisting of invalid hosts and URLs.**

---

## Table of Contents

- [Description](#description)
- [How It Works](#how-it-works)
- [Requirements](#requirements)
- [Dependencies](#dependencies)
- [Excel File Format](#excel-file-format)
- [Installation](#installation)
- [Usage](#usage)
- [Blacklist Management](#blacklist-management)
- [Parallel Downloads](#parallel-downloads)
- [Error Handling](#error-handling)
- [Authors](#authors)
- [Version History](#version-history)

---

## Description

The **PDF Downloader** tool reads URLs from an Excel file, downloads PDFs in parallel, and validates their file signatures. It automatically skips already downloaded files and blacklists unresponsive URLs and hosts for future downloads. The tool supports both simple HTTP requests and Selenium-based fallback for problematic URLs.

---

## How It Works

1. **Reads URLs from Excel**: Extracts URLs and associated IDs (e.g., BRnum) from the provided Excel file.
2. **Parallel Downloads**: Downloads PDFs in parallel using a thread pool, up to a specified maximum number of new files.
3. **Validation**: Validates downloaded files as valid PDFs.
4. **Blacklisting**: Maintains a blacklist of invalid hosts and URLs to avoid repeated failures.
5. **Fallback Mechanism**: Uses Selenium for URLs that fail with standard HTTP requests.

---

## Requirements

- **Python 3.12 or higher**
- **Internet connection** (for downloading PDFs and updating dependencies)
- **Chrome** (if using Selenium fallback)

---

## Dependencies

Install the required dependencies using:

```bash
py -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
py -m pip install -r requirements.txt
```

**Key dependencies:**

- `requests` (for HTTP requests)
- `selenium` (for fallback downloads)
- `webdriver-manager` (for managing ChromeDriver)
- `pathlib` (for file path handling)
- `concurrent.futures` (for parallel downloads)

---

## Excel File Format

The Excel file has a mandatory column:

- **BRnum**: A unique identifier for each PDF (used for naming the saved file).

Any URLs present in the file will be associated with the BRnum present in the row the URL is found at.

## Installation

1. Clone the repository:
  ```bash
   git clone <repository-url>
   cd pdf-downloader
  ```
2. Create a virtual environment and install dependencies:
  ```bash
   py -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   py -m pip install -r requirements.txt
  ```

---

## Usage

Run the downloader with:

```python
from pathlib import Path
from download_manager import DownloadManager

if __name__ == "__main__":
    excel_path = Path("data/in/GRI_2017_2020.xlsx")
    output_dir = Path("data/out")

    manager = DownloadManager(excel_path=excel_path, output_dir=output_dir, num_new_files=20)
    manager.run()
```

**Arguments:**

- `excel_path`: Path to the Excel file containing URLs.
- `output_dir`: Directory to save downloaded PDFs.
- `num_new_files`: Maximum number of new files to download.
- `max_workers`: Maximum number of parallel downloads (default: 10).

---

## Blacklist Management

Invalid hosts and URLs are automatically added to a blacklist file (`blacklist.json`). This file is used to skip failed URLs in future runs.

**Blacklist reasons:**

- `404`, `400`, `301` (HTTP errors)
- `SSL ERROR` (SSL certificate issues)
- `CONNECTION` (connection failures)
- `DNS FAILURE` (host not found)
- `SELENIUM FAILURE` (Selenium errors)

---

## Parallel Downloads

The tool uses `ThreadPoolExecutor` to download PDFs in parallel, improving performance for large batches of URLs.

---

## Error Handling

- **Already downloaded**: Skips files that already exist in the output directory.
- **Invalid PDFs**: Validates file signatures after download.
- **Fallback to Selenium**: Attempts to download via Selenium if standard HTTP requests fail.

---

## Authors

- **Frederik Lenk**

---

## Version History

- **v1.0** (2026-04-23): Initial release.