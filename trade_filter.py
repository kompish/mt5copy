import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime
import logging

def calculate_indicators(df):
    """Ručno izračunati indikatore"""
    try:
        # MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        # ATR
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        df['tr'] = np.maximum.reduce([high_low, high_close, low_close])
        df['atr'] = df['tr'].rolling(14).mean()
        
        # VWAP
        df['typical'] = (df['high'] + df['low'] + df['close']) / 3
        df['cumulative_volume'] = df['tick_volume'].cumsum()
        df['cumulative_tpv'] = (df['typical'] * df['tick_volume']).cumsum()
        df['vwap'] = df['cumulative_tpv'] / df['cumulative_volume']
        
        return df
    except Exception as e:
        logging.error(f"Error calculating indicators: {str(e)}")
        return df

def is_trade_valid(symbol, trade_type):
    """Provera uslova za trejd"""
    try:
        # Dobavi podatke
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 500)
        if rates is None:
            return False, "No data"
            
        df = pd.DataFrame(rates)
        df = calculate_indicators(df)
        
        if df.empty:
            return False, "Empty dataframe"
            
        # Trenutna cena
        current_price = mt5.symbol_info_tick(symbol).bid
        
        # Provera uslova
        last_row = df.iloc[-1]
        vwap_ok = current_price < last_row['vwap'] if trade_type == "SELL" else current_price > last_row['vwap']
        macd_ok = last_row['macd'] < last_row['signal'] if trade_type == "SELL" else last_row['macd'] > last_row['signal']
        vwap_message = "OK" if vwap_ok else "NOT OK"
        macd_message = "OK" if macd_ok else "NOT OK"
        message = f"VWAP: {'OK' if vwap_ok else 'NOT OK'}, MACD: {'OK' if macd_ok else 'NOT OK'}"
        return vwap_ok and macd_ok, vwap_message, macd_message
        
    except Exception as e:
        logging.error(f"Trade validation error: {str(e)}")
        return False, f"Error: {str(e)}"