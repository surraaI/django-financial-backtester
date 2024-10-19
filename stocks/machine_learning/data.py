import numpy as np

def prepare_data(prices_df):
    """
    Prepare data for machine learning training.
    X: Time steps (index)
    y: Closing stock prices
    """
    prices_df['Day'] = np.arange(len(prices_df))  
    X = prices_df[['Day']].values  
    y = prices_df['Close'].values 
    
    return X, y
