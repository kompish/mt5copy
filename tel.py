import requests
import time

def send_telegram_message(message, bot_token, chat_id):
    send_text = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&parse_mode=Markdown&text={message}'
    response = requests.get(send_text)
    return response.json()

def main():
    bot_token = '6830249748:AAGcMzcsXSjvSd6Jz_G0dnayZiAu7pY7xYo'  # Replace with your Telegram bot token
    chat_id = '-1001543990393'      # Replace with your chat ID

    # Wait for internet connection (optional, useful for startup notifications)
    max_retries = 5
    for _ in range(max_retries):
        try:
            requests.get('https://www.google.com', timeout=5)
            break
        except requests.ConnectionError:
            time.sleep(5)

    # Send the notification
    send_telegram_message('Your PC is now active.', bot_token, chat_id)

if __name__ == "__main__":
    main()