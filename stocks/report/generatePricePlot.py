import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import base64
from io import BytesIO

def generate_price_plot(historical_prices, historical_dates, predicted_prices, predicted_dates):
    try:
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

        # Encode the plot as base64
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()
        plt.close()

        return image_base64
    except Exception as e:
        print(f"Error generating price plot: {str(e)}")
        return None
