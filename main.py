from loader import bot
import handlers
from telebot.custom_filters import StateFilter
from utils.set_bot_commands import set_default_commands
from config_data import config
from flask import Flask, request
import requests
import telebot

LOCAL_ENV = config.LOCAL_ENV
WEBHOOK_URL = 'https://glinkin.pro'
BOT_TOKEN = config.BOT_TOKEN


def start_webhook():
    app = Flask(__name__)

    @app.route('/webhook_sublet', methods=['POST'])
    def webhook():
        update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
        bot.process_new_updates([update])
        return 'ok', 200

    def set_webhook():
        try:
            response = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={WEBHOOK_URL}/webhook_sublet')
            response.raise_for_status()
            print("Webhook set successfully:", response.json())
        except requests.exceptions.RequestException as e:
            print("Failed to set webhook:", e)

    set_webhook()
    app.run(host='0.0.0.0', port=5004)


if __name__ == "__main__":
    print(f"LOCAL_ENV value: {LOCAL_ENV}")
    bot.remove_webhook()
    bot.add_custom_filter(StateFilter(bot))
    set_default_commands(bot)

    if LOCAL_ENV == "local":
        bot.infinity_polling()
    else:
        start_webhook()
