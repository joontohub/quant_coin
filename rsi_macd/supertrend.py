import numpy as np
import pandas as pd
import requests
import time

url = "https://api.upbit.com/v1/candles/minutes/1"

querystring = {"market":"KRW-XRP","count":"100"}

response = requests.request("GET", url, params=querystring)

data = response.json()

df = pd.DataFrame(data)

df=df.iloc[::-1]


"""
Usage : 
    data = {
        "data": {
            "candles": [
                ["05-09-2013", 5553.75, 5625.75, 5552.700195, 5592.950195, 274900],
                ["06-09-2013", 5617.450195, 5688.600098, 5566.149902, 5680.399902, 253000],
                ["10-09-2013", 5738.5, 5904.850098, 5738.200195, 5896.75, 275200],
                ["11-09-2013", 5887.25, 5924.350098, 5832.700195, 5913.149902, 265000],
                ["12-09-2013", 5931.149902, 5932, 5815.799805, 5850.700195, 273000],
                ...
                ["27-01-2014", 6186.299805, 6188.549805, 6130.25, 6135.850098, 190400],
                ["28-01-2014", 6131.850098, 6163.600098, 6085.950195, 6126.25, 184100],
                ["29-01-2014", 6161, 6170.450195, 6109.799805, 6120.25, 146700],
                ["30-01-2014", 6067, 6082.850098, 6027.25, 6073.700195, 208100],
                ["31-01-2014", 6082.75, 6097.850098, 6067.350098, 6089.5, 146700]        
            ]
        }
    }
    
    # Date must be present as a Pandas DataFrame with ['date', 'open', 'high', 'low', 'close', 'volume'] as columns
    df = pd.DataFrame(data["data"]["candles"], columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    
    # Columns as added by each function specific to their computations
    EMA(df, 'close', 'ema_5', 5)
    ATR(df, 14)
    SuperTrend(df, 10, 3)
    MACD(df)
"""


# I need to change 'date', 'open', 'high', 'low', 'close', 'volume' column

df['Close']=df["trade_price"]
df['Open'] = df['opening_price']
df['High'] = df['high_price']
df['Low'] = df['low_price']


def EMA(df, base, target, period, alpha=False):
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

def ATR(df, period, ohlc=['Open', 'High', 'Low', 'Close']):
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


def SuperTrend(df, period, multiplier, ohlc=['Open', 'High', 'Low', 'Close']):
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

    print(df[stx])
    return df

SuperTrend(df, 10, 3)