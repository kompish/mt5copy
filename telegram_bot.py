import tzlocal
from telethon.sync import TelegramClient, events
from pytz import timezone as tz
import logging
import os
from datetime import datetime
from config import API_ID, API_HASH, TELEGRAM_CHANNEL, ALLOWED_USERS
from signal_handler import handle_signal
from utils import process_image

# Konfiguriši logovanje
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Inicijalizuj Telegram klijent
client = TelegramClient('anon', API_ID, API_HASH)

# Funkcija za logovanje poruka
def log_message(channel_name, message, timestamp, edit=False):
    try:
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"{channel_name}.log")
        edit_marker = "[EDITED]" if edit else ""
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {edit_marker} {message}\n")
    except Exception as e:
        logger.error(f"Failed to log message: {e}")

# Proveri da li poruka treba da se obradi
def should_process(event):
    # print(f"PRIMLJENA PORUKA: chat_id={event.chat_id}, sender_id={event.sender_id}, private={event.is_private}")
    try:
        if event.chat_id in TELEGRAM_CHANNEL:
            print("MATCH: TELEGRAM_CHANNEL")
            return True
        if event.is_private and event.sender_id in ALLOWED_USERS:
            print("MATCH: ALLOWED_USERS")
            return True
    except Exception as e:
        logger.error(f"Error in should_process: {e}")
    return False


# Novi događaji – nove poruke
@client.on(events.NewMessage)
async def new_message_handler(event):
    if should_process(event):
        await handle_message(event)

# Novi događaji – izmenjene poruke
@client.on(events.MessageEdited)
async def edited_message_handler(event):
    if should_process(event):
        await handle_message(event, edited=True)

# Glavna funkcija za obradu poruka
async def handle_message(event, edited=False):
    try:
        combined_text = event.message.text or ""
        if event.message.photo:
            media_folder = 'media'
            os.makedirs(media_folder, exist_ok=True)
            path = await event.message.download_media(file=media_folder)
            if path:
                currency_pair = process_image(path)
                if currency_pair:
                    combined_text += f" {currency_pair}"

        # Pretvori vreme u lokalnu vremensku zonu
        belgrade_tz = tzlocal.get_localzone()
        timestamp = event.message.date.astimezone(belgrade_tz).strftime('%Y-%m-%d %H:%M:%S')

        # Odredi ime chata za log
        if hasattr(event.chat, "title"):
            channel_name = event.chat.title
        elif hasattr(event.chat, "username"):
            channel_name = f"DM from @{event.chat.username}"
        else:
            channel_name = f"DM from {event.chat_id}"

        # Loguj i obradi
        log_message(channel_name, combined_text, timestamp, edit=edited)
        print("== NOVA PORUKA ==")
        print("Chat ID:", event.chat_id)
        print("Sender ID:", event.sender_id)
        print("Channel name:", channel_name)
        print("MESSAGE ID:", event.id)
        handle_signal(combined_text, event.message.chat_id, event.id,channel_name)

    except Exception as e:
        logger.error(f"Error handling message: {e}")

# Pokretanje Telegram bota
def start_telegram_bot():
    try:
        client.start()
        logger.info("Telegram bot started.")
        client.run_until_disconnected()
    except Exception as e:
        logger.error(f"Error starting Telegram bot: {e}")
