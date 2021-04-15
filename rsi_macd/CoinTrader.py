import numpy as np
import pandas as pd
import requests
import time


long_url_list = []

long_url_list.append("https://api.upbit.com/v1/candles/months")
long_url_list.append("https://api.upbit.com/v1/candles/weeks")
long_url_list.append("https://api.upbit.com/v1/candles/days")
long_url_list.append("https://api.upbit.com/v1/candles/minutes/240")

short_url_list = []
short_url_list.append("https://api.upbit.com/v1/candles/minutes/60")
short_url_list.append("https://api.upbit.com/v1/candles/minutes/30")
short_url_list.append("https://api.upbit.com/v1/candles/minutes/10")
short_url_list.append("https://api.upbit.com/v1/candles/minutes/5")
short_url_list.append("https://api.upbit.com/v1/candles/minutes/1")


def find_krw_market():
    word_count = 0
    word = []
    word_2 = []
    krw_list  = []
    word_2_str =""
    find_url = "https://api.upbit.com/v1/market/all"

    querystring = {"isDetails":"false"}

    response = requests.request("GET", find_url, params=querystring)

    coin_list = response.text
    coin_list = coin_list[1:]
    coin_list = coin_list[:-1]


    for a in coin_list:
        
        if a != "}":
            word.append(a)
        else:
            word.append(a)
            word_str = ''.join(word)
            if word_count == 0:
                word_str = word_str[1:]
            else:
                word_str = word_str[2:]
            word_str = word_str[:-1]
            if 'KRW-' in word_str:
                count = 0
                for a in word_str:
                    if a == '"':
                        word_2.append(a)
                        count += 1
                        if count == 4:
                            word_2_str= ''.join(word_2)
                            break
                    else:
                        word_2.append(a)
                if "{" in word_2_str:
                    word_2_str.replace("{","")
                
                
                krw_list.append(word_2_str)
            word = []
            word_2 = []
            word_str = ""
            word_2_str = ""
        word_count += 1
    del krw_list[0]
    return (krw_list)


# Commodity Channel Index 
def CCI(data, ndays): 
    print('--------------------cci ------------------------------------')
    TP = (data['high_price'] + data['low_price'] + data['trade_price']) / 3 
    CCI = pd.Series((TP - TP.rolling(ndays).mean()) / (0.0118 * TP.rolling(ndays).std()),
                    name = 'CCI') 
    sm = TP - TP.rolling(ndays).mean()
    sm = sm.rolling(ndays).sum() / ndays
    
    # CCI = pd.Series((TP - TP.rolling(ndays).mean()) / (0.015 * sm),
    #                 name = 'CCI') 

    # CCI = pd.Series((TP - TP.rolling(ndays).mean()) / (0.01015 * TP.rolling(ndays).std()),
    #                name = 'CCI')
    data = data.join(CCI) 
    return CCI

## rsi
def rsi(ohlc: pd.DataFrame, period: int = 14):
    print('--------------------rsi ------------------------------------')
    ohlc["trade_price"] = ohlc["trade_price"]
    delta = ohlc["trade_price"].diff()

    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0

    _gain = up.ewm(com=(period - 1), min_periods=period).mean()
    _loss = down.abs().ewm(com=(period - 1), min_periods=period).mean()

    RS = _gain / _loss
    return pd.Series(100 - (100 / (1 + RS)), name="RSI")

#####macd

def MACD(df2):
    
   #print('--------------------macd ------------------------------------')
   exp1 = df2['trade_price'].ewm(span=12, adjust=False).mean()
   exp2 = df2['trade_price'].ewm(span=26, adjust=False).mean()
   macd = exp1-exp2
   exp3 = macd.ewm(span=9, adjust=False).mean()
   histogram = macd[0] - exp3[0]

#    print('histogram: ',histogram)


#    print('MACD: ',macd[0])
#    print('Signal: ',exp3[0])

   test1=macd[0] - exp3[0]   # 0 은 오늘값
   test2=macd[1] - exp3[1]    # 1 은 어제값     

   call='매매 필요없음'

   return histogram
#    print('exp',exp3[1])    # exp3 은 시그널 값.

#    # test 는 시그널 값에서 macd 값을 뺀 것.  

#    print("test1" , test1)
#    print("test2", test2)

#    if test1<0 and test2>0:     # 어제는 0 위에 있었는데, 오늘 0 아래로 떨어질 때 매도
#       call='매도'
      
#    if test1>0 and test2<0:     # 어제는 0 아래에 있었는데, 오늘 0 위로 오를 때 매수. 
#       call='매수'
      
#    print('BTC 매매의견: ', call)


###supertrend

def EMA(df, base, target, period, alpha=False):
    print('--------------------supertrend ------------------------------------')
    """
    Function to compute Exponential Moving Average (EMA)
    
    Args :
        df : Pandas DataFrame which contains ['date', 'open', 'high', 'low', 'close', 'volume'] columns
        base : String indicating the column name from which the EMA needs to be computed from
        target : String indicates the column name to which the computed data needs to be stored
        period : Integer indicates the period of computation in terms of number of candles
        alpha : Boolean if True indicates to use the formula for computing EMA using alpha (default is False)
        
    Returns :
        df : Pandas DataFrame with new column added with name 'target'
    """

    con = pd.concat([df[:period][base].rolling(window=period).mean(), df[period:][base]])
    
    if (alpha == True):
        # (1 - alpha) * previous_val + alpha * current_val where alpha = 1 / period
        df[target] = con.ewm(alpha=1 / period, adjust=False).mean()
    else:
        # ((current_val - previous_val) * coeff) + previous_val where coeff = 2 / (period + 1)
        df[target] = con.ewm(span=period, adjust=False).mean()
    
    df[target].fillna(0, inplace=True)
    return df

def ATR(df, period, ohlc=['opening_price', 'high_price', 'low_price', 'trade_price']):
    """
    Function to compute Average True Range (ATR)
    
    Args :
        df : Pandas DataFrame which contains ['date', 'open', 'high', 'low', 'close', 'volume'] columns
        period : Integer indicates the period of computation in terms of number of candles
        ohlc: List defining OHLC Column names (default ['Open', 'High', 'Low', 'Close'])
        
    Returns :
        df : Pandas DataFrame with new columns added for 
            True Range (TR)
            ATR (ATR_$period)
    """
    atr = 'ATR_' + str(period)

    # Compute true range only if it is not computed and stored earlier in the df
    if not 'TR' in df.columns:
        df['h-l'] = df[ohlc[1]] - df[ohlc[2]]
        df['h-yc'] = abs(df[ohlc[1]] - df[ohlc[3]].shift())
        df['l-yc'] = abs(df[ohlc[2]] - df[ohlc[3]].shift())
         
        df['TR'] = df[['h-l', 'h-yc', 'l-yc']].max(axis=1)
         
        df.drop(['h-l', 'h-yc', 'l-yc'], inplace=True, axis=1)

    # Compute EMA of true range using ATR formula after ignoring first row
    EMA(df, 'TR', atr, period, alpha=True)
    
    return df


def SuperTrend(df, period, multiplier, ohlc=['opening_price', 'high_price', 'low_price', 'trade_price']):
    """
    Function to compute SuperTrend
    
    Args :
        df : Pandas DataFrame which contains ['date', 'open', 'high', 'low', 'close', 'volume'] columns
        period : Integer indicates the period of computation in terms of number of candles
        multiplier : Integer indicates value to multiply the ATR
        ohlc: List defining OHLC Column names (default ['Open', 'High', 'Low', 'Close'])
        
    Returns :
        df : Pandas DataFrame with new columns added for 
            True Range (TR), ATR (ATR_$period)
            SuperTrend (ST_$period_$multiplier)
            SuperTrend Direction (STX_$period_$multiplier)
    """

    ATR(df, period, ohlc=ohlc)
    atr = 'ATR_' + str(period)
    st = 'ST_' + str(period) + '_' + str(multiplier)
    stx = 'STX_' + str(period) + '_' + str(multiplier)
    
    """
    SuperTrend Algorithm :
    
        BASIC UPPERBAND = (HIGH + LOW) / 2 + Multiplier * ATR
        BASIC LOWERBAND = (HIGH + LOW) / 2 - Multiplier * ATR
        
        FINAL UPPERBAND = IF( (Current BASICUPPERBAND < Previous FINAL UPPERBAND) or (Previous Close > Previous FINAL UPPERBAND))
                            THEN (Current BASIC UPPERBAND) ELSE Previous FINALUPPERBAND)
        FINAL LOWERBAND = IF( (Current BASIC LOWERBAND > Previous FINAL LOWERBAND) or (Previous Close < Previous FINAL LOWERBAND)) 
                            THEN (Current BASIC LOWERBAND) ELSE Previous FINAL LOWERBAND)
        
        SUPERTREND = IF((Previous SUPERTREND = Previous FINAL UPPERBAND) and (Current Close <= Current FINAL UPPERBAND)) THEN
                        Current FINAL UPPERBAND
                    ELSE
                        IF((Previous SUPERTREND = Previous FINAL UPPERBAND) and (Current Close > Current FINAL UPPERBAND)) THEN
                            Current FINAL LOWERBAND
                        ELSE
                            IF((Previous SUPERTREND = Previous FINAL LOWERBAND) and (Current Close >= Current FINAL LOWERBAND)) THEN
                                Current FINAL LOWERBAND
                            ELSE
                                IF((Previous SUPERTREND = Previous FINAL LOWERBAND) and (Current Close < Current FINAL LOWERBAND)) THEN
                                    Current FINAL UPPERBAND
    """
    
    # Compute basic upper and lower bands
    df['basic_ub'] = (df[ohlc[1]] + df[ohlc[2]]) / 2 + multiplier * df[atr]
    df['basic_lb'] = (df[ohlc[1]] + df[ohlc[2]]) / 2 - multiplier * df[atr]

    # Compute final upper and lower bands
    df['final_ub'] = 0.00
    df['final_lb'] = 0.00
    for i in range(period, len(df)):
        df['final_ub'].iat[i] = df['basic_ub'].iat[i] if df['basic_ub'].iat[i] < df['final_ub'].iat[i - 1] or df[ohlc[3]].iat[i - 1] > df['final_ub'].iat[i - 1] else df['final_ub'].iat[i - 1]
        df['final_lb'].iat[i] = df['basic_lb'].iat[i] if df['basic_lb'].iat[i] > df['final_lb'].iat[i - 1] or df[ohlc[3]].iat[i - 1] < df['final_lb'].iat[i - 1] else df['final_lb'].iat[i - 1]
       
    # Set the Supertrend value
    df[st] = 0.00
    for i in range(period, len(df)):
        df[st].iat[i] = df['final_ub'].iat[i] if df[st].iat[i - 1] == df['final_ub'].iat[i - 1] and df[ohlc[3]].iat[i] <= df['final_ub'].iat[i] else \
                        df['final_lb'].iat[i] if df[st].iat[i - 1] == df['final_ub'].iat[i - 1] and df[ohlc[3]].iat[i] >  df['final_ub'].iat[i] else \
                        df['final_lb'].iat[i] if df[st].iat[i - 1] == df['final_lb'].iat[i - 1] and df[ohlc[3]].iat[i] >= df['final_lb'].iat[i] else \
                        df['final_ub'].iat[i] if df[st].iat[i - 1] == df['final_lb'].iat[i - 1] and df[ohlc[3]].iat[i] <  df['final_lb'].iat[i] else 0.00 
                 
    # Mark the trend direction up/down
    df[stx] = np.where((df[st] > 0.00), np.where((df[ohlc[3]] < df[st]), 'down',  'up'), np.NaN)

    # Remove basic and final bands from the columns
    df.drop(['basic_ub', 'basic_lb', 'final_ub', 'final_lb'], inplace=True, axis=1)
    
    df.fillna(0, inplace=True)

    return (df[stx].iloc[-1])
###adx dmi

def cal_dmi(df, n=14, n_ADX=14) :
    print('--------------------pdi adx ------------------------------------')
    #https://github.com/Crypto-toolbox/pandas-technical-indicators/blob/master/technical_indicators.py : ADX 
    i = 0 
    #print(data.loc[0,'trade_price'])
    UpI = [0] 
    DoI = [0] 
    while i + 1 <= df.index[-1] : 
        UpMove = df.loc[i + 1, "high_price"] - df.loc[i, "high_price"] 
        DoMove = df.loc[i, "low_price"] - df.loc[i+1, "low_price"] 
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
    while i < df.index[-1]: 
        TR = max(df.loc[i + 1, 'high_price'], df.loc[i, 'trade_price']) - min(df.loc[i + 1, 'low_price'], df.loc[i, 'trade_price']) 
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


coin_name = 'MFT'
for url in long_url_list:
    coin_name = 'KRW-' + coin_name
    querystring = {'market':coin_name, 'count':'200'}
    
    response = requests.request("GET", url, params=querystring)
    data = response.json()
    df = pd.DataFrame(data)
    df=df.reindex(index=df.index[::-1]).reset_index()
    ## for macd 
    df2 = pd.DataFrame(data)
    df2 = df2.iloc[::-1]

    #macd 는 df2
    histogram = MACD(df2)

    CCI = CCI(df, 20).iloc[-1]
    rsi = rsi(df, 14).iloc[-1]
    supertrend_status = SuperTrend(df, 10, 3)
    df["PDI"],df["MDI"],df["ADX"] = cal_dmi(df, n=27,n_ADX=27)
    pdi = df["PDI"].iloc[-1]
    pdi = float(pdi) * 100
    mdi = df["MDI"].iloc[-1]
    mdi = float(mdi) * 100
    adx = df["ADX"].iloc[-1]
    adx = float(adx) * 100

    cci_status = ''
    rsi_status = ''
    macd_status = ''
    #supertrend 는 이미 있음
    adx_status = ''
    pdi_status = '' 
    mdi_status = ''

    if url == long_url_list[0]:
        print('-------', coin_name, '의 월 상태 --------')
        print('대략적인 cci  : ' ,CCI)
        if CCI > 50 :
            print("CCI 50 이상 --  양호")
            cci_status = '양호'
        print('rsi  : ' ,rsi)
        if rsi > 50 :
            print('rsi 50 이상 --   양호')
            rsi_status = '양호'
        print('supertrend  : ', supertrend_status)
        if supertrend_status == 'up':
            print( 'supertrend  : up --    양호')
        else:
            print( 'supertrend  : down --    양호 X')
        print('macd 상태  : ', histogram )
        if(histogram > 0):
            print('macd histogram  0 초과  --    양호')
            macd_status = '양호'
        else:
            print('macd histogram 0 이하  --     양호 X')
        print('adx  : ' ,adx)
        if adx >= 20:
            print( 'adx 20 이상 --    양호')
            adx_status = '양호'
        else :
            print('adx 20 미만 --     양호 X')
        print('pdi  : ', pdi)
        if adx >= 20:
            print( 'pdi 20 이상 --    양호')
            pdi_status = '양호'
        else :
            print('pdi 20 미만 --     양호 X')
        print('mdi  : ', mdi)
        if adx <= 20:
            print( 'mdi 20 미만 --    양호')
            mdi_status = '양호'
        else :
            print('mdi 20 초과 --     양호 X')


        print('---------------------------------------------')
        print(' cci : ',cci_status,' rsi : ',rsi_status,' macd : ',macd_status,' supertrend : ',supertrend_status,' adx : ', adx_status, ' pdi : ', pdi_status, ' mdi : ', mdi_status)
        print('---------------------------------------------')


    elif url == long_url_list[1]:
        print('-------', coin_name, '의 주 상태 --------')
        print('대략적인 cci  : ' ,CCI)
        if CCI > 50 :
            print("CCI 50 이상 --  양호")
            cci_status = '양호'
        print('rsi  : ' ,rsi)
        if rsi > 50 :
            print('rsi 50 이상 --   양호')
            rsi_status = '양호'
        print('supertrend  : ', supertrend_status)
        if supertrend_status == 'up':
            print( 'supertrend  : up --    양호')
        else:
            print( 'supertrend  : down --    양호 X')
        print('macd 상태  : ', histogram )
        if(histogram > 0):
            print('macd histogram  0 초과  --    양호')
            macd_status = '양호'
        else:
            print('macd histogram 0 이하  --     양호 X')
        print('adx  : ' ,adx)
        if adx >= 20:
            print( 'adx 20 이상 --    양호')
            adx_status = '양호'
        else :
            print('adx 20 미만 --     양호 X')
        print('pdi  : ', pdi)
        if adx >= 20:
            print( 'pdi 20 이상 --    양호')
            pdi_status = '양호'
        else :
            print('pdi 20 미만 --     양호 X')
        print('mdi  : ', mdi)
        if adx <= 20:
            print( 'mdi 20 미만 --    양호')
            mdi_status = '양호'
        else :
            print('mdi 20 초과 --     양호 X')


        print('---------------------------------------------')
        print(' cci : ',cci_status,' rsi : ',rsi_status,' macd : ',macd_status,' supertrend : ',supertrend_status,' adx : ', adx_status, ' pdi : ', pdi_status, ' mdi : ', mdi_status)
        print('---------------------------------------------')

    elif url == long_url_list[2]:
        print('-------', coin_name, '의 일 상태 --------')
        print('대략적인 cci  : ' ,CCI)
        if CCI > 50 :
            print("CCI 50 이상 --  양호")
            cci_status = '양호'
        print('rsi  : ' ,rsi)
        if rsi > 50 :
            print('rsi 50 이상 --   양호')
            rsi_status = '양호'
        print('supertrend  : ', supertrend_status)
        if supertrend_status == 'up':
            print( 'supertrend  : up --    양호')
        else:
            print( 'supertrend  : down --    양호 X')
        print('macd 상태  : ', histogram )
        if(histogram > 0):
            print('macd histogram  0 초과  --    양호')
            macd_status = '양호'
        else:
            print('macd histogram 0 이하  --     양호 X')
        print('adx  : ' ,adx)
        if adx >= 20:
            print( 'adx 20 이상 --    양호')
            adx_status = '양호'
        else :
            print('adx 20 미만 --     양호 X')
        print('pdi  : ', pdi)
        if adx >= 20:
            print( 'pdi 20 이상 --    양호')
            pdi_status = '양호'
        else :
            print('pdi 20 미만 --     양호 X')
        print('mdi  : ', mdi)
        if adx <= 20:
            print( 'mdi 20 미만 --    양호')
            mdi_status = '양호'
        else :
            print('mdi 20 초과 --     양호 X')


        print('---------------------------------------------')
        print(' cci : ',cci_status,' rsi : ',rsi_status,' macd : ',macd_status,' supertrend : ',supertrend_status,' adx : ', adx_status, ' pdi : ', pdi_status, ' mdi : ', mdi_status)
        print('---------------------------------------------')

    
    elif url == long_url_list[3]:
        print('-------', coin_name, '의 4시간봉 상태 --------')
        print('대략적인 cci  : ' ,CCI)
        if CCI > 50 :
            print("CCI 50 이상 --  양호")
            cci_status = '양호'
        print('rsi  : ' ,rsi)
        if rsi > 50 :
            print('rsi 50 이상 --   양호')
            rsi_status = '양호'
        print('supertrend  : ', supertrend_status)
        if supertrend_status == 'up':
            print( 'supertrend  : up --    양호')
        else:
            print( 'supertrend  : down --    양호 X')
        print('macd 상태  : ', histogram )
        if(histogram > 0):
            print('macd histogram  0 초과  --    양호')
            macd_status = '양호'
        else:
            print('macd histogram 0 이하  --     양호 X')
        print('adx  : ' ,adx)
        if adx >= 20:
            print( 'adx 20 이상 --    양호')
            adx_status = '양호'
        else :
            print('adx 20 미만 --     양호 X')
        print('pdi  : ', pdi)
        if adx >= 20:
            print( 'pdi 20 이상 --    양호')
            pdi_status = '양호'
        else :
            print('pdi 20 미만 --     양호 X')
        print('mdi  : ', mdi)
        if adx <= 20:
            print( 'mdi 20 미만 --    양호')
            mdi_status = '양호'
        else :
            print('mdi 20 초과 --     양호 X')


        print('---------------------------------------------')
        print(' cci : ',cci_status,' rsi : ',rsi_status,' macd : ',macd_status,' supertrend : ',supertrend_status,' adx : ', adx_status, ' pdi : ', pdi_status, ' mdi : ', mdi_status)
        print('---------------------------------------------')
