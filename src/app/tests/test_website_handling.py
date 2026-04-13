# tests/test_robustness.py
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import requests
from app.pdf_downloader import PdfDownloader
from app.pdf_validator import PdfValidator

def test_malformed_urls():
    malformed_urls = [
        "ftp://example.com/file.pdf",
        "example.com/file.pdf",
        "",
        None,
        "../malicious.pdf"
    ]
    save_path = Path("data/out/test_sample.pdf")
    for url in malformed_urls:
        assert PdfDownloader.download(url, save_path) is False

def test_non_pdf_files(tmp_path):
    non_pdf_files = [
        tmp_path / "fake.pdf.txt",
        tmp_path / "fake.pdf.png",
        tmp_path / "fake.pdf.exe"
    ]
    for file in non_pdf_files:
        file.write_text("This is not a PDF")
        assert PdfValidator.is_pdf(file) is False

def test_corrupt_pdf(tmp_path):
    corrupt_pdf = tmp_path / "corrupt.pdf"
    corrupt_pdf.write_bytes(b"This is not a PDF")
    assert PdfValidator.is_pdf(corrupt_pdf) is False

def test_path_traversal(tmp_path):
    malicious_path = tmp_path / "../../../etc/passwd.pdf"
    save_path = tmp_path / "safe.pdf"
    assert PdfDownloader.download("http://example.com/file.pdf", malicious_path) is False
    assert PdfDownloader.download("http://example.com/file.pdf", save_path) is True

def test_timeout(mocker):
    mocker.patch("requests.get", side_effect=requests.exceptions.Timeout())
    save_path = Path("data/out/test_sample.pdf")
    assert PdfDownloader.download("http://slow.url/file.pdf", save_path) is False

def test_ssl_error(mocker):
    mocker.patch("requests.get", side_effect=requests.exceptions.SSLError())
    save_path = Path("data/out/test_sample.pdf")
    assert PdfDownloader.download("https://bad.ssl/file.pdf", save_path) is False