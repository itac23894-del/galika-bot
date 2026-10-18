import os
import requests
from flask import Flask, request

app = Flask(__name__)

TELEGRAM_TOKEN = "8830195933:AAEZ9sA2sDyPSTFv6Gxzt0nBd3-vVRZawBM"
GROQ_KEY = "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"

PROMPT = 'أنت بوت مراهق وشاب اسمك Galika. تتكلم بالدارجة الجزائرية العفوية. رد دائماً بطريقة قصيرة، فكاهية وممتعة.'

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

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if data and "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"]["text"]
        
        # إرسال الطلب مباشرة لـ Groq API عبر HTTP POST
        try:
            headers = {
                "Authorization": f"Bearer {GROQ_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": PROMPT},
                    {"role": "user", "content": user_text}
                ],
                "temperature": 0.7
            }
            response = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=15)
            res_data = response.json()
            
            if "choices" in res_data:
                reply = res_data["choices"][0]["message"]["content"]
            else:
                print("Groq Error Response:", res_data)
                reply = "يا خويا كاين ضغط في السيرفر تاع Groq، عاود جرب."
        except Exception as e:
            print(f"HTTP Request Error: {e}")
            reply = "راسك خشين يا خويا، ماقدرتش نتصل بالذكاء الاصطناعي!"
            
        send_telegram_message(chat_id, reply)
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    
    railway_url = os.getenv("RAILWAY_STATIC_URL") or os.getenv("RAILWAY_PUBLIC_DOMAIN")
    if railway_url:
        if not railway_url.startswith("http"):
            railway_url = f"https://{railway_url}"
        webhook_url = f"{railway_url}/{TELEGRAM_TOKEN}"
        set_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={webhook_url}"
        try:
            requests.get(set_url, timeout=10)
        except Exception as e:
            print("Webhook set error:", e)

    app.run(host="0.0.0.0", port=port)
