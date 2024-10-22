from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse, JsonResponse

from stocks.models import StockData, StockPricePrediction
from stocks.report.generatePricePlot import generate_price_plot
from stocks.report.generate_pdf import generate_pdf_report


class GenerateStockReportView(APIView):
    def get(self, request, symbol, format=None):
        print(f"Request received for stock symbol: {symbol}")
        historical_data = StockData.objects.filter(symbol=symbol).order_by('date')
        predictions = StockPricePrediction.objects.filter(stock_symbol=symbol).order_by('prediction_date')

        if not historical_data.exists() or not predictions.exists():
            return Response({
                'error': f'No data found for stock symbol: {symbol}'
            }, status=status.HTTP_404_NOT_FOUND)

        historical_prices = [entry.close_price for entry in historical_data]
        historical_dates = [entry.date for entry in historical_data]
        predicted_prices = [entry.predicted_price for entry in predictions]
        predicted_dates = [entry.prediction_date for entry in predictions]

        metrics = {
            'total_return': 10.0,  
            'max_drawdown': 5.0,  
            'number_of_trades': 3  
        }

        
        plot_base64 = generate_price_plot(historical_prices, historical_dates, predicted_prices, predicted_dates)
        report_format = request.GET.get('format', 'json') 
        if report_format == 'pdf':
            pdf_buffer = generate_pdf_report(symbol, metrics, plot_base64)
            return FileResponse(pdf_buffer, as_attachment=True, filename=f"{symbol}_stock_report.pdf")


        return JsonResponse({
            'stock_symbol': symbol,
            'metrics': metrics,
            'plot_image': plot_base64,
            'predicted_prices': [
                {
                    'predicted_date': predicted_dates[i].strftime('%Y-%m-%d'),
                    'predicted_price': predicted_prices[i]
                } for i in range(len(predicted_prices))
            ]
        }, status=status.HTTP_200_OK)

