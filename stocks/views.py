from django.db import connection
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
import requests
from stocks.backtest import backtest_strategy
from stocks.models import StockData

def fetch_stock_data_view(request):
    symbol = 'AAPL'
    api_key = settings.ALPHA_VANTAGE_API_KEY
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        # print('datafetched from the Api')
        # print(data)

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
            # print(connection.queries)
        
        # loop over data in database and print row by row
        # print('printing data from the database')
        # for row in StockData.objects.all():
        #     print(row) 
        
        
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

    # Fetch historical data for the selected symbol
    stock_data = StockData.objects.filter(symbol=symbol, date__range=[start_date, end_date]).order_by('date')
    print(stock_data)
    # Fetch all historical data for the selected symbol
    stock_data = StockData.objects.filter(symbol=symbol).order_by('date')
    for row in stock_data:
        print(row)
    
    
    

    if not stock_data.exists():
        return JsonResponse({"error": "No stock data found for the given date range."}, status=404)

    # Convert data to a list of closing prices
    prices = stock_data.values_list('close_price', flat=True)
    
    # Run the backtest strategy
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
