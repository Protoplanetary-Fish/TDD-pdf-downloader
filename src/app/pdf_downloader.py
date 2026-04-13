from pathlib import Path
from colorama import Fore, Style, init
from utils import get_host
from blacklist import Blacklist, BLACKLIST_REASONS
from download_and_validate import download_and_validate_pdf
import requests

class PDFDownloader:
    RED = Fore.RED + Style.BRIGHT
    BLUE = Fore.BLUE + Style.BRIGHT
    GRAY = Fore.LIGHTBLACK_EX + Style.BRIGHT
    YELLOW_BRIGHT = Fore.YELLOW + Style.BRIGHT
    YELLOW = Fore.YELLOW + Style.DIM
    RESET = Style.RESET_ALL

    def __init__(self, output_dir: Path, blacklist: Blacklist):
        self.output_dir = output_dir
        self.blacklist = blacklist

    def is_host_alive(self, host: str) -> bool:
        try:
            # First, try a HEAD request
            response = requests.head(f"https://{host}", timeout=5)
            if response.ok:
                return True
            # If HEAD fails, try a GET request
            response = requests.get(f"https://{host}", timeout=5)
            return response.ok
        except requests.RequestException:
            return False

    def download_brnum(self, brnum: str, urls: list, index: int, total: int) -> str:
        save_path = self.output_dir / f"{brnum}.pdf"

        if save_path.exists():
            return f"[{index:03}/{total}] {self.GRAY}SKIP{self.RESET}    | {brnum} | ALREADY EXISTS "

        last_error = "NO VALID URL"

        for url in urls:
            host = get_host(url)
            if self.blacklist.contains_url(url) or self.blacklist.contains_host(host):
                continue

            # Check if the host is alive before attempting download
            if not self.is_host_alive(host):
                self.blacklist.add_host(host)
                print(f"{self.YELLOW_BRIGHT}HOST DOWN        | Blacklisting host        | {host}{self.RESET}")
                continue

            success, reason = download_and_validate_pdf(url, save_path)

            if success:
                return f"[{index:03}/{total}] {self.BLUE}OK     {self.RESET} | {brnum} | SAVED          | {url}"
            if reason in BLACKLIST_REASONS:
                    self.blacklist.add_url(url)
                    print(f"{self.YELLOW}{reason.ljust(15)}  | Blacklisting URL         | {url}{self.RESET}")

            last_error = f"{reason.ljust(15)}| {url}"

        if save_path.exists():
            return f"[{index:03}/{total}] {self.BLUE}OK     {self.RESET} | {brnum} | SAVED          | {url}"
        if last_error == "NO VALID URL":
            return f"[{index:03}/{total}] {self.GRAY}SKIP   {self.RESET} | {brnum} | {last_error}"

        return f"[{index:03}/{total}] {self.RED}FAIL   {self.RESET} | {brnum} | {last_error}"