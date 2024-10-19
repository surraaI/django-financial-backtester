from django.db import models
import pandas as pd

class StockData(models.Model):
    symbol = models.CharField(max_length=10)
    date = models.DateField()
    open_price = models.DecimalField(max_digits=10, decimal_places=2)
    high_price = models.DecimalField(max_digits=10, decimal_places=2)
    low_price = models.DecimalField(max_digits=10, decimal_places=2)
    close_price = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.BigIntegerField()
    moving_avg_50 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    moving_avg_200 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def calculate_moving_averages(self):
        stock_data = StockData.objects.filter(symbol=self.symbol).order_by('date')
        df = pd.DataFrame(list(stock_data.values('date', 'close_price')))
        df.set_index('date', inplace=True)
        
        df['moving_avg_50'] = df['close_price'].rolling(window=50).mean() if len(df) >= 50 else None
        df['moving_avg_200'] = df['close_price'].rolling(window=200).mean() if len(df) >= 200 else None

        df.dropna(inplace=True)  
        for date, row in df.iterrows():
            StockData.objects.filter(symbol=self.symbol, date=date).update(
                moving_avg_50=row['moving_avg_50'],
                moving_avg_200=row['moving_avg_200']
            )


    def save(self, *args, **kwargs):
        self.calculate_moving_averages()
        super().save(*args, **kwargs)
        
    class Meta:
        unique_together = ('symbol', 'date')
        indexes = [
            models.Index(fields=['symbol', 'date']),
        ]

    def __str__(self):
        return f"{self.symbol} - {self.date}"


class StockPricePrediction(models.Model):
    stock_symbol = models.CharField(max_length=10)
    prediction_date = models.DateField()
    predicted_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.symbol} - {self.prediction_date} - Predicted: {self.predicted_price}"
