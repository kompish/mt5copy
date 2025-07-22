# mt5_client.py
import MetaTrader5 as mt5

def connect_to_mt5():
    if not mt5.initialize():
        raise ConnectionError("MT5 konekcija nije uspela")
    return mt5