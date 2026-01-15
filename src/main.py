"""
BOE Resumer - Main entry point.

Usage:
    python main.py          - Run the Telegram bot (default)
    python main.py bot      - Run the Telegram bot
    python main.py pipeline - Run the pipeline once (fetch, summarize, print)
    python main.py send     - Run pipeline and send to CHAT_ID from .env
"""

import sys

from dotenv import load_dotenv


def main() -> None:
    """Main entry point."""
    load_dotenv()

    # Default to bot mode if no argument
    mode = sys.argv[1] if len(sys.argv) > 1 else "bot"

    if mode == "bot":
        from bot import run_bot
        run_bot()

    elif mode == "pipeline":
        from pipeline import get_daily_summary
        summary = get_daily_summary()
        if summary:
            print("\n" + "=" * 50)
            print(summary)
        else:
            print("Failed to get summary")
            sys.exit(1)

    elif mode == "send":
        # Legacy mode: run pipeline and send to configured CHAT_ID
        import os
        from pipeline import get_daily_summary
        from telegram_sender import send_telegram_message

        summary = get_daily_summary()
        if not summary:
            print("Failed to get summary")
            sys.exit(1)

        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("CHAT_ID")

        if not token or not chat_id:
            print("Error: TELEGRAM_BOT_TOKEN and CHAT_ID required for send mode")
            sys.exit(1)

        print("📤 Sending to Telegram...")
        send_telegram_message(token, chat_id, summary)
        print("✅ Summary sent successfully!")

    else:
        print(f"Unknown mode: {mode}")
        print("Usage: python main.py [bot|pipeline|send]")
        sys.exit(1)


if __name__ == "__main__":
    main()
