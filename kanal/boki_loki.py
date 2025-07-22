import re
import parovi
from config import LOG_FILENAME
from id_kanal import id
import logging
logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',  # Dodaje [INFO] ili [ERROR]
    datefmt='%m/%d/%Y %I:%M:%S %p',
    filename=LOG_FILENAME,
    level=logging.INFO
)

def parse_signal(message,channel_id):
    try:
        
        signal_details = {}

        signal_pattern = r'(?i)\b(SELL|BUY)'
        sl_pattern = r"(?i)\bSl.*?(\d+\.\d+|\d\d+)|St.*?(\d+\.\d+|\d\d+)"
        trade_zone_pattern = r'\b(\d+\.\d+|\d+)'
        tp_pattern = r"(?i)\bTp.*?(\d+\.\d+|\d\d+)|Ta.*?(\d+\.\d+|\d\d+)"
        signal = re.search(signal_pattern, message, re.IGNORECASE)
        sl = re.search(sl_pattern,message, re.IGNORECASE)
        price = re.search(trade_zone_pattern, message, re.IGNORECASE)
        tp = re.findall(tp_pattern,message,re.IGNORECASE)

        match = None
        for substring in parovi.forex_pairs:
            if substring in message.upper():
                match = 'XAUUSD' if substring == 'GOLD' else substring.upper()
                break  # Exit only when a match is found
        # print(f"Match: {match}")
        # if any((match := substring)in message.upper() for substring in parovi.forex_pairs):
        #     if match == 'Gold' or match == 'GOLD':
        #         match = 'XAUUSD'
        signal_details['pair'] = match
        signal_details['signal'] = signal.group(1).upper()
        signal_details['price'] = float(price.group(1))
        signal_details['stop_loss'] = float(sl.group(1)) if sl.group(1) else float(sl.group(2))
        result_list=[]
        for rez in tp:
            for group in rez:
                if group:
                    result_list.append(float(group))
        signal_details["take_profit"] = result_list
        signal_details['comment'] = id[str(channel_id)]
        print("SIGNAL DETAILS: ",signal_details)

        if signal_details['pair'] and signal_details['signal']  and signal_details['take_profit'] and signal_details['stop_loss']:
            logging.info(f"SIGNAL: {signal_details}")
            return signal_details
        else:
            logging.error(f"PAIR: {signal_details['pair']} SIGNAL: {signal_details['signal']} PRICE: {signal_details['price']}, STPOP LOSS: {signal_details['stop_loss']} TAKE PROFIT: {signal_details['take_profit']}")
            logging.error(f"RETURN NONE FOR SIGNAL DETAILS {message}")
            return None

    except Exception as e:
        # print(f"Failed to parse signal. Error: {e}")
        return None