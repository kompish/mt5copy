# database.py
import sqlite3

def connect_db():
    conn = sqlite3.connect("trades.db")
    return conn

def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket INTEGER,
            symbol TEXT,
            volume REAL,
            price REAL,
            sl REAL,
            tp REAL,
            order_type TEXT,
            comment TEXT,
            signal_direction TEXT,
            timestamp TEXT,
            channel_id TEXT,
            message_id TEXT,
            status TEXT DEFAULT 'open',
            VWAP,
            MCAD,
            FILTER
        )
    """)
    conn.commit()
    conn.close()

def insert_trade(trade_data):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO trades (
            ticket, symbol, volume, price, sl, tp, order_type, comment,
            signal_direction, timestamp, channel_id, message_id,VWAP,MACD,FILTER
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, trade_data)
    conn.commit()
    conn.close()
