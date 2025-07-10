import MetaTrader5 as mt5
import pandas as pd
import numpy as np

# Function to connect to MetaTrader 5
def connect_mt5():
    if not mt5.initialize():
        print("MetaTrader5 initialization failed. Error code:", mt5.last_error())
        return False
    print("MetaTrader5 initialized successfully.")
    return True

# Function to disconnect from MetaTrader 5
def disconnect_mt5():
    mt5.shutdown()
    print("Disconnected from MetaTrader 5.")

# Function to get historical data (OHLC)
def get_data(symbol, timeframe, n_bars=1000):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n_bars)
    if rates is None:
        print(f"Failed to retrieve data for {symbol} on {timeframe}. Error code: {mt5.last_error()}")
        return None
    
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df

# Function to calculate the EMA
def calculate_ema(df, period):
    return df['close'].ewm(span=period, adjust=False).mean()

# Function to check EMA conditions (this is the main function that checks the strategy)
def check_ema_conditions(symbol):
    # Get the latest data for both the daily and 1-hour timeframes
    df_daily = get_data(symbol, mt5.TIMEFRAME_D1)
    df_hourly = get_data(symbol, mt5.TIMEFRAME_H1)

    if df_daily is None or df_hourly is None:
        return

    # Calculate EMAs for daily and hourly charts
    df_daily['ema_50'] = calculate_ema(df_daily, 50)
    df_daily['ema_200'] = calculate_ema(df_daily, 200)
    df_hourly['ema_20'] = calculate_ema(df_hourly, 20)
    df_hourly['ema_50'] = calculate_ema(df_hourly, 50)

    # Get the most recent data (last row)
    last_daily = df_daily.iloc[-1]
    last_hourly = df_hourly.iloc[-1]

    # Check for buy/sell conditions
    if last_daily['ema_50'] > last_daily['ema_200'] and last_hourly['ema_20'] > last_hourly['ema_50']:
        print(f"Buy Signal: EMA 50 is above EMA 200 on daily chart and EMA 20 is above EMA 50 on 1-hour chart for {symbol}")
    elif last_daily['ema_50'] < last_daily['ema_200'] and last_hourly['ema_20'] < last_hourly['ema_50']:
        print(f"Sell Signal: EMA 50 is below EMA 200 on daily chart and EMA 20 is below EMA 50 on 1-hour chart for {symbol}")
    else:
        print(f"No clear signal: The conditions are not met for {symbol}")


