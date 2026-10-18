import os
from openai import OpenAI
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8830195933:AAGSfxWfuLkTu_4r_0GiHpjOMdYbupR4s34")
OPENAI_KEY = os.getenv("GROQ_API_KEY", "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")

if OPENAI_KEY and OPENAI_KEY.startswith("gsk_"):
    client = OpenAI(api_key=OPENAI_KEY, base_url="https://api.groq.com/openai/v1")
    MODEL = "llama-3.1-8b-instant"
else:
    client = OpenAI(api_key=OPENAI_KEY)
    MODEL = "gpt-4o-mini"

PROMPT = 'أنت Galika. تقولي "انتظر... أعالج هذا الشعور..." و "سجلت كلامك في النواة تاعي..." دارجة جزائرية حنينة وذكية.'

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": update.message.text}
        ]
    )
    await update.message.reply_text(completion.choices[0].message.content)

if __name__ == "__main__":
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    print("Bot is running...")
    app.run_polling()
