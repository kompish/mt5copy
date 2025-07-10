import sqlite3
import MetaTrader5 as mt5
import time
import logging
from config import DB_PATH, LOG_FILENAME_DB

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    filename=LOG_FILENAME_DB,
    level=logging.INFO
)

def initialize_mt5():
    mt5_path = r"C:\Program Files\MetaTrader 5\terminal64.exe"  # putanja MT5
    if not mt5.initialize(path=mt5_path):
        logging.error(f"Failed to initialize MT5. Error: {mt5.last_error()}")
        return False
    return True

def update_trade_status():
    if not initialize_mt5():
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 1. TP1 zatvoren -> status = 'closed'
        cursor.execute("""
            SELECT ticket, comment, symbol FROM trades WHERE comment LIKE '%_TP1' AND status = 'open'
        """)
        tp1_trades = cursor.fetchall()
        for ticket, comment, symbol in tp1_trades:
            position = mt5.positions_get(ticket=ticket)
            if not position:
                # pozicija zatvorena
                logging.info(f"TP1 trade {ticket} zatvoren, menjam status u closed.")
                cursor.execute("UPDATE trades SET status = 'closed' WHERE ticket = ?", (ticket,))

        # 2. TP2 zatvoren -> status = 'tp2_closed' i pomeri TP3 SL na current price
        cursor.execute("""
            SELECT t1.ticket, t1.comment, t1.symbol, t1.sl FROM trades t1
            JOIN trades t2 ON SUBSTR(t1.comment, 1, INSTR(t1.comment, '_') - 1) = SUBSTR(t2.comment, 1, INSTR(t2.comment, '_') - 1)
            WHERE t1.comment LIKE '%_TP3' AND t1.status = 'open' AND t2.comment LIKE '%_TP2' AND t2.status = 'open'
        """)
        rows = cursor.fetchall()

        for tp3_ticket, tp3_comment, symbol, old_sl in rows:
            # Pronađi TP2 ticket sa istim ID i statusom open
            cursor.execute("""
                SELECT ticket FROM trades 
                WHERE comment LIKE ? AND status = 'open'
            """, (tp3_comment.replace('_TP3', '_TP2'),))
            tp2_ticket = cursor.fetchone()
            if not tp2_ticket:
                continue
            tp2_ticket = tp2_ticket[0]

            # Proveri da li je TP2 zatvoren
            position_tp2 = mt5.positions_get(ticket=tp2_ticket)
            if position_tp2:
                continue  # jos uvek otvoren

            # TP2 zatvoren, update status i pomeri SL TP3
            logging.info(f"TP2 trade {tp2_ticket} zatvoren, menjam status i pomeram SL za TP3 trade {tp3_ticket}.")

            # Dohvati current price za symbol
            tick = mt5.symbol_info_tick(symbol)
            if not tick:
                logging.error(f"Ne mogu dobiti tick za {symbol}")
                continue
            
            # Nadji poziciju TP3 i update SL
            positions_tp3 = mt5.positions_get(ticket=tp3_ticket)
            if not positions_tp3:
                logging.info(f"TP3 trade {tp3_ticket} je zatvoren ili ne postoji.")
                cursor.execute("UPDATE trades SET status = 'closed' WHERE ticket = ?", (tp3_ticket,))
                continue
            
            pos_tp3 = positions_tp3[0]
            # Odredi novi SL price (trenutna cena, koristimo ask za buy, bid za sell)
            # if pos_tp3.type == mt5.ORDER_TYPE_BUY:
            #     new_sl = tick.ask
            # else:
            #     new_sl = tick.bid
            new_sl = pos_tp3.price_open

            # Napravi zahtev za modifikaciju pozicije TP3
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "position": tp3_ticket,
                "sl": new_sl,
                "tp": pos_tp3.tp,
                "symbol": symbol,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            result = mt5.order_send(request)
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logging.info(f"SL za TP3 trade {tp3_ticket} pomeren na {new_sl}")
                # Update status TP2 u 'tp2_closed' i TP3 ostaje open sa novim SL
                cursor.execute("UPDATE trades SET status = 'tp2_closed' WHERE ticket = ?", (tp2_ticket,))
            else:
                logging.error(f"Neuspešno pomeranje SL za TP3 trade {tp3_ticket}: {result.retcode}")

        # 3. TP3 zatvoren -> status = 'closed'
        cursor.execute("""
            SELECT ticket FROM trades WHERE comment LIKE '%_TP3' AND status = 'open'
        """)
        tp3_open_trades = cursor.fetchall()
        for ticket_tuple in tp3_open_trades:
            ticket = ticket_tuple[0]
            pos = mt5.positions_get(ticket=ticket)
            if not pos:
                logging.info(f"TP3 trade {ticket} zatvoren, menjam status u closed.")
                cursor.execute("UPDATE trades SET status = 'closed' WHERE ticket = ?", (ticket,))
        
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
