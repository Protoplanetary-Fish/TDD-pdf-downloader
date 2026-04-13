import pytest
import requests
from pathlib import Path
from unittest.mock import MagicMock, patch
from app.pdf_downloader import PDFDownloader
from app.pdf_validator import PdfValidator
from app.download_and_validate import download_and_validate_pdf

# --- Test Malformed URLs ---
@pytest.mark.parametrize("malformed_url", [
    "ftp://example.com/file.pdf",
    "example.com/file.pdf",
    "",
    None,
    "../malicious.pdf"
])
def test_malformed_urls(malformed_url):
    save_path = Path("data/out/test_sample.pdf")
    assert PdfDownloader.download(malformed_url, save_path) is False

# --- Test Network Errors ---
@pytest.mark.parametrize("exception", [
    requests.exceptions.Timeout(),
    requests.exceptions.SSLError(),
    requests.exceptions.ConnectionError(),
    Exception("Generic error")
])
def test_network_errors(mocker, exception):
    mocker.patch("requests.get", side_effect=exception)
    save_path = Path("data/out/test_sample.pdf")
    assert PdfDownloader.download("http://example.com/file.pdf", save_path) is False

# --- Test Valid and Invalid PDFs ---
def test_valid_pdf(mocker):
    # Mock a valid PDF download
    mock_response = MagicMock()
    mock_response.content = b"%PDF-1.4 fake pdf content"
    mock_response.raise_for_status = MagicMock()
    mocker.patch("requests.get", return_value=mock_response)

    # Mock filetype.guess to return a PDF
    mocker.patch("filetype.guess", return_value=type('obj', (object,), {
        'extension': 'pdf',
        'mime': 'application/pdf'
    })())

    save_path = Path("data/out/test_sample.pdf")
    assert download_and_validate_pdf("http://example.com/file.pdf", save_path) is True

def test_invalid_file_type(mocker):
    # Mock a non-PDF download
    mock_response = MagicMock()
    mock_response.content = b"Not a PDF"
    mock_response.raise_for_status = MagicMock()
    mocker.patch("requests.get", return_value=mock_response)

    # Mock filetype.guess to return a non-PDF
    mocker.patch("filetype.guess", return_value=None)

    save_path = Path("data/out/test_sample.pdf")
    assert download_and_validate_pdf("http://example.com/file.pdf", save_path) is False

# --- Test Path Traversal ---
def test_path_traversal(mocker):
    # Mock the downloader to fail on path traversal
    mocker.patch("app.pdf_downloader.PdfDownloader.download", return_value=False)
    save_path = Path("data/out/test_sample.pdf")
    assert download_and_validate_pdf("http://example.com/../../../etc/passwd.pdf", save_path) is False