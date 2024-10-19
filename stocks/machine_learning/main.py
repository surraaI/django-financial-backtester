from .data import prepare_data
from .saveTrainedMachine import save_model
from .train import train_model
from .yFinance import get_historical_data


if __name__ == "__main__":
    symbol = 'AAPL'
    data = get_historical_data(symbol, period='1y')
    X, y = prepare_data(data)
    model = train_model(X, y)
    save_model(model, 'stock_price_model.pkl')
