from django.urls import path
from .views import backtest_view, fetch_stock_data_view, PredictStockView, GenerateStockReportView

urlpatterns = [
    path('fetch-stock-data/', fetch_stock_data_view, name='fetch_stock_data'),
    path('backtest/', backtest_view, name='backtest'),
    path('predict/<str:symbol>/', PredictStockView.as_view(), name='predict_stock'),
    path('report/<str:symbol>/', GenerateStockReportView.as_view(), name='stock-report'),
]
