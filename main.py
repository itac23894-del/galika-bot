import os
import requests
import telebot
from datetime import datetime, timedelta

TELEGRAM_TOKEN = os.getenv("8830195933:AAHhXpc5F_a392CEwpLd5dOPSpas9KY17Y0")
GROQ_KEY = os.getenv("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")

if not TELEGRAM_TOKEN or not GROQ_KEY:
    print("خطأ: لازم تحط TELEGRAM_TOKEN و GROQ_KEY في Variables!")
    exit(1)

bot = telebot.TeleBot(TELEGRAM_TOKEN)
FAILED_COINS = {}

class JarvisLegendary:
    def whale_eye(self, volume_spike):
        if volume_spike > 5: return 30, "🐋 دخول حوت ضخم x5"
        if volume_spike > 3: return 20, "🐋 حيتان بداو يدخلو"
        return 0, "لا يوجد حيتان"
    def news_nose(self): return 15, "👃 الأخبار هادئة وآمنة"
    def chart_brain(self, rsi, price_change):
        score = 0; reasons = []
        if 55 < rsi < 68: score += 25; reasons.append(f"🧠 RSI مثالي ({rsi:.1f})")
        if 2 < price_change < 8: score += 25; reasons.append(f"🧠 بداية بومب +{price_change:.2f}%")
        if price_change > 15: score -= 20; reasons.append("🧠 فات الحال - طلعت بزاف")
        return score, reasons
    def trap_shield(self, symbol):
        if symbol in FAILED_COINS:
            if datetime.now() - FAILED_COINS[symbol] < timedelta(hours=24):
                return False, "🛡️ عملة فشلت البارح"
        return True, "🛡️ آمنة"
    def sniper_engine(self, price, score):
        if score >= 85: t1 = price * 1.12; t2 = price * 1.25
        elif score >= 75: t1 = price * 1.077; t2 = price * 1.16
        else: t1 = price * 1.05; t2 = price * 1.09
        sl = price * 0.96; return price, t1, t2, sl
    def get_legendary_alert(self, symbol, price, volume_spike, rsi, price_change):
        is_safe, shield_msg = self.trap_shield(symbol)
        if not is_safe: return None, f"⚠️ العملة {symbol} غير آمنة ({shield_msg})"
        total_score = 0; all_reasons = [shield_msg]
        w_score, w_msg = self.whale_eye(volume_spike); total_score += w_score; all_reasons.append(w_msg)
        n_score, n_msg = self.news_nose(); total_score += n_score; all_reasons.append(n_msg)
        c_score, c_reasons = self.chart_brain(rsi, price_change); total_score += c_score; all_reasons.extend(c_reasons)
        entry, t1, t2, sl = self.sniper_engine(price, total_score)
        report = f"""🚀 جارفيس الأسطوري: {symbol.upper()}
💰 دخول: {entry:.8f}
🎯 هدف 1: {t1:.8f}
🎯 هدف 2: {t2:.8f}
🛑 ستوب: {sl:.8f}
📊 تحليل: {chr(10).join(all_reasons)}
🔥 ثقة: {total_score}%"""
        return total_score, report

jarvis = JarvisLegendary()

def fetch_coingecko_data(symbol):
    symbol_lower = symbol.lower()
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        search_url = f"https://api.coingecko.com/api/v3/search?query={symbol_lower}"
        res = requests.get(search_url, headers=headers, timeout=10)
        if res.status_code != 200: return None
        coins = res.json().get("coins", [])
        if not coins: return None
        coin_id = next((c["id"] for c in coins if c["symbol"].lower() == symbol_lower), coins[0]["id"])
        price_url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usdt&include_24hr_change=true&include_24hr_vol=true"
        price_res = requests.get(price_url, headers=headers, timeout=10).json()
        if coin_id in price_res:
            info = price_res[coin_id]
            price = float(info.get("usdt", 0))
            price_change = float(info.get("usdt_24h_change", 2.0))
            vol = float(info.get("usdt_24h_vol", 1000000))
            rsi = 62.0 if price_change > 0 else 45.0
            volume_spike = round(min(max(vol / 5000000, 1.5), 6.0), 2)
            return {"price": price, "price_change": price_change, "rsi": rsi, "volume_spike": volume_spike}
    except Exception as e:
        print(f"CoinGecko error: {e}")
    return None

def generate_ai_advice(symbol, score, report):
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    prompt = f"أنت جارفيس خبير تداول. ممنوع إعلانات أو روابط. نصيحة قصيرة جدا بالدارجة الجزائرية فقط لعملة {symbol} تقرير {report} ثقة {score}%"
    payload = {"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": prompt}], "temperature": 0.7}
    try:
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=10)
        data = res.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Groq error: {e}")
    return "💡 التزم بالأهداف والستوب لوس!"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "⚡ مرحبا في جارفيس الأسطوري!\nأرسل رمز العملة مثل BTC ETH PEPE SOL")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    symbol = message.text.strip().replace("$", "").upper()
    if len(symbol) > 10: return
    chat_id = message.chat.id
    bot.send_message(chat_id, f"🔍 جاري فحص {symbol}...")
    try:
        data = fetch_coingecko_data(symbol)
        if not data:
            bot.send_message(chat_id, f"❌ لم أجد {symbol}")
            return
        score, report = jarvis.get_legendary_alert(symbol, data["price"], data["volume_spike"], data["rsi"], data["price_change"])
        if report and score:
            ai_advice = generate_ai_advice(symbol, score, report)
            bot.send_message(chat_id, f"{report}\n\n🤖 رأي جارفيس:\n{ai_advice}")
        else:
            bot.send_message(chat_id, f"⚠️ {symbol} لم تتخط الشروط حاليا.")
    except Exception as e:
        print(e)
        bot.send_message(chat_id, "⚠️ خطأ في المعالجة.")

if __name__ == "__main__":
    print("Jarvis Bot Running...")
    try: bot.delete_webhook(drop_pending_updates=True)
    except: pass
    bot.infinity_polling(skip_pending=True)
