import os
from dotenv import load_dotenv
load_dotenv()

import pyupbit
df = pyupbit.get_ohlcv("KRW-BTC", count = 30, interval = "day")
print(df)


