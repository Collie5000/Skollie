import requests
from datetime import datetime, timezone

URL = "https://api.exchange.coinbase.com/products/BTC-USD/candles"

params = {"granularity": 300}
headers = {"User-Agent": "Skollie-BTC-Signal/1.0"}

response = requests.get(
    URL, params=params, headers=headers, timeout=20
)
response.raise_for_status()

candles = response.json()

if not isinstance(candles, list) or len(candles) < 50:
    raise ValueError("Not enough BTC candle data received")

# Coinbase format: time, low, high, open, close, volume
candles = sorted(candles, key=lambda candle: candle[0])
closes = [float(candle[4]) for candle in candles]
price = closes[-1]

def moving_average(values, period):
    return sum(values[-period:]) / period

ma20 = moving_average(closes, 20)
ma50 = moving_average(closes, 50)

changes = [
    closes[i] - closes[i - 1]
    for i in range(len(closes) - 14, len(closes))
]

gains = [max(change, 0) for change in changes]
losses = [max(-change, 0) for change in changes]

avg_gain = sum(gains) / 14
avg_loss = sum(losses) / 14

if avg_loss == 0:
    rsi = 100.0 if avg_gain > 0 else 50.0
else:
    rsi = 100 - (100 / (1 + avg_gain / avg_loss))

if ma20 > ma50 and rsi > 50:
    signal = "BUY"
elif ma20 < ma50 and rsi < 50:
    signal = "SELL"
else:
    signal = "HOLD"

report = (
    f"BTC-USD Signal Check (UTC): "
    f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}\n"
    f"Price: ${price:,.2f} USD\n"
    f"MA20: ${ma20:,.2f}\n"
    f"MA50: ${ma50:,.2f}\n"
    f"RSI14: {rsi:.2f}\n"
    f"Signal: {signal}\n"
    "Mode: SIGNAL ONLY - NO LIVE TRADES\n"
    "Warning: Indicators are not guaranteed predictions.\n"
)

print(report)

with open("btc_signal_report.txt", "w", encoding="utf-8") as file:
    file.write(report)
