# mt5_trader.py
import db_3
from id_kanal import id
import MetaTrader5 as mt5
import logging
from datetime import datetime
from new_filter import analyze_signal

from config import MT5_LOGIN, LOG_FILENAME
logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',  # Dodaje [INFO] ili [ERROR]
    datefmt='%m/%d/%Y %I:%M:%S %p',
    filename=LOG_FILENAME,
    level=logging.INFO
)
import pandas as pd
from mt5_client import connect_to_mt5


def place_order(signal,channel_id,message_id,channel_name):

    db_3.create_table()
    
    if not connect_to_mt5():
        logging.error("MT5 not initialized or connection lost.")
        return

    
    # PROVERA FILTERA
    result_filter = analyze_signal(signal['pair'],signal['signal'])
    ema_result = result_filter['status_ema']
    rsi_result = result_filter['status_rsi']
    mcad_result = result_filter['status_macd']
    vwap_result = result_filter['status_vwap']
    
    order_type = mt5.ORDER_TYPE_BUY if signal['signal'] == 'Buy' or signal['signal'] == 'BUY' else mt5.ORDER_TYPE_SELL
    print(f"order type {order_type}")
    price = mt5.symbol_info_tick(signal['pair']).ask if signal['signal'] == 'Buy' or signal['signal'] == 'BUY' else mt5.symbol_info_tick(signal['pair']).bid
    account_info = mt5.account_info()
    symbol_info = mt5.symbol_info(signal['pair'])
    balance1 = account_info.balance
    total_volume = symbol_info.volume_min
    num_tps = len(signal['take_profit'])
    print(f"Volume: {symbol_info.volume_min}")
    print(num_tps)
    for i in range(num_tps):
        order_request = {
            'action': mt5.TRADE_ACTION_DEAL,
            'symbol': signal['pair'],
            'volume': total_volume,  # Adjust as needed
            'type': order_type,
            'price': price,
            'sl': signal['stop_loss'],
            'tp': signal['take_profit'][i],
            'deviation': 20,
            'magic': int(str(channel_id)[3:]),
            'comment': f"{message_id}_TP{i+1}",
            'type_time': mt5.ORDER_TIME_GTC,
            'type_filling': mt5.ORDER_FILLING_IOC,
        }
        print("ORDER REQUEST: ",order_request,i)
        print(f"IME KANALA: {channel_name}")


        try:
            result = mt5.order_send(order_request)  # Svaki nalog se odmah šalje
            
            if result is not None and result.retcode is not None:
                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    logging.error(f"Order {i} failed with error code {result.retcode}")
                else:
                    logging.info(f"Order {i} placed successfully: {result}")
                    trade_data_3 = (
                    result.order,                     # ticket
                    signal['pair'],                   # symbol
                    total_volume,                     # volume
                    price,                            # price
                    signal['stop_loss'],              # sl
                    signal['take_profit'][i],         # tp
                    'BUY' if order_type == mt5.ORDER_TYPE_BUY else 'SELL',  # type
                    order_request['comment'],         # comment
                    signal['signal'],                 # signal_direction
                    datetime.now().isoformat(),       # timestamp
                    str(channel_id),
                    id[str(channel_id)],                  # channel_id
                    str(message_id),                   # message_id
                    str(vwap_result),
                    str(mcad_result),
                    str(rsi_result),
                    str(ema_result),
                    str("final_ok")
                )
                    db_3.insert_trade(trade_data_3)
            else:
                last_error = mt5.last_error()
                logging.error(f"Order {i} send failed. Last error: {last_error}")
            
        except Exception as e:
            logging.error(f"An exception occurred for order {i}: {e}")
    
    print('=================================================================================')
    mt5.shutdown()
