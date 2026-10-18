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
    
    # سلاح 1: عين الحوت 🐋
    def whale_eye(self, symbol, volume_spike):
        if volume_spike > 5: return 30, "🐋 دخول حوت ضخم x5"
        if volume_spike > 3: return 20, "🐋 حيتان بداو يدخلو"
        return 0, "لا يوجد حيتان"

    # سلاح 2: أنف الأخبار 👃
    def news_nose(self, symbol):
        try:
            url = f"https://api.coingecko.com/api/v3/coins/{symbol.lower()}"
            headers = {"User-Agent": "Mozilla/5.0"}
            requests.get(url, headers=headers, timeout=3)
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

    # ===== التحليل الأسطوري =====
    def get_legendary_alert(self, symbol, price, volume_spike, rsi, price_change):
        is_safe, shield_msg = self.trap_shield(symbol)
        if not is_safe:
            return None, f"⚠️ **تنبيه:** العملة `{symbol}` غير آمنة حالياً ({shield_msg})"

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
        return total_score, report

jarvis = JarvisLegendary()

# ==================== جلب البيانات من Binance ====================
def fetch_binance_data(symbol):
    symbol_usdt = f"{symbol.upper()}USDT"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        ticker_url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol_usdt}"
        res = requests.get(ticker_url, headers=headers, timeout=8)
        ticker_res = res.json()
        
        if not isinstance(ticker_res, dict) or "lastPrice" not in ticker_res:
            return None

        price = float(ticker_res["lastPrice"])
        price_change = float(ticker_res["priceChangePercent"])

        klines_url = f"https://api.binance.com/api/v3/klines?symbol={symbol_usdt}&interval=1h&limit=15"
        klines_res = requests.get(klines_url, headers=headers, timeout=8).json()
        
        if isinstance(klines_res, list) and len(klines_res) > 1:
            closes = [float(k[4]) for k in klines_
