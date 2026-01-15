"""
Pipeline module for BOE document processing.

Handles: Fetching → Extracting → Summarizing (no Telegram logic).
"""

import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from text_extractor import extract_text
from summarizer import create_summarizer
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


def get_api_key() -> str:
    """Get the model API key from environment."""
    load_dotenv()
    api_key = os.getenv("MODEL_API_KEY")
    if not api_key:
        raise ValueError("Missing required environment variable: MODEL_API_KEY")
    return api_key


def fetch_daily_boe() -> Path | None:
    """
    Fetch today's BOE XML file.

    Returns:
        Path to the downloaded file, or None if failed.
    """
    print("🌐 Fetching today's BOE XML...")
    return download_boe_xml()


def get_daily_summary(force_refresh: bool = False) -> str | None:
    """
    Get today's BOE summary, using cache if available.

    Args:
        force_refresh: If True, regenerate summary even if cached.

    Returns:
        The summary text, or None if fetching/processing failed.
    """
    # Fetch today's BOE
    file_path = fetch_daily_boe()
    if file_path is None:
        print("❌ Failed to fetch BOE XML")
        return None

    return process_file(str(file_path), force_refresh=force_refresh)


def process_file(file_path: str, force_refresh: bool = False) -> str:
    """
    Process a file: extract text and summarize.

    Args:
        file_path: Path to the file to process (PDF or XML).
        force_refresh: If True, regenerate summary even if cached.

    Returns:
        The generated summary text.
    """
    print(f"📄 Processing file: {file_path}")

    # Check cache first (unless force refresh)
    if not force_refresh:
        cached_summary = load_cached_summary(file_path)
        if cached_summary:
            print("📦 Using cached summary...")
            print(f"   Loaded summary ({len(cached_summary)} characters)")
            return cached_summary

    # Extract text from file
    print("📖 Extracting text...")
    text = extract_text(file_path)
    print(f"   Extracted {len(text)} characters")

    # Summarize the text
    print("🤖 Generating summary...")
    api_key = get_api_key()
    summarizer = create_summarizer(api_key, model_type="gemini")
    summary = summarizer.summarize(text)
    print(f"   Generated summary ({len(summary)} characters)")

    # Cache the summary for future use
    save_summary_to_cache(file_path, summary)

    return summary


if __name__ == "__main__":
    # Quick test: fetch and summarize today's BOE
    summary = get_daily_summary(force_refresh=False)
    if summary:
        print("\n" + "=" * 50)
        print(summary)
