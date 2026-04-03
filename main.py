from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import aiohttp

# ========== 我已经帮你填好 ==========
BOT_TOKEN = "8759872051:AAEtPVCsQq-uNtrOkOfGhb3baXOapNzr91w"
YOUR_TG_ID = 8475704328
AI_API_KEY = "sk-d2509e77f1b54821bb6f4b604ea3ef05"
# ==================================

AI_URL = "https://api.deepseek.com/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {AI_API_KEY}",
    "Content-Type": "application/json"
}

async def get_ai_reply(text: str) -> str:
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一个高智商、逻辑严谨、思维深度强、说话自然聪明的AI助手，回答简洁不啰嗦"},
            {"role": "user", "content": text}
        ],
        "temperature": 0.8
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(AI_URL, headers=HEADERS, json=payload) as resp:
                res = await resp.json()
                return res["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return "我思考一下，请稍等…"

async def auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if not message or not user:
        return

    is_mention_me = False

    # 群里 @ 你
    if message.entities:
        for ent in message.entities:
            if ent.type == "mention":
                is_mention_me = True

    # 回复你的消息
    if message.reply_to_message:
        if message.reply_to_message.from_user.id == YOUR_TG_ID:
            is_mention_me = True

    if not is_mention_me:
        return

    text = message.text or ""
    if not text:
        return

    reply = await get_ai_reply(text)
    await message.reply_text(reply)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_reply))
    app.run_polling()

if __name__ == "__main__":
    main()
