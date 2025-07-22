# signal_handler.py
from datetime import datetime
from id_kanal import id
from utils import parse_signal
from mt5_trader import place_order

def handle_signal(message, channel_id,message_id,channel_name):
    # print("kanal: ", id[str(channel_id)])
    # print("message: ",message)
    
    signal = parse_signal(message,channel_id)

    if signal:
        # print('=================================================================================')
        # print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        # print('=================================================================================')
        print(print(datetime.now().strftime("%d/%m/%Y %H:%M:%S")), signal)
        pair = signal['pair']
        # check_ema_conditions(pair)

        place_order(signal,channel_id,message_id,channel_name)
