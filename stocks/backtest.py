import pandas as pd

def backtest_strategy(initial_investment, prices, short_window=50, long_window=200):
    df = pd.DataFrame(prices, columns=['price'])
    df['short_mavg'] = df['price'].rolling(window=short_window, min_periods=1).mean()
    df['long_mavg'] = df['price'].rolling(window=long_window, min_periods=1).mean()

    cash = initial_investment
    holdings = 0
    peak_value = initial_investment
    max_drawdown = 0
    transactions = []

    for i in range(len(df)):
        price = float(df['price'].iloc[i])
        short_mavg = float(df['short_mavg'].iloc[i])
        long_mavg = float(df['long_mavg'].iloc[i])

        # Buy condition: when short-term moving average crosses above long-term
        if short_mavg > long_mavg and cash >= price:
            holdings += 1
            cash -= price
            transactions.append(('buy', i, price))

        # Sell condition: when price is greater than the long-term moving average
        elif price > long_mavg and holdings > 0:
            holdings -= 1
            cash += price
            transactions.append(('sell', i, price))

        portfolio_value = cash + holdings * price
        peak_value = max(peak_value, portfolio_value)
        drawdown = (peak_value - portfolio_value) / peak_value
        max_drawdown = max(max_drawdown, drawdown)

    final_value = cash + holdings * df['price'].iloc[-1]
    total_return = (final_value - initial_investment) / initial_investment * 100

    performance_summary = {
        'total_return': total_return,
        'max_drawdown': max_drawdown * 100,
        'number_of_trades': len(transactions)
    }

    return final_value, transactions, performance_summary
