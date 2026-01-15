import os
from datetime import datetime
import httpx
from pathlib import Path

# Config
BASE_URL = "https://www.boe.es/datosabiertos/api/boe/sumario/"
DOWNLOAD_DIR = Path("downloads")
STATUS_FILE = Path(".last_run")

def download_boe_xml():
    today_str = datetime.now().strftime("%Y%m%d")
    
    if STATUS_FILE.exists() and STATUS_FILE.read_text().strip() == today_str:
        print(f"Already processed for {today_str}. Skipping.")
        return

    DOWNLOAD_DIR.mkdir(exist_ok=True)
    url = f"{BASE_URL}{today_str}"
    file_path = DOWNLOAD_DIR / f"boe_{today_str}.xml"

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
                return

            response.raise_for_status()
            file_path.write_bytes(response.content)
            
        STATUS_FILE.write_text(today_str)
        print(f"✅ Saved to {file_path}")
        
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP Error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    download_boe_xml()