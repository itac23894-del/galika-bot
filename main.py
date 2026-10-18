import os
import requests
from flask import Flask, request

app = Flask(__name__)

# 1. توكن البوت تاعك
TELEGRAM_TOKEN = "8830195933:AAEZ9sA2sDyPSTFv6Gxzt0nBd3-vVRZawBM"

# 2. حط مفتاح Groq الجديد اللي خرجتو دوك هنا
GROQ_KEY = "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"

# البرومبت الخاص بشخصية Galika (شاب/مراهق جزائري عفوي وذكي)
SYSTEM_PROMPT = (
    "أنت Galika، روبوت بشخصية شاب ومراهق جزائري عفوي وذكي جداً. "
    "تتكلم بالدارجة الجزائرية العفوية تاع الشباب والشوارع. "
    "أسلوبك فكاهي، حنون، شوية فوضوي وممتع. "
    "استخدم عبارات مثل: 'يا خويا'، 'واش راك'، 'سجلت كلامك في راسي'، 'أعالج هذا الشعور'. "
    "جاوب دايماً بدارجة جزائرية قصيرة، متجددة ومباشرة بدون رسميات."
)

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error sending to Telegram: {e}")

@app.route("/", methods=["GET"])
def home():
    return "Galika AI is Running!", 200

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if data and "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"]["text"]

        # إرسال النص للذكاء الاصطناعي (Groq Llama 3.1)
        headers = {
            "Authorization": f"Bearer {GROQ_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
            "temperature": 0.8
        }

        try:
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=12)
            res_data = res.json()
            
            if "choices" in res_data and len(res_data["choices"]) > 0:
                reply = res_data["choices"][0]["message"]["content"]
            else:
                print("API Response Error:", res_data)
                reply = "يا خويا مفتاح Groq راه فيه مشكل ولا كاين ضغط، بدل المفتاح!"
        except Exception as e:
            print(f"Network Error: {e}")
            reply = "صرا انقطاع صغير في التلكوم، عاود ابعتلي يا خويا."

        send_telegram_message(chat_id, reply)

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))

    # تسجيل الـ Webhook تلقائياً في Railway
    railway_url = os.getenv("RAILWAY_STATIC_URL") or os.getenv("RAILWAY_PUBLIC_DOMAIN")
    if railway_url:
        if not railway_url.startswith("http"):
            railway_url = f"https://{railway_url}"
        webhook_url = f"{railway_url}/{TELEGRAM_TOKEN}"
        set_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={webhook_url}"
        try:
            requests.get(set_url, timeout=10)
        except Exception as e:
            print("Webhook Auto Set Error:", e)

    app.run(host="0.0.0.0", port=port)
