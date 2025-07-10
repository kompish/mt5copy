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
    mt5_path = r"C:\Program Files\MetaTrader 5\terminal64.exe"
    if not mt5.initialize(path=mt5_path):
        logging.error(f"Failed to initialize MT5. Error: {mt5.last_error()}")
        return False
    return True

def get_trade_group_id(comment):
    """Extract the base trade group ID from comment (e.g., '12345_TP2' -> '12345')"""
    parts = comment.split('_')
    if len(parts) > 1 and parts[1].startswith('TP'):
        return parts[0]
    return None

def update_trade_status():
    if not initialize_mt5():
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Get all open trades from database
        cursor.execute("SELECT ticket, comment, symbol FROM trades WHERE status = 'open'")
        open_trades = cursor.fetchall()
        
        # Create dictionary to group trades by their base ID
        trade_groups = {}
        
        for ticket, comment, symbol in open_trades:
            group_id = get_trade_group_id(comment)
            if not group_id:
                continue
                
            if group_id not in trade_groups:
                trade_groups[group_id] = []
            trade_groups[group_id].append((ticket, comment, symbol))
        
        # Process each trade group
        for group_id, trades in trade_groups.items():
            # Sort trades by TP level (assuming comment format is {group_id}_TP{level})
            sorted_trades = sorted(trades, key=lambda x: int(x[1].split('_TP')[1]))
            
            # Check status of each trade in order
            for i, (ticket, comment, symbol) in enumerate(sorted_trades):
                position = mt5.positions_get(ticket=ticket)
                
                if not position:  # Trade is closed
                    # Determine the new status based on TP level
                    tp_level = int(comment.split('_TP')[1])
                    
                    if tp_level == 1:
                        new_status = 'closed'
                    else:
                        # Check if all lower TP levels are closed
                        all_lower_closed = True
                        for lower_ticket, lower_comment, _ in sorted_trades[:i]:
                            cursor.execute("SELECT status FROM trades WHERE ticket = ?", (lower_ticket,))
                            lower_status = cursor.fetchone()[0]
                            if lower_status != 'closed':
                                all_lower_closed = False
                                break
                        
                        if all_lower_closed:
                            new_status = f'tp{tp_level-1}_closed'
                        else:
                            new_status = 'closed'
                    
                    # Update status in database
                    logging.info(f"Trade {ticket} ({comment}) closed. Updating status to {new_status}")
                    cursor.execute("UPDATE trades SET status = ? WHERE ticket = ?", (new_status, ticket))
        
        conn.commit()

    except Exception as e:
        logging.error(f"Error in trade status tracker: {e}")
        conn.rollback()

    finally:
        conn.close()
        mt5.shutdown()

if __name__ == "__main__":
    while True:
        update_trade_status()
        time.sleep(60)