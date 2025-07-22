# database.py
import mysql.connector

DB_CONFIG = {
    "host": "",
    "user": "",         # ← promeni
    "password": "", # ← promeni
    "database": "trades"      # ← kreiraj ovu bazu ako ne postoji
}

def connect_db():
    return mysql.connector.connect(**DB_CONFIG)

def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades_new_3 (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ticket INT,
            symbol VARCHAR(50),
            volume DOUBLE,
            price DOUBLE,
            sl DOUBLE,
            tp DOUBLE,
            order_type VARCHAR(10),
            comment TEXT,
            signal_direction VARCHAR(10),
            timestamp DATETIME,
            channel_id VARCHAR(50),
            channel_name VARCHAR(50),
            message_id VARCHAR(50),
            status VARCHAR(10) DEFAULT 'open',
            VWAP TEXT,
            MACD TEXT,
            RSI TEXT,
            EMA50 TEXT,
            FILTER TEXT DEFAULT "None"
        )
    """)
    conn.commit()
    conn.close()

def insert_trade(trade_data):
    if len(trade_data) != 18:
        raise ValueError("Expected 18 fields in trade_data")
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO trades_new_3 (
            ticket, symbol, volume, price, sl, tp, order_type, comment,
            signal_direction, timestamp, channel_id, channel_name, message_id, VWAP, MACD, RSI, EMA50, FILTER
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, trade_data)
    conn.commit()
    conn.close()
