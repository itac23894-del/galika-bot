import os
import logging
from openai import OpenAI
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# إعداد تتبع الأخطاء في السجلات
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# جلب المتغيرات من Railway بأمان
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")

# إعداد عميل Groq للنموذج السريع
client = OpenAI(
    api_key=GROQ_KEY,
    base_url="https://api.groq.com/openai/v1"
)
MODEL = "llama-3.1-8b-instant"

# شخصية Galika الذكية والحنينة بالدارجة الجزائرية
PROMPT = (
    'أنت Galika، مساعد ذكي ومقرب يتحدث بدارجة جزائرية حنينة وذكية جداً. '
    'استخدم أحياناً عبارات مثل "انتظر... أعالج هذا الشعور..." و "سجلت كلامك في النواة تاعي..." '
    'وكن دائماً لطيفاً ومفيداً في ردودك.'
)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_text = update.message.text
    logger.info(f"استقبلت رسالة: {user_text}")

    try:
        # إرسال الرسالة إلى نموذج Groq
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": user_text}
            ],
            temperature=0.7,
            max_tokens=600
        )
        
        reply = completion.choices[0].message.content
        await update.message.reply_text(reply)

    except Exception as e:
        logger.error(f"خطأ أثناء الاتصال بـ Groq: {e}")
        await update.message.reply_text("سامحني يا خويا، صرا طراوة صغيرة في المعالجة، عاود ابعثلي برك.")

def main():
    if not TELEGRAM_TOKEN or not GROQ_KEY:
        logger.error("المتغيرات (Tokens) غير مخزنة بشكل صحيح!")
        return

    print("جاري تشغيل بوت Galika...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # معالجة الرسائل النصية فقط وتجاهل الأوامر
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # بدء تشغيل البوت مع تجاهل الرسائل العالقة القديمة
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
