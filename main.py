import os
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    filters,
    ContextTypes
)
import aiohttp

# 从 GitHub Secrets 读取
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
API_BASE_URL = "https://api.openai.com/v1"
MODEL_NAME = "gpt-3.5-turbo"
MY_USER_ID = 862731773  # 你的正确ID：8475704328

async def get_ai_response(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_BASE_URL}/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=10
            ) as resp:
                if resp.status != 200:
                    return "Sorry, I cannot reply right now."
                result = await resp.json()
                return result["choices"][0]["message"]["content"].strip()
    except Exception:
        return "Sorry, I cannot reply right now."

async def handle_message(update: Update, context: ContextTypes):
    msg = update.effective_message
    chat = update.effective_chat
    if not msg or not msg.text or not chat:
        return

    bot_id = context.bot.id
    should_reply = False

    # --- 私聊：只回复你的消息 ---
    if chat.type == "private":
        if update.effective_user and update.effective_user.id == MY_USER_ID:
            should_reply = True

    # --- 群聊：只在被@或被回复时回复 ---
    elif chat.type in ["group", "supergroup"]:
        # 被@
        if msg.entities:
            for entity in msg.entities:
                if entity.type == "mention" and entity.user:
                    if entity.user.id == MY_USER_ID or entity.user.id == bot_id:
                        should_reply = True
        # 被回复
        if not should_reply and msg.reply_to_message:
            reply_to_id = msg.reply_to_message.from_user.id
            if reply_to_id == MY_USER_ID or reply_to_id == bot_id:
                should_reply = True

    if not should_reply:
        return

    ai_reply = await get_ai_response(msg.text)
    await msg.reply_text(ai_reply)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
