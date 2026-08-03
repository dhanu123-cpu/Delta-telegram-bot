import os
import time
import requests
import pandas as pd
import numpy as np
from threading import Thread
from flask import Flask
app = Flask(__name__)
# Telegram & Trading Configuration
BOT_TOKEN = "8380158711:AAG31v0UNc1L-Aw_qNAiOMoMUF2FQAQkvb0"
CHAT_ID = "7755539827"
TIMEFRAMES = ["1m", "3m", "5m", "15m", "30m", "60m"]
SYMBOL = "BTCUSDT"
@app.route('/')
def home():
    return "EMA Crossover Bot is running 24/7!"
def send_telegram_signal(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        print("Telegram Response:", response.status_code)
    except Exception as e:
        print("Telegram Send Error:", e)

def fetch_candles(timeframe):
    url = f"https://api.delta.exchange/v2/history/candles?resolution={timeframe}&symbol={SYMBOL}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get("success") and "result" in data:
            df = pd.DataFrame(data["result"], columns=["time", "open", "high", "low", "close", "volume"])
            df["close"] = df["close"].astype(float)
            df = df.sort_values("time").reset_index(drop=True)
            return df
    except Exception as e:
        print(f"API Error for {timeframe}:", e)
    return None

def check_strategy(tf):
    # Yahan pe data fetch hota hoga (jaise df = ...)
    
    # Ye variables function ke andar hone chahiye:
    c2 = df.iloc[-2]
    c1 = df.iloc[-1]
    
    cross_up = (c2['ema9'] < c2['ema20']) and (c1['ema9'] >= c1['ema20'])
    cross_down = (c2['ema9'] > c2['ema20']) and (c1['ema9'] <= c1['ema20'])
    
    if cross_up:
        msg = f"🟢 <b>DELTA BUY SIGNAL ({SYMBOL})</b>\n⏱️ Timeframe: <b>{tf}</b>\n📈 EMA 9 Crossed Above EMA 20\n💰 Price: {c1['close']}"
        send_telegram_signal(msg)

    if cross_down:
        msg = f"🔴 <b>DELTA SELL SIGNAL ({SYMBOL})</b>\n⏱️ Timeframe: <b>{tf}</b>\n📉 EMA 9 Crossed Below EMA 20\n💰 Price: {c1['close']}"
        send_telegram_signal(msg)
def run_trading_bot():
    print("EMA Crossover Strategy Bot Running 24/7...")
    send_telegram_signal("🤖 Test Alert: EMA Crossover Bot is successfully online and monitoring markets!")
    
    while True:
        try:
            for tf in TIMEFRAMES:
                check_strategy(tf)
                time.sleep(2)
        except Exception as e:
            print("Loop Error:", e)
        time.sleep(10)
if __name__ == "__main__":
    bot_thread = Thread(target=run_trading_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
