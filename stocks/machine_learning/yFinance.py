import yfinance as yf
import pandas as pd

def get_historical_data(symbol, period='1y'):
    stock = yf.Ticker(symbol)
    hist = stock.history(period=period)
    return hist[['Close']]
