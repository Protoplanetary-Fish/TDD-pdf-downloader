from pathlib import Path
from utils import get_host
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from blacklist import Blacklist, BLACKLIST_REASONS
from download_and_validate import download_and_validate_pdf, validate_pdf
from textcolors import *
from pdf_validator import PdfValidator

# Suppress Selenium's stderr output
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--log-level=3")  # Suppress Selenium logs

class PDFDownloader:
    """
    A class that downloads PDFs and validates their file signature.
    Blacklists unresponsive URLs and hosts.
    Escalates to Selenium if simple requests fail.
    """

    def __init__(self, output_dir: Path, blacklist: Blacklist):
        self.output_dir = output_dir
        self.blacklist = blacklist

    def _format_line(self, status: str, brnum: str, action: str, url: str = "", color: str = "") -> str:
        """Formats a log line with consistent column widths."""
        return (
            f"{color}{status.ljust(20)} | "
            f"{brnum.ljust(20)} | "
            f"{action.ljust(20)} | "
            f"{url}{RESET}"
        )

    def _get_selenium_options(self) -> Options:
        """Return Selenium options for headless Chrome."""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--log-level=3")  # Suppress Selenium logs
        return options

    def _try_selenium_download(self, url: str, save_path: Path) -> tuple[bool, str]:
        """Try downloading via Selenium as a fallback renderer."""
        try:
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=self._get_selenium_options()
            )

            driver.set_page_load_timeout(5)
            driver.set_script_timeout(5)

            try:
                driver.get(url)
            except Exception:
                driver.quit()
                return False, "SELENIUM TIMEOUT"

            content = driver.page_source.encode("utf-8")

            save_path.parent.mkdir(parents=True, exist_ok=True)
            save_path.write_bytes(content)
            valid, message = validate_pdf(save_path)

            driver.quit()
            return valid, message + " (Selenium)"

        except Exception as e:
            if 'driver' in locals():
                driver.quit()

            error = str(e)
            if "ERR_NAME_NOT_RESOLVED" in error:
                return False, "DNS FAILURE"
            elif "ConnectionResetError" in error:
                return False, "CONNECTION RESET"
            else:
                return False, "SELENIUM FAILURE"

    def is_host_alive(self, host: str) -> bool:
        """Check if the host is alive, with optional Selenium fallback."""

        # Try simple requests first
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        try:
            response = requests.head(f"https://{host}", headers=headers, timeout=2)
            if response.ok:
                return True
            response = requests.get(f"https://{host}", headers=headers, timeout=2)
            return response.ok
        except requests.exceptions.RequestException:
            pass  # Fall through to Selenium

        try:
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=self._get_selenium_options()
            )
            driver.get(f"https://{host}")
            driver.quit()
            return True
        except Exception:
            return False

    def download_brnum(self, brnum: str, urls: list, index: int, total: int) -> str:
        save_path = self.output_dir / f"{brnum}.pdf"

        if save_path.exists():
            return self._format_line(
                f"[{index:03}/{total}] SKIP", brnum, "ALREADY EXISTS", "", GRAY
            )

        last_error = "NO VALID URL"

        for url in urls:
            host = get_host(url)
            if self.blacklist.contains_url(url) or self.blacklist.contains_host(host):
                continue

            # Try downloading via requests first
            success, reason = download_and_validate_pdf(url, save_path)
            if success:
                return self._format_line(
                    f"[{index:03}/{total}] OK", brnum, "SAVED", url, BLUE
                )
            elif reason in ["404", "400", "301", "CONNECTION", "SSL ERROR"]:
                self.blacklist.add_url(url)
                print(self._format_line("", reason, "Blacklisting URL", url, YELLOW))

            # If requests fail, escalate to Selenium
            success, reason = self._try_selenium_download(url, save_path)
            if success:
                return self._format_line(
                    f"[{index:03}/{total}] OK", brnum, "SAVED (Selenium)", url, BLUE
                )
            host_failed = False

            # Decide what to blacklist
            if reason in ["DNS FAILURE", "CONNECTION RESET", "SELENIUM FAILURE", "SELENIUM TIMEOUT"]:
                host_failed = True
            else:
                # Not a host issue → blacklist URL instead
                self.blacklist.add_url(url)
                print(self._format_line("", reason, "Blacklisting URL", url, YELLOW))

            if host_failed:
                self.blacklist.add_host(host)
                print(self._format_line("", reason, "Blacklisting host", host, YELLOW_BRIGHT))

            last_error = reason

        if save_path.exists():
            return self._format_line(
                f"[{index:03}/{total}] OK", brnum, "SAVED", "", BLUE
            )
        if last_error == "NO VALID URL":
            return self._format_line(
                f"[{index:03}/{total}] SKIP", brnum, last_error, "", GRAY
            )

        return self._format_line(
            f"[{index:03}/{total}] FAIL", brnum, last_error, url, RED
        )