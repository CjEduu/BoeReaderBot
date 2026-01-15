"""Telegram bot integration module."""

import requests


TELEGRAM_API_BASE = "https://api.telegram.org/bot"


def send_telegram_message(
    bot_token: str,
    chat_id: str,
    message: str,
    parse_mode: str = "MarkdownV2",
) -> bool:
    """
    Send a message via Telegram Bot API.

    Args:
        bot_token: Telegram bot token.
        chat_id: Target chat ID.
        message: Message text to send.
        parse_mode: Message parsing mode ("Markdown" or "HTML").

    Returns:
        True if the message was sent successfully.

    Raises:
        RuntimeError: If the API request fails.
    """
    url = f"{TELEGRAM_API_BASE}{bot_token}/sendMessage"

    # Telegram has a 4096 character limit per message
    max_length = 4096

    if len(message) > max_length:
        # Split into chunks if message is too long
        chunks = _split_message(message, max_length)
        for chunk in chunks:
            _send_single_message(url, chat_id, chunk, parse_mode)
        return True

    return _send_single_message(url, chat_id, message, parse_mode)


def _send_single_message(
    url: str,
    chat_id: str,
    message: str,
    parse_mode: str | None,
) -> bool:
    """Send a single message to Telegram, with fallback for markdown errors."""
    payload: dict[str, str] = {
        "chat_id": chat_id,
        "text": message,
    }
    if parse_mode:
        payload["parse_mode"] = parse_mode

    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()

        result = response.json()
        if not result.get("ok"):
            raise RuntimeError(f"Telegram API error: {result.get('description')}")

        return True

    except requests.RequestException as e:
        # If markdown parsing failed (400 error), retry without parse_mode
        if parse_mode and "400" in str(e):
            print("⚠️  Markdown parsing failed, retrying as plain text...")
            return _send_single_message(url, chat_id, message, parse_mode=None)
        raise RuntimeError(f"Failed to send Telegram message: {e}") from e


def _split_message(message: str, max_length: int) -> list[str]:
    """
    Split a long message into chunks.

    Args:
        message: The message to split.
        max_length: Maximum length per chunk.

    Returns:
        List of message chunks.
    """
    chunks: list[str] = []
    lines = message.split("\n")
    current_chunk = ""

    for line in lines:
        if len(current_chunk) + len(line) + 1 <= max_length:
            current_chunk += line + "\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = line + "\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks
