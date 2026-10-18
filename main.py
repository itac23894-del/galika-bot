import os
import requests
from flask import Flask, request
from openai import OpenAI

app = Flask(__name__)

# التوكن ومفتاح Groq مدرجون مباشرة هنا
TELEGRAM_TOKEN = "8830195933:AAEZ9sA2sDyPSTFv6Gxzt0nBd3-vVRZawBM"
GROQ_KEY = "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"

# إعداد عميل Groq
client = OpenAI(
    api_key=GROQ_KEY,
    base_url="https://api.groq.com/openai/v1"
)
MODEL = "llama-3.1-8b-instant"

# شخصية Galika مراهق جزائري يتحدث بعفوية وحماس
PROMPT = (
    'أنت بوت مراهق وشاب اسمك Galika. تتكلم بالدارجة الجزائرية العفوية جداً تاع الشوارع والشباب. '
    'أسلوبك فكاهي، ذكي، حنون، وشوية فوضوي. استخدم أحياناً عبارات مثل "يا خويا"، "واش راك"، "سجلت كلامك في راسي"، '
    'و "أعالج هذا الشعور". رد بطريقة شبابية، قصيرة وممتعة وكأنك صديق مقرب.'
)

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error sending message: {e}")

@app.route("/", methods=["GET"])
def home():
    return "Galika Bot is alive!", 200

# مسار استقبال الرسائل من تيليجرام والتحدث مع المستخدم
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if data and "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"]["text"]
        
        try:
            completion = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": PROMPT},
                    {"role": "user", "content": user_text}
                ],
                temperature=0.8
            )
            reply = completion.choices[0].message.content
        except Exception as e:
            print(f"Groq API Error: {e}")
            reply = "يا خويا صرا كفاش في السيستم، عاود جرب بعد قليل."
            
        send_telegram_message(chat_id, reply)
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    
    # ربط الـ Webhook تلقائياً أول ما يشتعل السيرفر
    railway_url = os.getenv("RAILWAY_STATIC_URL") or os.getenv("RAILWAY_PUBLIC_DOMAIN")
    if railway_url:
        if not railway_url.startswith("http"):
            railway_url = f"https://{railway_url}"
        webhook_url = f"{railway_url}/{TELEGRAM_TOKEN}"
        set_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={webhook_url}"
        try:
            r = requests.get(set_url, timeout=10)
            print("Auto-set Webhook Response:", r.text)
        except Exception as e:
            print("Failed to auto-set webhook:", e)

    app.run(host="0.0.0.0", port=port)
