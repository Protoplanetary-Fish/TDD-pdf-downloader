from urllib.parse import urlparse

def get_host(url: str) -> str:
    """Extract host from URL safely."""
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""