from django.db import connection
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
import requests
from stocks.backtest import backtest_strategy
from stocks.models import StockData
from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import numpy as np
import pandas as pd
from .utils import load_model
from .models import StockPricePrediction


def fetch_stock_data_view(request):
    symbol = 'AAPL'
    api_key = settings.ALPHA_VANTAGE_API_KEY
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if 'Note' in data:
            return JsonResponse({"error": "API call limit reached. Please try again later."}, status=429)

        if 'Time Series (Daily)' not in data:
            return JsonResponse({"error": "Failed to fetch data"}, status=400)

        for date, values in data['Time Series (Daily)'].items():
            StockData.objects.update_or_create(
                symbol=symbol,
                date=date,
                defaults={
                    'open_price': float(values['1. open']),
                    'high_price': float(values['2. high']),
                    'low_price': float(values['3. low']),
                    'close_price': float(values['4. close']),
                    'volume': int(values['5. volume'])
                }
            )
        
        return JsonResponse({"success": f"Successfully fetched and stored data for {symbol}"})

    except requests.exceptions.HTTPError as http_err:
        return JsonResponse({"error": f"HTTP error occurred: {http_err}"}, status=500)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": "Network error occurred. Please check your connection."}, status=500)
    except requests.exceptions.Timeout:
        return JsonResponse({"error": "Request timed out. Please try again later."}, status=500)
    except requests.exceptions.RequestException as err:
        return JsonResponse({"error": f"An error occurred: {err}"}, status=500)
    except Exception as e:
        return JsonResponse({"error": f"An unexpected error occurred: {e}"}, status=500)

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from stocks.models import StockData
import pandas as pd

def backtest_view(request):
    symbol = request.GET.get('symbol', 'AAPL')
    initial_investment = float(request.GET.get('initial_investment', 1000))
    short_window = int(request.GET.get('short_window', 50))
    long_window = int(request.GET.get('long_window', 200))
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if not start_date or not end_date:
        return JsonResponse({"error": "Please provide both start_date and end_date parameters."}, status=400)

    stock_data = StockData.objects.filter(symbol=symbol, date__range=[start_date, end_date]).order_by('date')
    print(stock_data)
    stock_data = StockData.objects.filter(symbol=symbol).order_by('date')
    for row in stock_data:
        print(row)
    
    
    

    if not stock_data.exists():
        return JsonResponse({"error": "No stock data found for the given date range."}, status=404)

    prices = stock_data.values_list('close_price', flat=True)
    final_value, transactions, performance_summary = backtest_strategy(initial_investment, prices, short_window, long_window)

    return JsonResponse({
        "symbol": symbol,
        "start_date": start_date,
        "end_date": end_date,
        "initial_investment": initial_investment,
        "final_value": final_value,
        "transactions": transactions,
        "performance_summary": performance_summary
    })

class PredictStockView(APIView):
    def get(self, request, symbol, format=None):
        model = load_model()

        historical_data = StockData.objects.filter(symbol=symbol).order_by('date')
        if not historical_data.exists():
            return Response({
                'error': f'No historical data found for stock symbol: {symbol}'
            }, status=status.HTTP_404_NOT_FOUND)

        historical_prices = np.array([entry.close_price for entry in historical_data])
        historical_dates = np.array([entry.date for entry in historical_data])
        future_dates = pd.date_range(start=now().date(), periods=30).to_pydatetime()
        future_days = np.array([i for i in range(len(historical_prices) + 1, len(historical_prices) + 31)]).reshape(-1, 1)
        predicted_prices = model.predict(future_days)
        predictions = []
        for i, price in enumerate(predicted_prices):
            prediction = StockPricePrediction(
                stock_symbol=symbol,
                prediction_date=future_dates[i],
                predicted_price=price
            )
            predictions.append(prediction)
        StockPricePrediction.objects.bulk_create(predictions)

        return Response({
            'stock_symbol': symbol,
            'predicted_prices': [
                {
                    'predicted_date': future_dates[i].strftime('%Y-%m-%d'),
                    'predicted_price': predicted_prices[i]
                } for i in range(len(predicted_prices))
            ]
        }, status=status.HTTP_200_OK)