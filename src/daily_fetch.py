import os
from datetime import datetime
import httpx
from pathlib import Path

# Config
BASE_URL = "https://www.boe.es/datosabiertos/api/boe/sumario/"
DOWNLOAD_DIR = Path("downloads")
STATUS_FILE = Path(".last_run")

def download_boe_xml():
    # 1. Check if we already ran today
    today_str = datetime.now().strftime("%Y%m%d")
    
    if STATUS_FILE.exists() and STATUS_FILE.read_text().strip() == today_str:
        print(f"Already processed for {today_str}. Skipping.")
        return

    # 2. Prepare environment
    DOWNLOAD_DIR.mkdir(exist_ok=True)
    url = f"{BASE_URL}{today_str}"
    file_path = DOWNLOAD_DIR / f"boe_{today_str}.xml"

    # 3. Download
    print(f"Fetching XML for {today_str}...")
    try:
        response = httpx.get(url, follow_redirects=True)
        response.raise_for_status()
        
        file_path.write_bytes(response.content)
        
        # 4. Update status only on success
        STATUS_FILE.write_text(today_str)
        print(f"✅ Saved to {file_path}")
    except Exception as e:
        print(f"❌ Error downloading: {e}")

if __name__ == "__main__":
    download_boe_xml():