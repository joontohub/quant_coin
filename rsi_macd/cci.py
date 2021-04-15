import requests
import pandas as pd
import time
import matplotlib.pyplot as plt


url = "https://api.upbit.com/v1/candles/minutes/1"

querystring = {"market":"KRW-MFT","count":"200"}

response = requests.request("GET", url, params=querystring)

data = response.json()

df = pd.DataFrame(data)
df=df.reindex(index=df.index[::-1]).reset_index()
#df=df.reindex(index=df.index[::-1]).reset_index()

  


    # Commodity Channel Index 
def CCI(data, ndays): 
    TP = (data['high_price'] + data['low_price'] + data['trade_price']) / 3 
    CCI = pd.Series((TP - TP.rolling(ndays).mean()) / ( 0.0118 * TP.rolling(ndays).std()),
                    name = 'CCI') 
    sm = TP - TP.rolling(ndays).mean()
    sm = sm.rolling(ndays).sum() / ndays
    
    # CCI = pd.Series((TP - TP.rolling(ndays).mean()) / (0.015 * sm),
    #                 name = 'CCI') 

    # CCI = pd.Series((TP - TP.rolling(ndays).mean()) / (0.01015 * TP.rolling(ndays).std()),
    #                name = 'CCI')
    data = data.join(CCI) 
    return CCI



CCI = CCI(df, 20).iloc[-1]


#CCI = CCI["CCI"]

print( 'cci : ', CCI)


 
    # if(CCI > 95 ):
    #     print("cci buy signal")
    # elif (CCI < -105):
    #     print("floor signal") # 위험 , 저점 잡을 때, 
    # else:
    #     print( "wait")


    #166

