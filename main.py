import os
import logging
from openai import OpenAI
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# إعداد تتبع الأخطاء في السجلات
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# جلب المتغيرات من Railway
TELEGRAM_TOKEN = os.getenv("8830195933:AAEZ9sA2sDyPSTFv6Gxzt0nBd3-vVRZawBM")
GROQ_KEY = os.getenv("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")

# إعداد عميل Groq
client = OpenAI(
    api_key=GROQ_KEY,
    base_url="https://api.groq.com/openai/v1"
)
MODEL = "llama-3.1-8b-instant"

PROMPT = (
    'أنت Galika. تتكلم بدارجة جزائرية حنينة وذكية جداً. '
    'استخدم أحياناً عبارات مثل "انتظر... أعالج هذا الشعور..." و "سجلت كلامك في النواة تاعي..."'
)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_text = update.message.text
    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": user_text}
            ],
            temperature=0.7
        )
        reply = completion.choices[0].message.content
        await update.message.reply_text(reply)
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("عذراً، حدث خطأ مؤقت في المعالجة.")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # تشغيل البوت مع تجاوز الرسائل القديمة المعلقة
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
