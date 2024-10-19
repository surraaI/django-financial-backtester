import pickle
import os

model_path = os.path.join(os.path.dirname(__file__), '../stock_price_model.pkl')

def load_model(model_path=model_path):
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    return model
