from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
import requests
from stocks.models import StockData

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
