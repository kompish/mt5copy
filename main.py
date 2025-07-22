# main.py
import os
from telegram_bot import start_telegram_bot
# from mt5_trader import initialize_mt5
# main.py i tp_manager.py
from mt5_client import connect_to_mt5
import logging
from config import LOG_FILENAME
logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',  # Dodaje [INFO] ili [ERROR]
    datefmt='%m/%d/%Y %I:%M:%S %p',
    filename=LOG_FILENAME,
    level=logging.INFO
)
if __name__ == '__main__':
    if connect_to_mt5():
        logging.info("Starting the Telegram bot...")
        os.system('cls')
        start_telegram_bot()
