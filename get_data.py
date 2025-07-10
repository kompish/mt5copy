import MetaTrader5 as mt5
import pandas as pd
import os
from datetime import datetime
os.system('cls')
def download_mt5_data(symbol, timeframe=mt5.TIMEFRAME_H1, 
                      start_date=None, end_date=None,
                      data_folder='historical_data'):
    """
    Preuzima istorijske podatke iz MT5 za dati simbol i timeframe,
    i čuva ih kao CSV u folderu data_folder.
    
    timeframe: mt5.TIMEFRAME_H1, mt5.TIMEFRAME_M1, itd.
    start_date, end_date: datetime objekti ili None (preuzme maksimalno dostupno)
    """
    
    if not mt5.initialize():
        raise RuntimeError("MT5 nije moguće inicijalizovati")
    
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    
    utc_from = None
    utc_to = None
    if start_date:
        utc_from = datetime(start_date.year, start_date.month, start_date.day)
    if end_date:
        utc_to = datetime(end_date.year, end_date.month, end_date.day)
    
    # Preuzimamo maksimalno 100000 barova po zahtevu
    # Ako start_date i end_date nisu dati, MT5 vrati poslednje dostupne barove
    rates = mt5.copy_rates_range(symbol, timeframe, utc_from, utc_to) if utc_from and utc_to else \
            mt5.copy_rates_from_pos(symbol, timeframe, 0, 100000)
    
    if rates is None or len(rates) == 0:
        raise ValueError(f"Nema dostupnih podataka za simbol {symbol} u zadatom opsegu")
    
    df = pd.DataFrame(rates)
    
    # Pretvaramo vreme iz timestamp u datetime
    df['datetime'] = pd.to_datetime(df['time'], unit='s')
    
    # Redosled kolona (možeš prilagoditi kako želiš)
    df = df[['datetime', 'open', 'high', 'low', 'close', 'tick_volume', 'spread', 'real_volume']]
    
    # Čuvamo u CSV fajl
    file_path = os.path.join(data_folder, f"{symbol}.csv")
    df.to_csv(file_path, index=False)
    print(f"Podaci za {symbol} su sačuvani u {file_path}")
    
    mt5.shutdown()

if __name__ == "__main__":
    # symbols_to_download = ['AUDCAD','AUDCHF','AUDJPY','AUDNZD','AUDUSD','CADCHF','CADJPY','CHFJPY','EURAUD','EURCAD','EURCHF','EURGBP',
    #                        'EURJPY','EURNZD','EURUSD','GBPAUD','GBPJPY','GBPNZD','GBPUSD','NZDCAD','NZDCHF','NZDJPY',
    #                        'NZDUSD','USDCAD','USDCHF','USDJPY']  # Dodaj simbole koje želiš.
    symbols_to_download = ['GBPNZD']
    timeframe = mt5.TIMEFRAME_M1  # 1-satni timeframe (možeš promeniti)
    
    # Opcionalno - period preuzimanja
    start_date = datetime(2025, 5, 18)
    end_date = datetime(2025, 5, 23)
    
    for sym in symbols_to_download:
        try:
            print(f"Preuzimam podatke za {sym}...")
            download_mt5_data(sym, timeframe, start_date, end_date)
        except Exception as e:
            print(f"Greška prilikom preuzimanja za {sym}: {e}")
