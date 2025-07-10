def calculate_sl(price, signal, pips, currency_pair):
    jpy_pairs = ['JPY', 'JPY/XXX', 'AUD/JPY', 'CAD/JPY', 'CHF/JPY', 'EUR/JPY', 'GBP/JPY', 'NZD/JPY', 'USD/JPY']  # Add other JPY pairs if needed
    currency_pair = currency_pair.upper()

    if len(currency_pair) == 6:  # Handle pairs without separator (e.g., CADJPY)
        base_currency = currency_pair[:3]
        quote_currency = currency_pair[3:]
    else:
        base_currency = currency_pair.split('/')[0]
        quote_currency = currency_pair.split('/')[1]

    print("Analyzing currency pair:", currency_pair)

    if base_currency == 'JPY' or quote_currency == 'JPY' or currency_pair in jpy_pairs:
        pip_value = 0.01
        print("JPY pair recognized. Pip value is 0.01.")
    else:
        pip_value = 0.0001
        print("Non-JPY pair recognized. Pip value is 0.0001.")

    if signal.lower() == 'buy':
        sl_price = price - pips * pip_value
    elif signal.lower() == 'sell':
        sl_price = price + pips * pip_value
    else:
        raise ValueError("Invalid signal. Please provide 'buy' or 'sell'.")

    return sl_price

