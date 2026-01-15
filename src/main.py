"""
BOE Resumer - PDF summarization pipeline with Telegram delivery.

This script orchestrates the flow: Load PDF → Extract → Summarize → Send.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from pdf_extractor import extract_text_from_pdf
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


def process_pdf(pdf_path: str) -> None:
    """
    Process a PDF file: extract, summarize, and send via Telegram.

    Args:
        pdf_path: Path to the PDF file to process.
    """
    print(f"📄 Loading PDF: {pdf_path}")

    # Load configuration
    config = load_config()

    # Step 1: Extract text from PDF
    print("📖 Extracting text from PDF...")
    text = extract_text_from_pdf(pdf_path)
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
        print("Usage: python main.py <pdf_path>")
        print("Example: python main.py document.pdf")
        sys.exit(1)

    pdf_path = sys.argv[1]

    if not Path(pdf_path).exists():
        print(f"Error: File not found: {pdf_path}")
        sys.exit(1)

    try:
        process_pdf(pdf_path)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
