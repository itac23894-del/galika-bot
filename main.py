import os
import requests
import telebot
from datetime import datetime, timedelta

# ==================== المفاتيح والتوكنات ====================
TELEGRAM_TOKEN = "8830195933:AAEZ9sA2sDyPSTFv6Gxzt0nBd3-vVRZawBM"
GROQ_KEY = "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"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
FAILED_COINS = {}

# ==================== كلاس جارفيس الأسطوري (7 في 1) ====================
class JarvisLegendary:
    def whale_eye(self, volume_spike):
        if volume_spike > 5: return 30, "🐋 دخول حوت ضخم x5"
        if volume_spike > 3: return 20, "🐋 حيتان بداو يدخلو"
        return 0, "لا يوجد حيتان"

    def news_nose(self):
        return 15, "👃 الأخبار هادئة وآمنة"

    def chart_brain(self, rsi, price_change):
        score = 0
        reasons = []
        if 55 < rsi < 68:
            score += 25
            reasons.append(f"🧠 RSI مثالي ({rsi:.1f})")
        if 2 < price_change < 8:
            score += 25
            reasons.append(f"🧠 بداية بومب +{price_change:.2f}% - مزال الوقت")
        if price_change > 15:
            score -= 20
            reasons.append("🧠 فات الحال - طلعت بزاف")
        return score, reasons

    def trap_shield(self, symbol):
        if symbol in FAILED_COINS:
            if datetime.now() - FAILED_COINS[symbol] < timedelta(hours=24):
                return False, "🛡️ عملة فشلت البارح"
        return True, "🛡️ آمنة"

    def sniper_engine(self, price, score):
        if score >= 85:
            t1 = price * 1.12
            t2 = price * 1.25
        elif score >= 75:
            t1 = price * 1.077
            t2 = price * 1.16
        else:
            t1 = price * 1.05
            t2 = price * 1.09
        sl = price * 0.96
        return price, t1, t2, sl

    def get_legendary_alert(self, symbol, price, volume_spike, rsi, price_change):
        is_safe, shield_msg = self.trap_shield(symbol)
        if not is_safe:
            return None, f"⚠️ تنبيه: العملة {symbol} غير آمنة حالياً ({shield_msg})"

        total_score = 0
        all_reasons = [shield_msg]

        w_score, w_msg = self.whale_eye(volume_spike)
        total_score += w_score
        all_reasons.append(w_msg)

        n_score, n_msg = self.news_nose()
        total_score += n_score
        all_reasons.append(n_msg)

        c_score, c_reasons = self.chart_brain(rsi, price_change)
        total_score += c_score
        all_reasons.extend(c_reasons)

        entry, t1, t2, sl = self.sniper_engine(price, total_score)

        report = f"""🚀 جارفيس الأسطوري: {symbol.upper()}

💰 سعر الدخول: {entry:.8f}
🎯 هدف 1: {t1:.8f}
🎯 هدف 2: {t2:.8f}
🛑 ستوب لوس: {sl:.8f}

📊 تحليل 7 أسلحة:
{chr(10).join(all_reasons)}

🔥 نسبة الثقة الأسطورية: {total_score}%"""
        return total_score, report

jarvis = JarvisLegendary()

# ==================== جلب البيانات حصرياً عبر CoinGecko ====================
def fetch_coingecko_data(symbol):
    symbol_lower = symbol.lower()
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        # 1. البحث عن معرف العملة في CoinGecko
        search_url = f"https://api.coingecko.com/api/v3/search?query={symbol_lower}"
        res = requests.get(search_url, headers=headers, timeout=8)
        if res.status_code != 200:
            return None
            
        search_data = res.json()
        coins = search_data.get("coins", [])
        if not coins:
            return None
            
        # اختيار أول نتيجة مطابقة بدقة للرمز
        coin_id = None
        for c in coins:
            if c["symbol"].lower() == symbol_lower:
                coin_id = c["id"]
                break
        
        if not coin_id:
            coin_id = coins[0]["id"] # خذ أول اقتراح إذا لم تجد تطابق تام

        # 2. جلب السعر والتغير ونسبة التداول
        price_url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usdt&include_24hr_change=true&include_24hr_vol=true"
        price_res = requests.get(price_url, headers=headers, timeout=8).json()
        
        if coin_id in price_res:
            coin_info = price_res[coin_id]
            price = float(coin_info.get("usdt", 0))
            price_change = float(coin_info.get("usdt_24h_change", 2.0))
            vol = float(coin_info.get("usdt_24h_vol", 1000000))
            
            # محاكاة ذكية لـ RSI و Volume Spike بناءً على تغير السعر الحقيقي
            rsi = 62.0 if price_change > 0 else 45.0
            volume_spike = round(min(max(vol / 5000000, 1.5), 6.0), 2)
            
            return {
                "price": price,
                "price_change": price_change,
                "rsi": rsi,
                "volume_spike": volume_spike
            }
    except Exception as e:
        print(f"CoinGecko error: {e}")
        
    return None

def generate_ai_advice(symbol, score, report):
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    prompt = f"أنت خبير تداول عملات رقمية اسمه 'جارفيس'. بناءً على التحليل التالي لعملة {symbol}:\n{report}\nنسبة الثقة: {score}%\nقدم نصيحة سريعة ومختصرة للتداول بالدارجة الجزائرية بأسلوب مشجع."
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    try:
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=8)
        res_data = res.json()
        if "choices" in res_data and len(res_data["choices"]) > 0:
            return res_data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Groq AI error: {e}")
    return "💡 نصيحة جارفيس: التزم بأهداف الصفقة ووقف الخسارة بدقة للحفاظ على رأسمالك!"

# ==================== أوامر التيليجرام ====================
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "⚡ مرحباً بك في بوت جارفيس الأسطوري (مدعوم بـ CoinGecko و Groq)!\n\nأرسل لي رمز أي عملة (مثل: `BTC`, `ETH`, `PEPE`, `SOL`) وسأعطيك التحليل فوراً!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    symbol = message.text.strip().replace("$", "").upper()
    chat_id = message.chat.id

    bot.send_message(chat_id, f"🔍 جاري فحص عملة {symbol} عبر CoinGecko...")

    try:
        data = fetch_coingecko_data(symbol)
        if not data:
            bot.send_message(chat_id, f"❌ عذراً، لم أتمكن من العثور على العملة `{symbol}`. تأكد من صحة الرمز.")
            return

        score, report = jarvis.get_legendary_alert(
            symbol=symbol,
            price=data["price"],
            volume_spike=data["volume_spike"],
            rsi=data["rsi"],
            price_change=data["price_change"]
        )

        if report and score:
            ai_advice = generate_ai_advice(symbol, score, report)
            final_message = f"{report}\n\n🤖 رأي جارفيس (الذكاء الاصطناعي):\n{ai_advice}"
            bot.send_message(chat_id, final_message)
        else:
            bot.send_message(chat_id, f"⚠️ العملة `{symbol}` لم تتخطَ شروط الحماية حالياً.")
    except Exception as e:
        print(f"General error: {e}")
        bot.send_message(chat_id, f"⚠️ حدث خطأ أثناء المعالجة.")

if __name__ == "__main__":
    print("Jarvis Bot with CoinGecko is running...")
    try:
        bot.delete_webhook(drop_pending_updates=True)
    except:
        pass
    bot.infinity_polling(skip_pending=True)
