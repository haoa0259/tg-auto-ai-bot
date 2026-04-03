import asyncio
import aiohttp
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8759872051:AAEtPVCsQq-uNtrOkOfGhb3baXOapNzr91w"
YOUR_TG_ID = 822241945
TARGET_GROUP = -1003728062886
AI_API_KEY = "sk-d2509e77f1b54821bb6f4b604ea3ef05"
API_URL = "https://api.deepseek.com/v1/chat/completions"

async def get_ai(text):
    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": text}],
        "temperature": 0.7
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, headers=headers, json=data, timeout=10) as resp:
                if resp.status != 200:
                    return "Sorry, I can't answer now."
                res = await resp.json()
                return res["choices"][0]["message"]["content"].strip()
    except:
        return "Sorry, I can't answer now."

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user
    bot_id = context.bot.id

    if not chat or chat.id != TARGET_GROUP:
        return
    if not msg or not user:
        return

    trigger = False

    if msg.entities:
        for e in msg.entities:
            if e.type == "mention" and e.user:
                if e.user.id == YOUR_TG_ID or e.user.id == bot_id:
                    trigger = True

    if msg.reply_to_message:
        reply_user = msg.reply_to_message.from_user
        if reply_user.id == YOUR_TG_ID or reply_user.id == bot_id:
            trigger = True

    if not trigger:
        return

    text = msg.text or ""
    if not text:
        return

    reply = await get_ai(text)
    await msg.reply_text(reply)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.run_polling()

if __name__ == "__main__":
    main()
