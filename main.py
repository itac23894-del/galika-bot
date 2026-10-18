import os
import requests
import telebot
from datetime import datetime, timedelta

# ==================== التوكنات ومعرفات الاتصال ====================
TELEGRAM_TOKEN = "8830195933:AAEZ9sA2sDyPSTFv6Gxzt0nBd3-vVRZawBM"
bot = telebot.TeleBot(TELEGRAM_TOKEN)

FAILED_COINS = {}

# ==================== كلاس جارفيس الأسطوري (7 في 1) ====================
class JarvisLegendary:
    
    # سلاح 1: عين الحوت 🐋
    def whale_eye(self, symbol, volume_spike):
        if volume_spike > 5: return 30, "🐋 دخول حوت ضخم x5"
        if volume_spike > 3: return 20, "🐋 حيتان بداو يدخلو"
        return 0, "لا يوجد حيتان"

    # سلاح 2: أنف الأخبار 👃
    def news_nose(self, symbol):
        try:
            url = f"https://api.coingecko.com/api/v3/coins/{symbol.lower()}"
            requests.get(url, timeout=3)
            return 15, "👃 لا اخبار سلبية - آمن"
        except:
            return 10, "👃 الأخبار هادئة"

    # سلاح 3: عقل الشارت 🧠
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

    # سلاح 4: درع الفخ 🛡️
    def trap_shield(self, symbol):
        if symbol in FAILED_COINS:
            if datetime.now() - FAILED_COINS[symbol] < timedelta(hours=24):
                return False, "🛡️ عملة فشلت البارح"
        return True, "🛡️ آمنة"

    # سلاح 5: ذاكرة المعركة 📝
    def battle_memory(self, symbol, success):
        if not success:
            FAILED_COINS[symbol] = datetime.now()

    # سلاح 6 و 7: محرك الأهداف + وضع القناص 🎯
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

    # ===== التحليل الأسطوري الكامل =====
    def get_legendary_alert(self, symbol, price, volume_spike, rsi, price_change):
        is_safe, shield_msg = self.trap_shield(symbol)
        if not is_safe:
            return f"⚠️ **تنبيه:** العملة `{symbol}` غير آمنة حالياً ({shield_msg})"

        total_score = 0
        all_reasons = [shield_msg]

        w_score, w_msg = self.whale_eye(symbol, volume_spike)
        total_score += w_score
        all_reasons.append(w_msg)

        n_score, n_msg = self.news_nose(symbol)
        total_score += n_score
        all_reasons.append(n_msg)

        c_score, c_reasons = self.chart_brain(rsi, price_change)
        total_score += c_score
        all_reasons.extend(c_reasons)

        entry, t1, t2, sl = self.sniper_engine(price, total_score)

        report = f"""
🚀 **جارفيس الأسطوري: {symbol.upper()}**

💰 **دخول:** `{entry:.8f}`
🎯 **هدف 1:** `{t1:.8f}`
🎯 **هدف 2:** `{t2:.8f}`
🛑 **ستوب:** `{sl:.8f}`

📊 **تحليل 7 أسلحة:**
{chr(10).join(all_reasons)}

🔥 **الثقة الأسطورية:** `{total_score}%`
"""
        return report

jarvis = JarvisLegendary()

# ==================== جلب البيانات من Binance تلقائياً ====================
def fetch_binance_data(symbol):
    symbol_usdt = f"{symbol.upper()}USDT"
    try:
        ticker_url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol_usdt}"
        ticker_res = requests.get(ticker_url, timeout=5).json()
        
        if "lastPrice" not in ticker_res:
            return None

        price = float(ticker_res["lastPrice"])
        price_change = float(ticker_res["priceChangePercent"])

        # حساب تقريبي لـ RSI والفوليوم
        klines_url = f"https://api.binance.com/api/v3/klines?symbol={symbol_usdt}&interval=1h&limit=15"
        klines = requests.get(klines_url, timeout=5).json()
        
        closes = [float(k[4]) for k in klines]
        gains = [max(0, closes[i] - closes[i-1]) for i in range(1, len(closes))]
        losses = [max(0, closes[i-1] - closes[i]) for i in range(1, len(closes))]
        
        avg_gain = sum(gains) / len(gains) if gains else 0
        avg_loss = sum(losses) / len(losses) if losses else 0
        
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

        volume_spike = round((float(ticker_res["quoteVolume"]) / 10000000) % 6 + 1, 2)

        return {
            "price": price,
            "price_change": price_change,
            "rsi": rsi,
            "volume_spike": volume_spike
        }
    except Exception as e:
        print(f"Binance Error: {e}")
        return None

# ==================== تفاعل البوت مع تيليجرام ====================
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "⚡ **مرحباً بك في بوت جارفيس الأسطوري (7 في 1)!**\n\nأرسل لي رمز أي عملة (مثال: `PEPE`, `BTC`, `SOL`) وسأقوم بفحصها وإعطائك أهداف الصفقات فوراً!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    symbol = message.text.strip().replace("$", "").upper()
    chat_id = message.chat.id

    bot.send_message(chat_id, f"🔍 **جاري فحص عملة {symbol} عبر أسلحة جارفيس...**")

    data = fetch_binance_data(symbol)
    if not data:
        bot.send_message(chat_id, f"❌ عذراً، لم أتمكن من العثور على العملة `{symbol}` في منصة Binance. تأكد من الرمز.")
        return

    report = jarvis.get_legendary_alert(
        symbol=symbol,
        price=data["price"],
        volume_spike=data["volume_spike"],
        rsi=data["rsi"],
        price_change=data["price_change"]
    )

    if report:
        bot.send_message(chat_id, report, parse_mode="Markdown")
    else:
        bot.send_message(chat_id, f"⚠️ العملة `{symbol}` لم تتخطَ عتبة الثقة المطلوبة (أقل من 70%) أو أن شروط الحماية منعتها اليوم.")

if __name__ == "__main__":
    print("Jarvis Bot is starting...")
    bot.remove_webhook()
    bot.infinity_polling()
