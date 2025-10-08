import os
import re
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Отправь /pin <время> в ответ на сообщение, чтобы закрепить его на время."
    )

# Команда /pin
async def pin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Проверяем, что команда в ответ на сообщение
    if not update.message or not update.message.reply_to_message:
        await update.message.reply_text(
            "Эту команду нужно отправлять в ответ на сообщение, которое хочешь закрепить."
        )
        return

    # Парсим время: 10s, 5m, 2h
    duration_text = context.args[0] if context.args else "1m"
    match = re.match(r"(\d+)([smhd])", duration_text)
    if not match:
        await update.message.reply_text(
            "Используй формат: /pin 10m (s=секунды, m=минуты, h=часы, d=дни)"
        )
        return

    value, unit = int(match[1]), match[2]
    multipliers = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    seconds = value * multipliers[unit]

    try:
        # Закрепляем сообщение
        await context.bot.pin_chat_message(
            chat_id=update.effective_chat.id,
            message_id=update.message.reply_to_message.id
        )
        await update.message.reply_text(f"Сообщение закреплено на {value}{unit}.")

        # Ждём указанное время
        await asyncio.sleep(seconds)

        # Открепляем
        await context.bot.unpin_chat_message(chat_id=update.effective_chat.id)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Сообщение откреплено.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

# Основная функция
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("pin", pin_message))
    app.run_polling()

if __name__ == "__main__":
    main()
