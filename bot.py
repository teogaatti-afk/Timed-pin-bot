import os
import re
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")  # токен из переменных Render

async def pin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("Ответь на сообщение, которое хочешь закрепить.")
        return

    match = re.search(r"(\d+)([smhd])", " ".join(context.args))
    if not match:
        await update.message.reply_text("Используй формат: /pin 10m (s=сек, m=мин, h=час, d=день)")
        return

    value, unit = int(match[1]), match[2]
    seconds = {"s":1, "m":60, "h":3600, "d":86400}[unit] * value
    msg = update.message.reply_to_message

    await context.bot.pin_chat_message(chat_id=update.effective_chat.id, message_id=msg.message_id)
    await update.message.reply_text(f"Сообщение закреплено на {value}{unit} ⏳")

    await asyncio.sleep(seconds)

    await context.bot.unpin_chat_message(chat_id=update.effective_chat.id, message_id=msg.message_id)
    await update.message.reply_text("Сообщение откреплено ⏰")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("pin", pin))

app.run_polling()
