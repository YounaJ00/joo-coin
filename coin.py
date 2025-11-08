import os
from dotenv import load_dotenv
load_dotenv()

import pyupbit
df = pyupbit.get_ohlcv("KRW-BTC", count = 30, interval = "day")

from openai import OpenAI
client = OpenAI()

response = client.chat.completions.create(
  model="gpt-4.1-nano",
  messages=[
    {
      "role": "system",
      "content": [
        {
          "type": "text",
          "text": "You are a professional Bitcoin investment analyst and trader with expertise in both technical and fundamental analysis.\nBased on the provided chart data (from the variable df), which contains recent OHLCV information for Bitcoin (KRW-BTC), analyze the current market condition and determine the safest possible action: Buy, Sell, or Hold.\nYour top priority is to avoid any potential loss and protect the principal amount under all circumstances.\nIf there is any uncertainty or risk of loss, choose Hold instead of taking action.\nEvaluate short-term momentum, trend direction, and volatility carefully, but only recommend Buy or Sell if the probability of loss is virtually zero.\nConclude with your final recommendation (Buy, Sell, or Hold) and provide a brief, clear explanation for your reasoning. Response in Json Format.\n\nResponse Example: \n{\n  \"decision\": \"buy\",\n  \"confidence\": 0.88,\n  \"reason\": \"Bitcoin has formed a higher low on the daily chart and just broke above the 50-day moving average with rising volume. RSI is recovering from the mid-40s, suggesting renewed bullish momentum.\",\n  \"risk_level\": \"low\",\n  \"timestamp\": \"2025-11-07T22:45:00+09:00\"\n}\n{\n  \"decision\": \"sell\",\n  \"confidence\": 0.91,\n  \"reason\": \"A double-top pattern has formed near the 100-day moving average with decreasing volume. RSI shows bearish divergence, and price failed to hold the key resistance level at 98,000,000 KRW.\",\n  \"risk_level\": \"medium\",\n  \"timestamp\": \"2025-11-07T22:45:00+09:00\"\n}\n{\n  \"decision\": \"hold\",\n  \"confidence\": 0.76,\n  \"reason\": \"The market is currently consolidating within a narrow range between 92M and 95M KRW. No clear breakout or breakdown signal is confirmed, and volatility remains low.\",\n  \"risk_level\": \"none\",\n  \"timestamp\": \"2025-11-07T22:45:00+09:00\"\n}"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
         "text": df.to_json()
         }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": "{\n  \"decision\": \"hold\",\n  \"confidence\": 0.74,\n  \"reason\": \"Bitcoin has seen a pronounced downtrend in recent candles, with a sharp decline in price from above 170M KRW to the low 150M KRW range, and high volatility indicated by large candles and volume spikes. Despite a recent small bounce, the short-term trend remains downward, and there is no confirmed bullish reversal or stable consolidation yet. Attempting to buy now risks further downside, and selling here could result in exiting near a potential oversold area without clear reversal. The safest action to protect principal is to stay on the sidelines until a bottom or reliable shift in momentum is confirmed.\",\n  \"risk_level\": \"none\",\n  \"timestamp\": \"2025-11-07T22:45:00+09:00\"\n}"
        }
      ]
    }
  ],
  response_format={
    "type": "json_object"
  },
)

result = response.choices[0].message.content


import json
result = json.loads(result)

# 로그인 기능 구현
import pyupbit

access = os.getenv('UPBIT_ACCESS_KEY')
secret = os.getenv('UPBIT_SECRET_KEY')
upbit = pyupbit.Upbit(access, secret)


# 전량 매수, 매도 로직(get_balance 가 잔고)
if result['decision'] == "buy":
  print(upbit.buy_market_order("KRW-BTC", upbit.get_balance("KRW")))
  print(result["reason"])
elif result['decision'] == "sell":
  print(upbit.sell_market_order("KRW-BTC", upbit.get_balance("KRW-BTC")))
  print(result["reason"])
elif result['decision'] == "hold":
  print(result["reason"])
pass


