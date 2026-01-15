"""
BOE Resumer - Document summarization pipeline with Telegram delivery.

This script orchestrates the flow: Load File → Extract → Summarize → Send.
Supports PDF and XML files. When run without arguments, fetches today's BOE XML.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from text_extractor import extract_text, SUPPORTED_EXTENSIONS
from summarizer import create_summarizer
from telegram_sender import send_telegram_message
from daily_fetch import download_boe_xml, DOWNLOAD_DIR

# Directory to cache generated summaries
CACHE_DIR = Path("cache")


def get_cache_path(file_path: str) -> Path:
    """Get the cache file path for a given input file."""
    CACHE_DIR.mkdir(exist_ok=True)
    input_name = Path(file_path).stem
    return CACHE_DIR / f"{input_name}_summary.txt"


def load_cached_summary(file_path: str) -> str | None:
    """Load cached summary if it exists."""
    cache_path = get_cache_path(file_path)
    if cache_path.exists():
        return cache_path.read_text(encoding="utf-8")
    return None


def save_summary_to_cache(file_path: str, summary: str) -> None:
    """Save summary to cache."""
    cache_path = get_cache_path(file_path)
    cache_path.write_text(summary, encoding="utf-8")
    print(f"   Cached summary to {cache_path}")


def load_config() -> dict[str, str]:
    """
    Load configuration from environment variables.

    Returns:
        Dictionary with configuration values.

    Raises:
        ValueError: If required environment variables are missing.
    """
    load_dotenv()

    required_vars = ["TELEGRAM_BOT_TOKEN", "CHAT_ID", "MODEL_API_KEY"]
    config: dict[str, str] = {}

    for var in required_vars:
        value = os.getenv(var)
        if not value:
            raise ValueError(f"Missing required environment variable: {var}")
        config[var] = value

    return config


def process_file(file_path: str) -> None:
    """
    Process a file: extract text, summarize, and send via Telegram.

    Args:
        file_path: Path to the file to process (PDF or XML).
    """
    print(f"📄 Loading file: {file_path}")

    # Load configuration
    config = load_config()

    # Check for cached summary first
    cached_summary = load_cached_summary(file_path)
    if cached_summary:
        print("📦 Using cached summary...")
        summary = cached_summary
        print(f"   Loaded summary ({len(summary)} characters)")
    else:
        # Step 1: Extract text from file
        print("📖 Extracting text...")
        text = extract_text(file_path)
        print(f"   Extracted {len(text)} characters")

        # Step 2: Summarize the text
        print("🤖 Generating summary...")
        summarizer = create_summarizer(config["MODEL_API_KEY"], model_type="gemini")
        summary = summarizer.summarize(text)
        print(f"   Generated summary ({len(summary)} characters)")

        # Cache the summary for future use
        save_summary_to_cache(file_path, summary)

    # Step 3: Send via Telegram
    print("📤 Sending to Telegram...")
    send_telegram_message(
        bot_token=config["TELEGRAM_BOT_TOKEN"],
        chat_id=config["CHAT_ID"],
        message=summary,
    )
    print("✅ Summary sent successfully!")

def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        # No file provided - fetch today's BOE XML
        
        file_path = download_boe_xml()
        if file_path is None:
            print("Error: Failed to download today's BOE XML.")
            sys.exit(1)

        process_file(str(file_path))
    else:
        file_path = sys.argv[1]

        if not Path(file_path).exists():
            print(f"Error: File not found: {file_path}")
            sys.exit(1)

        try:
            process_file(file_path)
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
