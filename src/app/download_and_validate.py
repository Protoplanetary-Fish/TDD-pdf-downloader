from pathlib import Path
from pdf_validator import PdfValidator
import requests


def download_and_validate_pdf(url: str, save_path: Path) -> tuple[bool, str]:
    """Download a PDF and return (success, reason)."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_bytes(response.content)
    except requests.exceptions.SSLError:
        return False, "SSL ERROR"
    except requests.exceptions.ConnectionError:
        return False, "CONNECTION"
    except requests.exceptions.Timeout:
        return False, "TIMEOUT"
    except requests.exceptions.RequestException:
        return False, "REQUEST ERROR"
    except Exception as e:
        print("Unexpected exception:", e)
        if save_path.exists():
            save_path.unlink()  # Delete the file if it exists
        return False, "DOWNLOAD ERROR"

    # Validate the file
    if not PdfValidator.is_pdf(save_path):
        save_path.unlink()  # Delete the file
        return False, "NOT A PDF"
    if PdfValidator.is_html(save_path):
        save_path.unlink()  # Delete the file
        return False, "HTML FILE"
    if not PdfValidator.check_pdf_integrity(save_path):
        save_path.unlink()  # Delete the file
        return False, "CORRUPT PDF"

    return True, "SUCCESS"