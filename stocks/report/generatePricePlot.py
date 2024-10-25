import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import os
from django.conf import settings  # Assuming this is a Django project and settings are imported

def generate_price_plot(historical_prices, historical_dates, predicted_prices, predicted_dates):
    try:
        # Print inputs for debugging
        print(f"Historical Prices: {historical_prices}")
        print(f"Historical Dates: {historical_dates}")
        print(f"Predicted Prices: {predicted_prices}")
        print(f"Predicted Dates: {predicted_dates}")
        
        # Plotting logic
        plt.figure(figsize=(10, 6))
        plt.plot(historical_dates, historical_prices, label='Actual Prices', color='blue')
        plt.plot(predicted_dates, predicted_prices, label='Predicted Prices', color='red', linestyle='--')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.title('Stock Price Prediction vs Actual')
        plt.legend()
        plt.grid(True)

        # Save the plot to a buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        # Save the image to a file in MEDIA_ROOT
        file_path = os.path.join(settings.MEDIA_ROOT, 'test_plot.png')
        with open(file_path, 'wb') as f:
            f.write(buffer.getvalue())  # Save to the specified path

        # Encode the plot as base64
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()
        plt.close()
        return image_base64
    except Exception as e:
        print(f"Error generating price plot: {str(e)}")
        return None, None
