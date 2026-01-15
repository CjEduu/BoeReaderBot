import os
from datetime import datetime
import httpx
from pathlib import Path

# Config
BASE_URL = "https://www.boe.es/datosabiertos/api/boe/sumario/"
DOWNLOAD_DIR = Path("downloads")
CACHE_DIR = Path("cache")


def _get_today_cache_path() -> Path:
    """Get the cache path for today's summary."""
    today_str = datetime.now().strftime("%Y%m%d")
    return CACHE_DIR / f"boe_{today_str}_summary.txt"


def _is_summary_cached() -> bool:
    """Check if today's summary is already cached."""
    return _get_today_cache_path().exists()


def download_boe_xml() -> Path | None:
    today_str = datetime.now().strftime("%Y%m%d")
    file_path = DOWNLOAD_DIR / f"boe_{today_str}.xml"

    # Skip download if summary is already cached
    if _is_summary_cached():
        print(f"Summary for {today_str} already cached. Skipping download.")
        # Return existing XML if it exists, otherwise we still need it
        if file_path.exists():
            return file_path

    DOWNLOAD_DIR.mkdir(exist_ok=True)
    url = f"{BASE_URL}{today_str}"

    # The BOE API requires a specific Accept header
    headers = {
        "Accept": "application/xml",
        "User-Agent": "Python/httpx Agent"  # Some gov APIs block default library agents
    }

    print(f"Fetching XML for {today_str}...")
    try:
        # We use a client to handle headers and redirects cleanly
        with httpx.Client(follow_redirects=True) as client:
            response = client.get(url, headers=headers)
            
            # If it's still 400, it might be that the summary isn't out yet
            if response.status_code == 400:
                print("⚠️ API returned 400. The summary might not be published yet (usually available by 08:00-09:00).")
                return None

            response.raise_for_status()
            file_path.write_bytes(response.content)
            
        print(f"✅ Saved to {file_path}")
        
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP Error: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

    return Path(file_path)

if __name__ == "__main__":
    download_boe_xml()