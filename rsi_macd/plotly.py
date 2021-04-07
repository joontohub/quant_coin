import plotly.offline as offline 
import plotly.graph_objs as go 
import requests
import pandas as pd

url = "https://api.upbit.com/v1/candles/minutes/1"

querystring = {"market":"KRW-XRP","count":"100"}

response = requests.request("GET", url, params=querystring)

data = response.json()

df = pd.DataFrame(data)

df=df.iloc[::-1]


offline.init_notebook_mode(connected=True) 

trace = go.Candlestick(x=df.date_time, open=df.open_price, high=df.high_price, low=df.low_price, close=df.close_price) 
    
data = [trace] 

layout = go.Layout(title='Quant')
fig = go.Figure(data=data, layout=layout)
offline.iplot(fig, filename="candlestick")

