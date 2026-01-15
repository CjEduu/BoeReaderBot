"""
Telegram Bot for BOE Resumer.

Features:
- /register - Subscribe to daily BOE summaries
- /unregister - Unsubscribe from daily summaries
- /summary - Get today's BOE summary immediately
- Scheduled daily sending at 10:00 AM
"""

import asyncio
import os
from datetime import time
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from pipeline import get_daily_summary
from telegram_sender import send_telegram_message
from storage import (
    load_subscribers,
    add_subscriber,
    remove_subscriber,
    is_subscriber,
    get_subscriber_count,
)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    await update.message.reply_text(
        "👋 ¡Bienvenido al Bot del BOE!\n\n"
        "Comandos disponibles:\n"
        "• /register - Suscribirse al resumen diario (10:00 AM)\n"
        "• /unregister - Cancelar suscripción\n"
        "• /summary - Obtener el resumen de hoy ahora\n"
        "• /status - Ver estado de tu suscripción"
    )


async def register_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /register command - subscribe user to daily updates."""
    chat_id = update.effective_chat.id

    if is_subscriber(chat_id):
        await update.message.reply_text(
            "✅ Ya estás suscrito al resumen diario del BOE.\n"
            "Recibirás el resumen cada día a las 10:00 AM."
        )
        return

    add_subscriber(chat_id)

    await update.message.reply_text(
        "🎉 ¡Te has suscrito correctamente!\n\n"
        "Recibirás el resumen del BOE cada día a las 10:00 AM.\n"
        "Usa /unregister para cancelar en cualquier momento."
    )
    print(f"📝 New subscriber: {chat_id}")


async def unregister_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /unregister command - unsubscribe user from daily updates."""
    chat_id = update.effective_chat.id

    if not is_subscriber(chat_id):
        await update.message.reply_text(
            "ℹ️ No estás suscrito actualmente.\n"
            "Usa /register para suscribirte."
        )
        return

    remove_subscriber(chat_id)

    await update.message.reply_text(
        "👋 Te has dado de baja correctamente.\n"
        "Ya no recibirás el resumen diario.\n\n"
        "Puedes volver a suscribirte cuando quieras con /register."
    )
    print(f"📝 Subscriber removed: {chat_id}")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /status command - show subscription status."""
    chat_id = update.effective_chat.id

    if is_subscriber(chat_id):
        await update.message.reply_text(
            "✅ Estás suscrito al resumen diario.\n"
            "📅 Hora de envío: 10:00 AM"
        )
    else:
        await update.message.reply_text(
            "❌ No estás suscrito.\n"
            "Usa /register para suscribirte."
        )


async def summary_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /summary command - send today's BOE summary immediately."""
    await update.message.reply_text("⏳ Obteniendo resumen del BOE de hoy...")

    try:
        summary = get_daily_summary()
        if summary:
            await send_telegram_message(
                bot_token=get_bot_token(),
                chat_id=str(update.effective_chat.id),
                message=summary,
                parse_mode="MarkdownV2"
            )
        else:
            await update.message.reply_text(
                "❌ No se pudo obtener el resumen.\n"
                "El BOE de hoy puede no estar disponible todavía."
            )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def send_daily_summary(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Scheduled job: send daily summary to all subscribers."""
    print("🕐 Running scheduled daily summary...")

    subscribers = load_subscribers()
    if not subscribers:
        print("   No subscribers to notify")
        return

    try:
        summary = get_daily_summary()
        if not summary:
            print("   Failed to get summary")
            return

        print(f"   Sending to {len(subscribers)} subscribers...")

        for chat_id in subscribers:
            try:
                await send_telegram_message(
                    bot_token=get_bot_token(),
                    chat_id=str(chat_id),
                    message=summary,
                    parse_mode="MarkdownV2"
                )
                print(f"   ✅ Sent to {chat_id}")
            except Exception as e:
                print(f"   ❌ Failed to send to {chat_id}: {e}")

        print("   Daily summary job complete")

    except Exception as e:
        print(f"   ❌ Error in daily summary job: {e}")


def get_bot_token() -> str:
    """Get the Telegram bot token from environment."""
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("Missing TELEGRAM_BOT_TOKEN environment variable")
    return token


def run_bot() -> None:
    """Start the Telegram bot."""
    print("🤖 Starting BOE Resumer Bot...")

    token = get_bot_token()
    app = Application.builder().token(token).build()

    # Add command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("register", register_command))
    app.add_handler(CommandHandler("unregister", unregister_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("summary", summary_command))

    # Schedule daily summary at 10:00 AM
    job_queue = app.job_queue
    job_queue.run_daily(
        send_daily_summary,
        time=time(hour=10, minute=0, second=0),
        name="daily_boe_summary"
    )
    print("📅 Scheduled daily summary at 10:00 AM")

    print(f"📊 Current subscribers: {get_subscriber_count()}")
    print("✅ Bot is running. Press Ctrl+C to stop.")

    # Run the bot
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    run_bot()
