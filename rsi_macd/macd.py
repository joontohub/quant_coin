import requests
import pandas as pd
import time


while True:
   url = "https://api.upbit.com/v1/candles/minutes/10"

   querystring = {"market":"KRW-XRP","count":"200"}

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

   test1=macd[0] - exp3[0]   # 0 은 오늘값
   test2=macd[1] - exp3[1]    # 1 은 어제값     

   call='매매 필요없음'

   print('exp',exp3[1])    # exp3 은 시그널 값.

   # test 는 시그널 값에서 macd 값을 뺀 것.  

   print("test1" , test1)
   print("test2", test2)

   if test1<0 and test2>0:     # 어제는 0 위에 있었는데, 오늘 0 아래로 떨어질 때 매도
      call='매도'
      
   if test1>0 and test2<0:     # 어제는 0 아래에 있었는데, 오늘 0 위로 오를 때 매수. 
      call='매수'
      
   print('BTC 매매의견: ', call)

   time.sleep(1)
