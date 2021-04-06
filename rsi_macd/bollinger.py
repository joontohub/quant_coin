
import requests
import pandas as pd
import time


url = "https://api.upbit.com/v1/candles/minutes/1"

querystring = {"market":"KRW-XRP","count":"100"}

response = requests.request("GET", url, params=querystring)

data = response.json()

df = pd.DataFrame(data)

df=df.iloc[::-1]

def bollinger_bands(df, n):
    """
    
    :param df: pandas.DataFrame
    :param n: 
    :return: pandas.DataFrame
    """
    MA = pd.Series(df['Close'].rolling(n, min_periods=n).mean())
    MSD = pd.Series(df['Close'].rolling(n, min_periods=n).std())
    b1 = 4 * MSD / MA
    B1 = pd.Series(b1, name='BollingerB_' + str(n))
    df = df.join(B1)
    b2 = (df['Close'] - MA + 2 * MSD) / (4 * MSD)
    B2 = pd.Series(b2, name='Bollinger%b_' + str(n))
    df = df.join(B2)
    return df
