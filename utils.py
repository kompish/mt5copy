# utils.py
import kanal.boki_loki as boki_loki
import kanal.boki_test_loki as boki_test_loki
import kanal.m15premium as m15premium
import kanal.cjurefx as cjurefx
import re
import cv2
import pytesseract
import parovi
import logging
from config import LOG_FILENAME
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',  # Dodaje [INFO] ili [ERROR]
    datefmt='%m/%d/%Y %I:%M:%S %p',
    filename=LOG_FILENAME,
    level=logging.INFO
)
def process_image(image_path):
    """
    Process a given image to extract the currency pair.
    Uses OCR to read text from the image.
    """
    # Read and preprocess the image
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Convert to grayscale

    # OCR to extract text
    text = pytesseract.image_to_string(gray)
    # print("Text ",text)

    # Extract currency pair from the text
    match = re.search(r"([A-Z]{3} / [A-Z]{3})", text)
    if match:
        print("Match ",match)
    return match.group(1).replace(' / ', '') if match else ""
    

def parse_signal_channel_default(message):

    try:
        # lines = message.strip().split('\n')
        # trade_type, price = lines[0].split()  # First line should be trade type and price
        # tps = [float(line.split()[1]) for line in lines if line.startswith('TP')]  # Extract all TPs
        # sl_line = next(line for line in lines if line.startswith('SL'))
        # sl = float(sl_line.split()[1])
        # pair_match = re.search(r'([A-Z]{3} / [A-Z]{3})', sl_line)
        # pair = pair_match.group(1).replace(" / ","") if pair_match else ""
        
        signal_details = {}

        signal_pattern = r'(SELL|BUY)'
        sl_pattern = r"Sl.*?(\d+\.\d+|\d\d+)|St.*?(\d+\.\d+|\d\d+)"
        trade_zone_pattern = r'(\d+\.\d+|\d+)'
        tp_pattern = r"Tp.*?(\d+\.\d+|\d\d+)|Ta.*?(\d+\.\d+|\d\d+)"
        signal = re.search(signal_pattern, message, re.IGNORECASE)
        sl = re.search(sl_pattern,message, re.IGNORECASE)
        price = re.search(trade_zone_pattern, message, re.IGNORECASE)
        tp = re.findall(tp_pattern,message,re.IGNORECASE)


        if any((match := substring)in message.upper() for substring in parovi.forex_pairs):
            if match == 'Gold' or match == 'GOLD':
                match = 'XAUUSD'
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
        signal_details['comment'] = "M15 PREMIUM"

        
    except Exception as e:
        print(f"Failed to parse signal. Error: {e}")
        print('M15 Premium')
        return None



# channel_parsing_map = {
#     # Assuming the default channel ID is 1222448337
#     [-1002486504009,-1002464834753]: boki_loki.parse_signal,






#     # Add more channel IDs and their parsing functions as needed
# }

def parse_signal(message, channel_id):
    print('============================================================================================================================')
    print('PARSE SIGNAL FUNCTION')
    print(message,channel_id)
    print('============================================================================================================================')

    try:
        # parsing_function = channel_parsing_map.get(channel_id)
        return boki_loki.parse_signal(message,channel_id)
        
    except Exception as e:
        logging.error(f"Failed to parse signal for channel {channel_id}. Error: {e}")
        return None




