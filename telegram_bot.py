import tzlocal
from telethon.sync import TelegramClient, events
from pytz import timezone as tz
import logging
import os
from datetime import datetime
from config import API_ID, API_HASH, TELEGRAM_CHANNEL, ALLOWED_USERS
from signal_handler import handle_signal
from utils import process_image
from prepoznavanje_2 import find_currency_pair
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

client = TelegramClient('anon', API_ID, API_HASH)

def log_message(channel_name, message, timestamp, edit=False):
    try:
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)  # Ensure the logs directory exists
        log_file = os.path.join(log_dir, f"{channel_name}.log")
        edit_marker = "[EDITED]" if edit else ""

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {edit_marker} {message}\n")
    except Exception as e:
        logger.error(f"Failed to log message: {e}")

@client.on(events.NewMessage(chats=TELEGRAM_CHANNEL))
async def new_message_handler(event):
    await handle_message(event)

@client.on(events.MessageEdited(chats=TELEGRAM_CHANNEL))
async def edited_message_handler(event):
    await handle_message(event, edited=True)

async def handle_message(event, edited=False):
    try:
        combined_text = event.message.text or ""  # Start with the caption or text of the message
        
        if event.message.photo:
            # Download the image
            media_folder = 'media'
            os.makedirs(media_folder, exist_ok=True)
            path = await event.message.download_media(file=media_folder)
            if path:
                # Extract currency pair from the image
                currency_pair = process_image(path)
                if not currency_pair:
                    currency_pair = find_currency_pair(path)
                if currency_pair:
                    combined_text += f" {currency_pair}"
        
        # Convert timestamp to local timezone
        belgrade_tz = tzlocal.get_localzone()
        timestamp = event.message.date.astimezone(belgrade_tz).strftime('%Y-%m-%d %H:%M:%S')

        # Determine channel name
        # channel_name = event.chat.title or event.chat.username or str(event.chat_id)
                # ISPRAVLJEN DEO - Provera tipa chata
        if hasattr(event.chat, "title"):  # Ako je grupa ili kanal
            channel_name = event.chat.title  # <-- ISPRAVLJENO
        elif hasattr(event.chat, "username"):  # Ako je privatni chat i ima username
            channel_name = f"DM from @{event.chat.username}"  # <-- ISPRAVLJENO
        else:  # Ako nema username-a, koristi ID
            channel_name = f"DM from {event.chat_id}"  # <-- ISPRAVLJENO
        # Log the message
        log_message(channel_name, combined_text, timestamp, edit=edited)
        print(event.message.chat_id, channel_name)
        # Handle the message
        print("Id poruke: ",event.id)
        handle_signal(combined_text, event.message.chat_id, event.id)
    except Exception as e:
        logger.error(f"Error handling message: {e}")

def start_telegram_bot():
    try:
        client.start()
        logger.info("Telegram bot started.")
        client.run_until_disconnected()
    except Exception as e:
        logger.error(f"Error starting Telegram bot: {e}")
