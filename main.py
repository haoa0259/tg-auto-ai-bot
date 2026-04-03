import asyncio
import aiohttp
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Configuration
BOT_TOKEN = "8939740373:AAH6zQZ7eFZ9K5k9z7L9M8N0O9P1Q2R3S4T5U6V7W8X9Y0Z"
YOUR_USER_ID = 822241945
API_KEY = "sk-4e042e035445449f8f23c97e249f0f29"
API_URL = "https://api.deepseek.com/v1/chat/completions"

async def get_ai_response(text: str):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant. Respond naturally, concisely, and casually."},
            {"role": "user", "content": text}
        ],
        "temperature": 0.7
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, headers=headers, json=payload, timeout=15) as resp:
                if resp.status != 200:
                    return f"API Error (Status: {resp.status})"
                data = await resp.json()
                return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Request Failed: {str(e)}"

async def handle_message(update: Update, context: ContextTypes):
    message = update.effective_message
    if not message or not message.text:
        return

    mentioned = False
    if message.entities:
        for entity in message.entities:
            if entity.type == "mention" and entity.user and entity.user.id == YOUR_USER_ID:
                mentioned = True
    if message.reply_to_message and message.reply_to_message.from_user.id == YOUR_USER_ID:
        mentioned = True

    if not mentioned:
        return

    reply = await get_ai_response(message.text)
    await message.reply_text(reply)

async def start(update: Update, context: ContextTypes):
    await message.reply_text("✅ Bot online. I will auto-reply when you are mentioned.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
