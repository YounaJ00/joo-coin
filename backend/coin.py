import os
from dotenv import load_dotenv

load_dotenv()


# 자동 실행을 위한 함수 설정
def ai_trading():
    import pyupbit
    import json
    from openai import OpenAI

    # 공통 설정
    client = OpenAI()
    coin_name = "KRW-BTC"
    fee_multiplier = 0.9995
    min_order_amount = 5000

    df = pyupbit.get_ohlcv(coin_name, count=30, interval="day")

    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": 'You are a professional Bitcoin investment analyst and trader with expertise in both technical and fundamental analysis.\nBased on the provided chart data (from the variable df), which contains recent OHLCV information for Bitcoin (KRW-BTC), analyze the current market condition and determine the safest possible action: Buy, Sell, or Hold.\nYour top priority is to avoid any potential loss and protect the principal amount under all circumstances.\nIf there is any uncertainty or risk of loss, choose Hold instead of taking action.\nEvaluate short-term momentum, trend direction, and volatility carefully.\nConclude with your final recommendation (Buy, Sell, or Hold) and provide a brief, clear explanation for your reasoning. Response in Json Format.\n\nResponse Example: \n{\n  "decision": "buy",\n  "confidence": 0.88,\n  "reason": "Bitcoin has formed a higher low on the daily chart and just broke above the 50-day moving average with rising volume. RSI is recovering from the mid-40s, suggesting renewed bullish momentum.",\n  "risk_level": "low",\n  "timestamp": "2025-11-07T22:45:00+09:00"\n}\n{\n  "decision": "sell",\n  "confidence": 0.91,\n  "reason": "A double-top pattern has formed near the 100-day moving average with decreasing volume. RSI shows bearish divergence, and price failed to hold the key resistance level at 98,000,000 KRW.",\n  "risk_level": "medium",\n  "timestamp": "2025-11-07T22:45:00+09:00"\n}\n{\n  "decision": "hold",\n  "confidence": 0.76,\n  "reason": "The market is currently consolidating within a narrow range between 92M and 95M KRW. No clear breakout or breakdown signal is confirmed, and volatility remains low.",\n  "risk_level": "none",\n  "timestamp": "2025-11-07T22:45:00+09:00"\n}',
                    }
                ],
            },
            {"role": "user", "content": [{"type": "text", "text": df.to_json()}]},
        ],
        response_format={"type": "json_object"},
    )

    result = response.choices[0].message.content
    result = json.loads(result)

    # 로그인 기능 구현
    access = os.getenv("UPBIT_ACCESS_KEY")
    secret = os.getenv("UPBIT_SECRET_KEY")
    upbit = pyupbit.Upbit(access, secret)

    print("### AI Decision: ", result["decision"].upper(), "###")
    print("### Reason:", result["reason"], "###")

    my_money = upbit.get_balance("KRW")
    my_coin = upbit.get_balance(coin_name)  # 보유 코인 조회
    print("보유 금액:", my_money)
    print("보유 코인:", my_coin)

    if my_money is None or my_money == 0:
        print("⚠️ KRW 잔고가 없거나 조회 실패. 매매는 실행하지 않습니다.")
        return

    available_buy_amount = my_money * fee_multiplier

    if result["decision"] == "buy":
        if available_buy_amount > min_order_amount:
            print("### Buy Order Executed ###")
            print(upbit.buy_market_order(coin_name, available_buy_amount))
            # print("buy: " , result["reason"])
        else:
            print(f"### krw 잔고가 {min_order_amount}원 미만 입니다. ###")

    elif result["decision"] == "sell":
        # 현재 매도 호가 조회
        orderbook = pyupbit.get_orderbook(ticker=coin_name)
        current_price = orderbook["orderbook_units"][0]["ask_price"]
        # 매도 시 수수료 제외 전 총 매도 금액
        gross = my_coin * current_price
        available_sell_amount = gross * fee_multiplier

        if available_sell_amount > min_order_amount:
            print("### Sell Order Executed ###")
            print(upbit.sell_market_order(coin_name, my_coin))
            # print("sell: ", result["reason"])
        else:
            print(
                f"### {coin_name} 매도 예상 금액이 {min_order_amount}원 미만입니다. ###"
            )

    elif result["decision"] == "hold":
        print("### Hold Order No Executed ###")
        print("hold: ", result["reason"])
    pass


ai_trading()

# while True:
#   import time
#   print("### 10초 후 자동 매매가 시작됩니다 ###")
#   time.sleep(600)
#   ai_trading()
