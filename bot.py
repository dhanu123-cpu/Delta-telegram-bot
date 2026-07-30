import os
import threading
from flask import Flask

app = Flask(_name_)

@app.route('/')
def home():
    return "Bot is live!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_flask, daemon=True).start()import time
import requests
import pandas as pd

BOT_TOKEN = "8380158711:AAHDYOV81IJVsnQkNaQfa7yqk0VeOEFmpxo"
CHAT_ID = "7755539827"
TIMEFRAME = "5m"

def send_telegram_signal(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        res = requests.post(url, json=payload)
        if res.status_code == 200:
            print("Signal sent to Telegram successfully!")
        else:
            print("Telegram Error:", res.json())
    except Exception as e:
        print("Error sending signal:", e)

def fetch_delta_candles():
    end_time = int(time.time())
    start_time = end_time - (100 * 300)
    
    symbols_to_try = ["BTCUSD", "BTC_USDT"]
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    for symbol in symbols_to_try:
        url = f"https://api.delta.exchange/v2/history/candles?symbol={symbol}&resolution={TIMEFRAME}&start={start_time}&end={end_time}"
        try:
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                data_json = res.json()
                result = data_json.get("result", [])
                if data_json.get("success") and len(result) > 0:
                    df = pd.DataFrame(result)

                    if 'close' in df.columns:
                        pass
                    elif 'c' in df.columns:
                        df = df.rename(columns={'c': 'close', 'h': 'high', 'l': 'low', 'o': 'open'})
                    elif len(df.columns) >= 5 and isinstance(df.columns[0], int):
                        df = df.rename(columns={1: 'open', 2: 'high', 3: 'low', 4: 'close'})

                    df['close'] = df['close'].astype(float)
                    df['high'] = df['high'].astype(float)
                    df['low'] = df['low'].astype(float)
                    df['open'] = df['open'].astype(float)

                    df = df.iloc[::-1].reset_index(drop=True)
                    return df, symbol
        except Exception as e:
            print("Error fetching candles:", e)
            
    print("API returned empty data state for all symbols")
    return None, "BTCUSD"

def check_strategy():
    df, active_symbol = fetch_delta_candles()
    if df is None or len(df) < 30:
        return

    df['ema9'] = df['close'].ewm(span=9, adjust=False).mean()
    df['ema20'] = df['close'].ewm(span=20, adjust=False).mean()

    c3 = df.iloc[-4]
    c2 = df.iloc[-3]
    c1 = df.iloc[-2]

    # SELL STRATEGY
    cross_down = (c3['ema9'] > c3['ema20']) and (c2['ema9'] < c2['ema20'])
    retest_bearish = c2['high'] >= c2['ema9']
    is_red_c1 = c1['close'] < c1['open']

    if cross_down and retest_bearish and is_red_c1:
        msg = f"🔻 <b>DELTA SELL SIGNAL ({active_symbol})</b> 🔻\n\n• <b>Strategy:</b> 9/20 EMA Cross Down + Retest + Red Confirmation\n• <b>Price:</b> ${c1['close']}\n• <b>Timeframe:</b> {TIMEFRAME}"
        send_telegram_signal(msg)

    # BUY STRATEGY
    cross_up = (c3['ema9'] < c3['ema20']) and (c2['ema9'] > c2['ema20'])
    retest_bullish = c2['low'] <= c2['ema9']
    is_green_c1 = c1['close'] > c1['open']

    if cross_up and retest_bullish and is_green_c1:
        msg = f"🚀 <b>DELTA BUY SIGNAL ({active_symbol})</b> 🚀\n\n• <b>Strategy:</b> 9/20 EMA Cross Up + Retest + Green Confirmation\n• <b>Price:</b> ${c1['close']}\n• <b>Timeframe:</b> {TIMEFRAME}"
        send_telegram_signal(msg)

print("EMA Crossover Strategy Bot Running 24/7...")
while True:
    try:
        check_strategy()
    except Exception as e:
        print("Loop Error:", e)
    time.sleep(60)
