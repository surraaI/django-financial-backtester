import requests
import time
from django.core.management.base import BaseCommand
from stocks.models import StockData
from django.conf import settings

class Command(BaseCommand):
    help = "Fetch stock data from Alpha Vantage"

    def handle(self, *args, **kwargs):
        symbol = 'AAPL'
        api_key = settings.ALPHA_VANTAGE_API_KEY
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()  

            data = response.json()

            if 'Note' in data:
                self.stdout.write(self.style.WARNING("API call limit reached. Please try again later."))
                return

            if 'Time Series (Daily)' not in data:
                self.stdout.write(self.style.ERROR("Failed to fetch data"))
                return

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
            self.stdout.write(self.style.SUCCESS(f"Successfully fetched and stored data for {symbol}"))

        except requests.exceptions.HTTPError as http_err:
            self.stdout.write(self.style.ERROR(f"HTTP error occurred: {http_err}"))
        except requests.exceptions.ConnectionError:
            self.stdout.write(self.style.ERROR("Network error occurred. Please check your connection."))
        except requests.exceptions.Timeout:
            self.stdout.write(self.style.ERROR("Request timed out. Please try again later."))
        except requests.exceptions.RequestException as err:
            self.stdout.write(self.style.ERROR(f"An error occurred: {err}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An unexpected error occurred: {e}"))
