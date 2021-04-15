import requests
import pandas as pd
import time





url = "https://api.upbit.com/v1/candles/minutes/10"

querystring = {"market":"KRW-EOS","count":"500"}

response = requests.request("GET", url, params=querystring)

data = response.json()

df = pd.DataFrame(data)

df=df.reindex(index=df.index[::-1]).reset_index()

df['close']=df["trade_price"]




def stochrsi(close, length=None, scalar=None, drift=None,**kwargs):
    # Validate arguments
    length = int(length) if length and length > 0 else 14
    scalar = 100
    drift = int(drift) if drift and drift != 0 else 1

    # Calculate Result
    negative = close.diff(drift)
    positive = negative.copy()

    positive[positive < 0] = 0  # Make negatives 0 for the postive series
    negative[negative > 0] = 0  # Make postives 0 for the negative series
    
    alpha = (1.0 / length) if length > 0 else 0.5
    positive_avg = positive.ewm(alpha=alpha, adjust=False).mean()
    negative_avg = negative.ewm(alpha=alpha, adjust=False).mean().abs()

    rsi = scalar * positive_avg / (positive_avg + negative_avg)
    rsi_low   =  rsi.rolling(length).min()
    rsi_high =  rsi.rolling(length).max()

    fastk = 100 * (rsi - rsi_low) / (rsi_high-rsi_low)

    slowk = fastk.rolling(3).mean()
    slowd = slowk.rolling(3).mean()

    stochdf = pd.DataFrame(list(zip(rsi, slowk,slowd)))
    stochdf.columns=['rsi', 'stochrsi', 'stochrsi_3']

    return stochdf

stochdf =  stochrsi(df['close'])
print(stochdf)