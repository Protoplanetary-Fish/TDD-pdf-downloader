from pathlib import Path
import json
from threading import Lock

BLACKLIST_FILE = Path("data/out/blacklist.json")
BLACKLIST_REASONS = {
    "DNS", "CONNECTION", "SSL ERROR", "REQUEST ERROR", "TIMEOUT",
    "NOT A PDF", "HTML FILE", "CORRUPT PDF"
}

class Blacklist:
    def __init__(self):
        self.lock = Lock()
        self.urls = set()  # For specific URLs
        self.hosts = set()  # For hosts
        self.load()

    def load(self):
        if BLACKLIST_FILE.exists():
            with open(BLACKLIST_FILE, "r") as f:
                data = json.load(f)
                self.urls = set(data.get("urls", []))
                self.hosts = set(data.get("hosts", []))

    def contains_url(self, url: str) -> bool:
        with self.lock:
            return url in self.urls

    def contains_host(self, host: str) -> bool:
        with self.lock:
            return host in self.hosts

    def add_url(self, url: str):
        with self.lock:
            self.urls.add(url)
            self._save()

    def add_host(self, host: str):
        with self.lock:
            self.hosts.add(host)
            self._save()

    def _save(self):
        with open(BLACKLIST_FILE, "w") as f:
            json.dump({"urls": list(self.urls), "hosts": list(self.hosts)}, f)