import pandas as pd
import requests
import time

url = "https://api.upbit.com/v1/candles/minutes/10"

querystring = {"market":"KRW-BTC","count":"500"}

response = requests.request("GET", url, params=querystring)

data = response.json()

df = pd.DataFrame(data)

df=df.reindex(index=df.index[::-1]).reset_index()

df['close']=df["trade_price"]
df['open'] = df['opening_price']
df['high'] = df['high_price']
df['low'] = df['low_price']

def heikin_ashi(df):
    heikin_ashi_df = pd.DataFrame(index=df.index.values, columns=['open', 'high', 'low', 'close'])
    
    heikin_ashi_df['close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
    
    for i in range(len(df)):
        if i == 0:
            heikin_ashi_df.iat[0, 0] = df['open'].iloc[0]
        else:
            heikin_ashi_df.iat[i, 0] = (heikin_ashi_df.iat[i-1, 0] + heikin_ashi_df.iat[i-1, 3]) / 2
        
    heikin_ashi_df['high'] = heikin_ashi_df.loc[:, ['open', 'close']].join(df['high']).max(axis=1)
    
    heikin_ashi_df['low'] = heikin_ashi_df.loc[:, ['open', 'close']].join(df['low']).min(axis=1)
    
    print(heikin_ashi_df)
    return heikin_ashi_df
    
heikin_ashi(df)