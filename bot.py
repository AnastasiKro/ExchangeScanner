import telebot
import time
import asyncio
from main import scan_exchanges
bot = telebot.TeleBot('8471391916:AAGqNRJQ1n2yIEIo0QUIHc8ZHp5bdM7c5cA')

def scan_exchanges_sync():
    return asyncio.run(scan_exchanges())

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Start":
        for i in range (600):
            found = scan_exchanges_sync()
            if found:
                for symbol in found:
                    bot.send_message(message.from_user.id, f"{symbol} {found[symbol]}")

    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Send 'Start' to start scanning")
    else:
        bot.send_message(message.from_user.id, "Command not found. Send /help.")

bot.polling(none_stop=True, interval=0)
