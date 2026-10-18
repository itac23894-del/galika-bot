import os
import logging
from openai import OpenAI
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# إعداد التتبع لمعرفة أسباب أي خطأ في Railway Logs
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# جلب المفاتيح والمتغيرات
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8830195933:AAEZ9sA2sDyPSTFv6Gxzt0nBd3-vVRZawBM")
GROQ_KEY = os.getenv("GROQ_API_KEY", "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")

# إعداد عميل Groq عبر مكتبة OpenAI
client = OpenAI(
    api_key=GROQ_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# نموذج Llama السريع جداً من Groq
MODEL = "llama-3.1-8b-instant"

# التعليمات الخاصة بالبوت Galika
PROMPT = (
    'أنت Galika. تتكلم بدارجة جزائرية حنينة وذكية جداً. '
    'استخدم أحياناً عبارات مثل "انتظر... أعالج هذا الشعور..." و "سجلت كلامك في النواة تاعي..."'
)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_text = update.message.text
    print(f"وصلت رسالة جديدة: {user_text}")

    try:
        # إرسال النص إلى Groq
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": user_text}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        reply = completion.choices[0].message.content
        await update.message.reply_text(reply)

    except Exception as e:
        print(f"حدث خطأ أثناء الاتصال بـ Groq: {e}")
        await update.message.reply_text("آسف يا خويا، حدث خطأ بسيط أثناء معالجة الطلب، حاول مرة ثانية!")

def main():
    print("جاري تشغيل البوت...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # إضافة معالج الرسائل النصية
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # تشغيل البوت وإلغاء أي رسائل قديمة كانت معلقة
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
