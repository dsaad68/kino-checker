# %%

import os
# import re
import telebot
import logging

# from telebot import types

from my_logger import Logger

# from utils.answers import answer
# from bot.utils.call_parser import CallParser
from bot.utils.db_info_finder import FilmInfoFinder
from bot.utils.filters import filter_upcoming_films #, filter_showing_films

#%%
def get_or_raise(env_name: str) -> str:
    value = os.environ.get(env_name)
    if value is not None:
        return value
    else:
        raise ValueError(f"Missing environment variable {env_name}")

TOKEN = get_or_raise("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

upcoming_films_list = None
showing_films_list = None

# INFO: Works fine
@bot.message_handler(commands=["start", "restart"])
def send_welcome(message):
    """Sends a welcome message and show level 1 menu."""
    markup_start = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup_start.add(telebot.types.KeyboardButton("/Upcoming_Films"))
    # markup_start.add(telebot.types.KeyboardButton("/Showing_Films"))

    bot.reply_to(message, f"Howdy {message.from_user.first_name}, please choose from the list?", reply_markup=markup_start)

# INFO: Works fine
@bot.callback_query_handler(func=lambda call: call.data == "restart")
def restart(call):
    """Sends a welcome message and show level 1 menu."""
    markup_start = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup_start.add(telebot.types.KeyboardButton("/Upcoming_Films"))
    # markup_start.add(telebot.types.KeyboardButton("/Showing_Films"))

    bot.send_message(call.message.chat.id, "Please choose from the list?", reply_markup=markup_start)

# INFO: Works fine
@bot.message_handler(commands=["Upcoming_Films"])
def upcoming_films(message):
    """Shows the list of upcoming films."""

    films_list = db_info_finder.get_upcommings_films_list()
    global upcoming_films_list
    upcoming_films_list = films_list.copy()

    markup_films = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for film in upcoming_films_list:
        markup_films.add(telebot.types.KeyboardButton(film))

    bot.send_message(message.chat.id, "Choose a film:", reply_markup=markup_films)

# INFO: Works fine
# IDEA: User should be able to choose the version of the film
@bot.message_handler(func=lambda message: filter_upcoming_films(message, upcoming_films_list))
def track_upcommings_films(message):
    """Tracks the availability of upcoming films."""

    db_info_finder.upsert_users(message_id=str(message.message_id), chat_id=str(message.chat.id), title=message.text)
    bot.send_message(chat_id=message.chat.id, text="You will be informed when the tickets become available to buy.")

    global upcoming_films_list
    upcoming_films_list = None


# %%

if __name__ == "__main__":
    logger = Logger(file_handler=True)
    logger.get_logger()

    SQL_CONNECTION_URI = get_or_raise("POSTGRES_DB_CONNECTION_URI")

    db_info_finder = FilmInfoFinder(SQL_CONNECTION_URI)

    logging.info("----- Bot starts to run! -----")

    bot.infinity_polling()
