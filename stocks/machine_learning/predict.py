import pickle

import numpy as np

from stocks.machine_learning.main import X


def load_model(model_path='stock_price_model.pkl'):
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    return model

def predict_next_days(model, days_in_future=30):
    last_day = X[-1][0]  
    future_days = np.arange(last_day + 1, last_day + days_in_future + 1).reshape(-1, 1)
    
    predicted_prices = model.predict(future_days)
    return predicted_prices

if __name__ == "__main__":
    model = load_model('stock_price_model.pkl')

    predictions = predict_next_days(model, 30)
    print("Predicted Prices for the next 30 days:", predictions)
