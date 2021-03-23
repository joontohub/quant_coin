import requests
import pandas as pd
import time


while True:
    url = "https://api.upbit.com/v1/candles/days"

    querystring = {"market":"KRW-BTC","count":"100"}
    
    response = requests.request("GET", url, params=querystring)
    
    data = response.json()
    
    df = pd.DataFrame(data)
    
    df=df.iloc[::-1]
    
    df=df['trade_price']

  
    exp1 = df.ewm(span=12, adjust=False).mean()
    exp2 = df.ewm(span=26, adjust=False).mean()
    macd = exp1-exp2
    exp3 = macd.ewm(span=9, adjust=False).mean()
    
    print('MACD: ',macd[0])
    print('Signal: ',exp3[0])
    
    test1=exp3[0]-macd[0]
    test2=exp3[1]-macd[1]
    
    call='매매 필요없음'
    
    if test1<0 and test2>0:
       call='매도'
       
    if test1>0 and test2<0:
       call='매수'
       
    print('BTC 매매의견: ', call)

    time.sleep(1)
