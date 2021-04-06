import pandas as pd 
import numpy as np 
import requests
import time
url = "https://api.upbit.com/v1/candles/minutes/10"

querystring = {"market":"KRW-MED","count":"200"}

response = requests.request("GET", url, params=querystring)

data_json = response.json()

data = pd.DataFrame(data_json) 
data=data.reindex(index=data.index[::-1]).reset_index()

#data.columns = ['Open', 'High', "Low", "Close", "Volumn", "Adj"]
#'opening_price' 'high_price' , 'low_price', 'trade_price'
def cal_dmi(data, n=14, n_ADX=14) :
    #https://github.com/Crypto-toolbox/pandas-technical-indicators/blob/master/technical_indicators.py : ADX 
    i = 0 
    #print(data.loc[0,'trade_price'])
    UpI = [0] 
    DoI = [0] 
    while i + 1 <= data.index[-1] : 
        UpMove = data.loc[i + 1, "high_price"] - data.loc[i, "high_price"] 
        DoMove = data.loc[i, "low_price"] - data.loc[i+1, "low_price"] 
        if UpMove > DoMove and UpMove > 0 : 
            UpD = UpMove 
        else : 
            UpD = 0 
        UpI.append(UpD) 
        if DoMove > UpMove and DoMove > 0 :
            DoD = DoMove 
        else : 
            DoD = 0 
        DoI.append(DoD) 
        i = i + 1 
    
    i = 0 
    TR_l = [0] 
    while i < data.index[-1]: 
        TR = max(data.loc[i + 1, 'high_price'], data.loc[i, 'trade_price']) - min(data.loc[i + 1, 'low_price'], data.loc[i, 'trade_price']) 
        TR_l.append(TR) 
        i = i + 1 
    TR_s = pd.Series(TR_l) 
    ATR = pd.Series(TR_s.ewm(span=n, min_periods=1).mean()) 
    UpI = pd.Series(UpI) 
    DoI = pd.Series(DoI) 
    PosDI = pd.Series(UpI.ewm(span=n, min_periods=1).mean() / ATR) 
    NegDI = pd.Series(DoI.ewm(span=n, min_periods=1).mean() / ATR) 
    ADX = pd.Series((abs(PosDI - NegDI) / (PosDI + NegDI)).ewm(span=n_ADX, min_periods=1).mean(), name='ADX_' + str(n) + '_' + str(n_ADX)) 
    return PosDI, NegDI, ADX 


data["PDI"],data["MDI"],data["ADX"] = cal_dmi(data, n=27,n_ADX=27)

pdi = data["PDI"].iloc[-1]
pdi = float(pdi) * 100
mdi = data["MDI"].iloc[-1]
mdi = float(mdi) * 100
adx = data["ADX"].iloc[-1]
adx = float(adx) * 100

print("this is PDI", pdi)
print("this is MDI", mdi)
print("this is ADX", adx)
time.sleep(1)

    # 27 일때 같은 값 나옴.
