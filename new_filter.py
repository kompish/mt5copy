import pandas as pd
import numpy as np
import MetaTrader5 as mt5
# main.py i tp_manager.py
from mt5_client import connect_to_mt5


# === Inicijalizacija MT5 ===
def initialize_mt5():
    if not mt5.initialize():
        print("Greška pri inicijalizaciji MT5")
        return False
    return True

def shutdown_mt5():
    mt5.shutdown()

# === Dohvatanje podataka ===
def get_historical_data(symbol, timeframe, num_bars):
    if not connect_to_mt5():
        return None

    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, num_bars)
    # shutdown_mt5()

    if rates is None:
        print("Greška pri dobijanju podataka")
        return None

    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    return df

# === EMA ===
def calculate_ema(data, period, column='close'):
    return data[column].ewm(span=period, adjust=False).mean()

# === RSI ===
def calculate_rsi(data, period=14, column='close'):
    delta = data[column].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# === MACD ===
def calculate_macd(data, fast=12, slow=26, signal=9, column='close'):
    ema_fast = calculate_ema(data, fast, column)
    ema_slow = calculate_ema(data, slow, column)
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

# === VWAP ===
def calculate_vwap(data):
    cumulative_price_volume = (data['close'] * data['tick_volume']).cumsum()
    cumulative_volume = data['tick_volume'].cumsum()
    return cumulative_price_volume / cumulative_volume

# === Glavna funkcija za dobijanje statusa signala ===
def analyze_signal(symbol, signal_type):
    tf_map = {
        "D1": mt5.TIMEFRAME_D1,
        "H4": mt5.TIMEFRAME_H4,
        "H1": mt5.TIMEFRAME_H1,
    }

    # Preuzimanje podataka
    data_d1 = get_historical_data(symbol, tf_map["D1"], 300)
    data_h4 = get_historical_data(symbol, tf_map["H4"], 300)
    data_h1 = get_historical_data(symbol, tf_map["H1"], 300)

    if data_d1 is None or data_h4 is None or data_h1 is None:
        return None

    # EMA
    ema_200_d1 = calculate_ema(data_d1, 200).iloc[-1]
    ema_200_h4 = calculate_ema(data_h4, 200).iloc[-1]
    ema_200_h1 = calculate_ema(data_h1, 200).iloc[-1]
    ema_50_h4 = calculate_ema(data_h4, 50).iloc[-1]
    ema_50_h1 = calculate_ema(data_h1, 50).iloc[-1]

    close_h1 = data_h1['close'].iloc[-1]

    # RSI
    rsi_h1 = calculate_rsi(data_h1).iloc[-1]

    # MACD
    macd_line, signal_line, hist = calculate_macd(data_h1)
    macd_val = macd_line.iloc[-1]
    macd_sig = signal_line.iloc[-1]

    # VWAP
    vwap_h1 = calculate_vwap(data_h1).iloc[-1]

    # === Pravila filtriranja ===
    if signal_type.lower() == "buy":
        status_ema = "OK" if (ema_50_h4 > ema_200_h4 and ema_50_h1 > ema_200_h1 and close_h1 > ema_200_d1) else "NOT_OK"
        status_rsi = "OK" if rsi_h1 > 45 and rsi_h1 < 70 else "NOT_OK"
        status_macd = "OK" if macd_val > macd_sig else "NOT_OK"
        status_vwap = "OK" if close_h1 > vwap_h1 else "NOT_OK"
    elif signal_type.lower() == "sell":
        status_ema = "OK" if (ema_50_h4 < ema_200_h4 and ema_50_h1 < ema_200_h1 and close_h1 < ema_200_d1) else "NOT_OK"
        status_rsi = "OK" if rsi_h1 < 55 and rsi_h1 > 30 else "NOT_OK"
        status_macd = "OK" if macd_val < macd_sig else "NOT_OK"
        status_vwap = "OK" if close_h1 < vwap_h1 else "NOT_OK"
    else:
        return None

    # === Vraćanje vrednosti i statusa za bazu ===
    result = {
        "symbol": symbol,
        "signal": signal_type.upper(),

        "ema_200_d1": float(ema_200_d1),
        "ema_200_h4": float(ema_200_h4),
        "ema_200_h1": float(ema_200_h1),
        "ema_50_h4": float(ema_50_h4),
        "ema_50_h1": float(ema_50_h1),
        "close_h1": float(close_h1),

        "rsi_h1": float(rsi_h1),
        "macd_line": float(macd_val),
        "macd_signal": float(macd_sig),
        "vwap_h1": float(vwap_h1),

        "status_ema": status_ema,
        "status_rsi": status_rsi,
        "status_macd": status_macd,
        "status_vwap": status_vwap
    }

    return result

# === Primer upotrebe ===
if __name__ == "__main__":
    signal_data = analyze_signal("EURUSD", "sell")
    # if signal_data:
    print("EMA STATUS",signal_data["status_ema"])
    print("VWAP STATUS", signal_data["status_vwap"])
    print("STATUS MACD", signal_data["status_macd"])
    print("STATUS RSI",signal_data["status_rsi"])
