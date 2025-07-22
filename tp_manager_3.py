# tp_manager.py
import mysql.connector
import MetaTrader5 as mt5
import time
import logging
import re
from datetime import datetime, timedelta
from collections import defaultdict
from config import LOG_FILENAME_DB1
# main.py i tp_manager.py
from mt5_client import connect_to_mt5
# Config za MariaDB
DB_CONFIG = {
    "host": "",
    "user": "",         # ← prilagodi
    "password": "", # ← prilagodi
    "database": "trades"
}

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    filename=LOG_FILENAME_DB1,
    level=logging.INFO
)

def connect_db():
    return mysql.connector.connect(**DB_CONFIG)

def get_broker_time(symbol="XAUUSD"):
    tick = mt5.symbol_info_tick(symbol)
    if tick and tick.time:
        system_utc = datetime.utcnow()
        broker_time = datetime.fromtimestamp(tick.time)
        delta = broker_time - system_utc
        return datetime.now() + delta
    else:
        logging.warning(f"Nema tick podataka za simbol: {symbol}, koristim lokalno vreme.")
        return datetime.now()

def get_broker_time_hardcoded(offset_hours=1):
    return datetime.now() + timedelta(hours=offset_hours)

def get_closed_profit(ticket):
    broker_now = get_broker_time_hardcoded()
    
    now = datetime.now()
    now_1 = get_broker_time()
    print(f"BROKER TIME:{now_1},MY TIME:{now}")
    deals = mt5.history_deals_get(now_1 - timedelta(days=5), now_1 )
    if deals is None:
        logging.warning(f"Ne mogu da dobijem history_deals: {mt5.last_error()}")
        return None
    total_profit = 0
    found = False
    for deal in deals:
        # print(deal)
        if deal.position_id == ticket and deal.entry == mt5.DEAL_ENTRY_OUT:
            total_profit += deal.profit
            found = True
    return total_profit if found else None

def update_trade_status():
    if not connect_to_mt5():
        return

    conn = connect_db()
    cursor = conn.cursor()

    try:
        # 1. Ažuriraj statuse zatvorenih pozicija
        cursor.execute("""
            SELECT ticket, comment, status FROM trades_new_3 
            WHERE comment LIKE '%_TP%' AND status NOT IN ('profit', 'loss')
        """)
        all_tp_trades = cursor.fetchall()
        for ticket, comment, status in all_tp_trades:
            pos = mt5.positions_get(ticket=ticket)
            if not pos:
                profit = get_closed_profit(ticket)
                if profit is None:
                    logging.warning(f"Nije moguće pronaći deal za zatvoreni ticket {ticket}, postavljam status 'closed'.")
                    new_status = 'closed'
                elif profit > 0:
                    new_status = 'profit'
                else:
                    new_status = 'loss'

                logging.info(f"Pozicija {ticket} ({comment}) zatvorena, profit={profit}, status={new_status}.")
                cursor.execute("UPDATE trades_new_3 SET status = %s WHERE ticket = %s", (new_status, ticket))

        # 2. Grupisanje TP-ova po prefiksu
        cursor.execute("""
            SELECT ticket, comment, status, symbol FROM trades_new_3 
            WHERE comment LIKE '%_TP%' AND status NOT IN ('closed', 'profit', 'loss')
        """)
        rows = cursor.fetchall()

        grouped = defaultdict(list)
        for ticket, comment, status, symbol in rows:
            match = re.match(r"(.+)_TP(\d+)", comment)
            if not match:
                continue
            prefix, tp_num = match.groups()
            grouped[prefix].append((int(tp_num), ticket, comment, status, symbol))

        for prefix, trades in grouped.items():
            trades.sort()  # Sort po TP brojevima

            for i in range(len(trades) - 1):
                current_tp_num, current_ticket, current_comment, current_status, symbol = trades[i]
                next_tp_num, next_ticket, next_comment, next_status, _ = trades[i + 1]

                # Proveri da li je trenutni zatvoren
                cursor.execute("SELECT status FROM trades_new_3 WHERE ticket = %s", (current_ticket,))
                result = cursor.fetchone()
                if not result:
                    continue
                db_status = result[0]
                if db_status in ('profit', 'loss'):
                    next_pos = mt5.positions_get(ticket=next_ticket)
                    if next_pos:
                        tp_closed_status = f"tp{current_tp_num}_closed"
                        logging.info(f"TP{current_tp_num} zatvoren, postavljam status '{tp_closed_status}' za ticket {current_ticket}")
                        cursor.execute("UPDATE trades_new_3 SET status = %s WHERE ticket = %s", (tp_closed_status, current_ticket))

        conn.commit()

    except Exception as e:
        logging.error(f"Greška u tp_manager skripti: {e}")

    finally:
        conn.close()
        mt5.shutdown()

if __name__ == "__main__":
    while True:
        update_trade_status()
        time.sleep(60)
