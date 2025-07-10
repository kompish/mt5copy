import re

def parse_signal_channel_1832164233(message):
    try:
        # Replace 'Gold' with 'XAUUSD'
        message = message.replace('Gold', 'XAUUSD', 1)

        # Initialize a dictionary to hold our parsed data
        signal_details = {'pair': 'XAUUSD'}

        # Regular expression patterns
        trade_zone_pattern = r'XAUUSD (Buy|Sell) Zone @ (\d+\.\d+) - (\d+\.\d+)'
        sl_pattern = r'sl (\d+\.\d+)'
        tp_pattern = r'tp (\d+\.\d+)'

        # Extract the trade type and zone
        trade_zone_match = re.search(trade_zone_pattern, message, re.IGNORECASE)
        if trade_zone_match:
            signal_details['trade_type'] = trade_zone_match.group(1).upper()
            # Calculate the average price as the center of the buy/sell zone
            zone_start = float(trade_zone_match.group(2))
            zone_end = float(trade_zone_match.group(3))
            signal_details['price'] = (zone_start + zone_end) / 2

        # Extract the stop loss
        sl_match = re.search(sl_pattern, message, re.IGNORECASE)
        if sl_match:
            signal_details['stop_loss'] = float(sl_match.group(1))

        # Extract take profits
        tp_matches = re.findall(tp_pattern, message, re.IGNORECASE)
        if tp_matches:
            signal_details['take_profits'] = [float(tp) for tp in tp_matches]

        # Check if all necessary details were found
        if 'trade_type' in signal_details and 'price' in signal_details and 'stop_loss' in signal_details and 'take_profits' in signal_details:
            return signal_details
        else:
            return None

    except Exception as e:
        print(f"Failed to parse signal. Error: {e}")
        return None

rez=parse_signal_channel_1832164233('''Gold Buy Zone @ 1964.5 - 1961.5

sl 1958.5

tp 1965.5
tp 1967.5
tp 1974.5''')

print(rez)