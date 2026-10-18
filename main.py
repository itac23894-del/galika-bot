import os
import requests
from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

# بيانات الاعتماد
TELEGRAM_TOKEN = "8830195933:AAEZ9sA2sDyPSTFv6Gxzt0nBd3-vVRZawBM"
GROQ_KEY = "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"

SYSTEM_PROMPT = (
    "أنت خبير محترف ومحلل دقيق في مباريات كرة القدم والرهانات الرياضية. "
    "قدّم تحليلاً واقعياً يتماشى مع أحدث مستويات الفرق، التشكيلات الحالية، والغيابات.\n"
    "يتضمن تحليلك:\n"
    "1. الفريق الأقرب للفوز ونسبة الاحتمال.\n"
    "2. توقع الأهداف (Over/Under).\n"
    "3. الركنيات والبطاقات.\n"
    "4. نصيحة الرهان الذكية (Betting Tip).\n"
    "أجب بأسلوب رياضي ممتع بالدارجة الجزائرية أو العربية."
)

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        r = requests.post(url, json=payload, timeout=10)
        print("Telegram Response Status:", r.status_code)
    except Exception as e:
        print(f"Error sending to Telegram: {e}")

@app.route("/", methods=["GET"])
def home():
    return "Football Analysis Bot is Live!", 200

# مسار لتفعيل Webhook يدوي
@app.route("/set_webhook", methods=["GET"])
def set_webhook_manual():
    domain = os.getenv("RAILWAY_PUBLIC_DOMAIN") or os.getenv("RAILWAY_STATIC_URL")
    if domain:
        if not domain.startswith("http"):
            domain = f"https://{domain}"
        webhook_url = f"{domain}/{TELEGRAM_TOKEN}"
        set_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={webhook_url}"
        r = requests.get(set_url, timeout=10)
        return f"Webhook Status: {r.text}", 200
    return "Domain environment variable not found!", 400

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)
    if not data:
        return "No Data", 400

    print("Received Webhook Payload:", data)

    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"]["text"]

        headers = {
            "Authorization": f"Bearer {GROQ_KEY}",
            "Content-Type": "application/json"
        }
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"تاريخ اليوم {current_date}. أعطني تحليل لمباراة: {user_text}"}
            ],
            "temperature": 0.7
        }

        try:
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=15)
            res_data = res.json()
            
            if "choices" in res_data and len(res_data["choices"]) > 0:
                reply = res_data["choices"][0]["message"]["content"]
            else:
                err_msg = res_data.get("error", {}).get("message", "Unknown API error")
                reply = f"مشكل في API الذكاء الاصطناعي: {err_msg}"
        except Exception as e:
            reply = f"مشكل في الاتصال بالسيرفر: {str(e)}"

        send_telegram_message(chat_id, reply)

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    
    # تفعيل الـ Webhook تلقائياً عند التشغيل
    domain = os.getenv("RAILWAY_PUBLIC_DOMAIN") or os.getenv("RAILWAY_STATIC_URL")
    if domain:
        if not domain.startswith("http"):
            domain = f"https://{domain}"
        webhook_url = f"{domain}/{TELEGRAM_TOKEN}"
        set_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={webhook_url}"
        try:
            r = requests.get(set_url, timeout=10)
            print("Auto-set Webhook Response:", r.text)
        except Exception as e:
            print("Webhook Auto Set Error:", e)

    app.run(host="0.0.0.0", port=port)
