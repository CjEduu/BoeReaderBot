"""
BOE Resumer - Document summarization pipeline with Telegram delivery.

This script orchestrates the flow: Load File → Extract → Summarize → Send.
Supports PDF and XML files.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from text_extractor import extract_text, SUPPORTED_EXTENSIONS
from summarizer import create_summarizer
from telegram_sender import send_telegram_message


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

    # Step 1: Extract text from file
    print("📖 Extracting text...")
    text = extract_text(file_path)
    print(f"   Extracted {len(text)} characters")

    # Step 2: Summarize the text
    print("🤖 Generating summary...")
    summarizer = create_summarizer(config["MODEL_API_KEY"], model_type="gemini")
    summary = summarizer.summarize(text)
    print(f"   Generated summary ({len(summary)} characters)")

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
        extensions = ", ".join(SUPPORTED_EXTENSIONS)
        print(f"Usage: python main.py <file_path>")
        print(f"Supported formats: {extensions}")
        print("Example: python main.py document.pdf")
        print("Example: python main.py data.xml")
        sys.exit(1)

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
