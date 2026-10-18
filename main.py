import os
from openai import OpenAI
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# جلب التوكن والمفتاح من البيئة بأمان
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8830195933:AAEZ9sA2sDyPSTFv6Gxzt0nBd3-vVRZawBM")
OPENAI_KEY = os.environ.get("OPENAI_KEY", "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")

# إعداد عميل Groq
if OPENAI_KEY and OPENAI_KEY.startswith("gsk_"):
    client = OpenAI(api_key=OPENAI_KEY, base_url="https://api.groq.com/openai/v1")
    MODEL = "llama-3.1-8b-instant"
else:
    client = OpenAI(api_key=OPENAI_KEY)
    MODEL = "gpt-4o-mini"

PROMPT = """أنت Galika، مساعد ذكي بشخصية دافئة وحنينة تتحدث بالدارجة الجزائرية اللطيفة والذكية."""

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    sent_message = await update.message.reply_text("انتظر... أعالج هذا الشعور...")

    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": update.message.text}
            ]
        )
        
        bot_reply = completion.choices[0].message.content
        final_response = f"سجلت كلامك في النواة تاعي...\n\n{bot_reply}"
        await sent_message.edit_text(final_response)

    except Exception as e:
        await sent_message.edit_text("عذراً، حدث خطأ أثناء معالجة الطلب.")
        print(f"Error: {e}")

def main():
    print("Bot is running...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.run_polling()

if __name__ == "__main__":
    main()
