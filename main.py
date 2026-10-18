import os
import requests
from flask import Flask, request
from openai import OpenAI

app = Flask(__name__)

# جلب المفاتيح من Railway
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

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

@app.route("/", methods=["GET"])
def home():
    return "Galika Bot is alive!", 200

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"]["text"]
        
        try:
            # الرد عبر Groq
            completion = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": PROMPT},
                    {"role": "user", "content": user_text}
                ],
                temperature=0.7
            )
            reply = completion.choices[0].message.content
        except Exception as e:
            reply = "سامحني يا خويا، صرا طراوة صغيرة في المعالجة."
            
        send_telegram_message(chat_id, reply)
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
