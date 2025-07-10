# mt5_trader.py
from database import create_table, insert_trade
from datetime import datetime


import calculate_sl
from id_kanal import id
import lot_size
import MetaTrader5 as mt5
import logging
from ema import check_ema_conditions
from config import MT5_LOGIN, LOG_FILENAME
from trade_filter import is_trade_valid
logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',  # Dodaje [INFO] ili [ERROR]
    datefmt='%m/%d/%Y %I:%M:%S %p',
    filename=LOG_FILENAME,
    level=logging.INFO
)
import pandas as pd
def initialize_mt5():

    mt5_path = r"C:\Program Files\MetaTrader 5\terminal64.exe"  # path to the MT5 terminal
    if not mt5.initialize(path=mt5_path):
        error_msg = mt5.last_error()
        logging.error(f"Failed to initialize MT5. Error: {error_msg}")
        return False
    return True


def place_order(signal,channel_id,message_id):
    
    create_table()

    if not mt5.initialize():
        logging.error("MT5 not initialized or connection lost.")
        return
    
    # PROVERA FILTERA
    is_valid, vwap, macd = is_trade_valid(signal['pair'], signal['signal'])
    logging.info(f"Trade Filter Check: VWAP{vwap}, MACD{macd}")
    
    order_type = mt5.ORDER_TYPE_BUY if signal['signal'] == 'Buy' or signal['signal'] == 'BUY' else mt5.ORDER_TYPE_SELL
    print('++++++++++++++++++++++++++')
    print("checking price")
    selected = mt5.symbol_select(signal['pair'], True)
    if selected:
        price = mt5.symbol_info_tick(signal['pair']).ask if signal['signal'] == 'Buy' or signal['signal'] == 'BUY' else mt5.symbol_info_tick(signal['pair']).bid
    print(price)
    print("Filter:", is_valid,vwap,macd)
    account_info = mt5.account_info()
    symbol_info = mt5.symbol_info(signal['pair'])
    balance1 = account_info.balance
    total_volume = symbol_info.volume_min
    num_tps = len(signal['take_profit'])
    # split_volume = total_volume / num_tps
    # rounded_split_volume = round(split_volume,2)
    # lot = lot_size.calculate_lot_size(balance1,2,10,75)
    # calc_sl=calculate_sl.calculate_sl(price,signal['signal'],60,signal['pair'])
    # for tp in signal['take_profit']:
    # ema = ema_signal(signal['pair'], mt5.TIMEFRAME_H1)
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
            # 'comment': f"{id[str(channel_id)][:12]} TP{i}",
            'comment': f"{message_id}_TP{i+1}",
            'type_time': mt5.ORDER_TIME_GTC,
            'type_filling': mt5.ORDER_FILLING_IOC,
        }
        print("ORDER REQUEST: ",order_request,i)

        # check_ema_conditions(signal['pair'])
        # print(channel_id)
        # print(type(channel_id))


        try:
            result = mt5.order_send(order_request)  # Svaki nalog se odmah šalje
            
            if result is not None and result.retcode is not None:
                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    logging.error(f"Order {i} failed with error code {result.retcode}")
                else:
                    logging.info(f"Order {i} placed successfully: {result}")
                    trade_data = (
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
                    str(channel_id),                  # channel_id
                    str(message_id),                   # message_id
                    str(vwap),
                    str(macd),
                    str(is_valid)
                )
                    insert_trade(trade_data)
            else:
                last_error = mt5.last_error()
                logging.error(f"Order {i} send failed. Last error: {last_error}")
            
        except Exception as e:
            logging.error(f"An exception occurred for order {i}: {e}")
    
    print('=================================================================================')
    # print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    # print('=================================================================================')
    mt5.shutdown()
