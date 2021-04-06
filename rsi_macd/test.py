import requests
import pandas as pd
import time




url = "https://api.upbit.com/v1/candles/minutes/10"

querystring = {"market":"KRW-BTC","count":"500"}

response = requests.request("GET", url, params=querystring)

data = response.json()

df = pd.DataFrame(data)

df=df.reindex(index=df.index[::-1]).reset_index()

df['close']=df["trade_price"]

print(df)