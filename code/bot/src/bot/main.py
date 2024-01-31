# %%

import os
# import re
import telebot
import logging

from telebot import types

from my_logger import Logger

# from utils.answers import answer
from bot.utils.call_parser import CallParser
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

    films_list = db_info_finder.get_upcomings_films_list()
    films_dict = {film['title'].lower(): film['upcoming_film_id'] for film in films_list}

    global upcoming_films_dict
    upcoming_films_dict = films_dict.copy()

    upcoming_films_list = list(upcoming_films_dict.keys())

    markup_films = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for film in upcoming_films_list:
        markup_films.add(telebot.types.KeyboardButton(film))

    bot.send_message(message.chat.id, "Choose a film:", reply_markup=markup_films)

@bot.message_handler(func=lambda message: filter_upcoming_films(message, upcoming_films_list))
def upcoming_films_ov_filter(message):
    """Inline keyboard for filtering upcoming films based on OV availability."""

    film_id = db_info_finder.get_film_id_by_title(message.text)

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='✅ Yes', callback_data=f'{film_id},uf|1,ov'))
    keyboard.add(types.InlineKeyboardButton(text='⛔ No', callback_data=f'{film_id},uf|0,ov'))
    keyboard.add(types.InlineKeyboardButton(text="🤷 Doesn't matter", callback_data=f'{film_id},uf|2,ov'))
    # Fix Go back button
    keyboard.add(types.InlineKeyboardButton(text="🔙 Restart!", callback_data="restart"))

    bot.send_message(message.chat.id, "Are you looking for OV Version?", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.endswith(('ov')))
def upcoming_films_imax_filter_callback(call):
    """Inline keyboard for filtering upcoming films based on IMAX availability."""

    logging.info(f"Call Data: {call.data}")

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='✅ Yes', callback_data=f'{call.data}|1,imax'))
    keyboard.add(types.InlineKeyboardButton(text='⛔ No', callback_data=f'{call.data}|0,imax'))
    keyboard.add(types.InlineKeyboardButton(text="🤷 Doesn't matter", callback_data=f'{call.data}|2,imax'))
    keyboard.add(types.InlineKeyboardButton(text="🔙 Restart!", callback_data="restart"))

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Are you looking for IMAX Version?", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.endswith(('imax')))
def upcoming_films_3d_filter_callback(call):

    logging.info(f"Call Data: {call.data}")

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='✅ Yes', callback_data=f'{call.data}|1,3d'))
    keyboard.add(types.InlineKeyboardButton(text='⛔ No', callback_data=f'{call.data}|0,3d'))
    keyboard.add(types.InlineKeyboardButton(text="🤷 Doesn't matter", callback_data=f'{call.data}|2,3d'))
    keyboard.add(types.InlineKeyboardButton(text="🔙 Restart!", callback_data="restart"))

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Are you looking for 3D Version?", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.endswith(('3d')))
def track_upcommings_films(call):
    """Tracks the availability of upcoming films."""

    logging.info(f"Call Data: {call.data}")

    input_dict = CallParser.parse_for_input(call.data)

    film_title = upcoming_films_dict.get(input_dict.get('uf'))

    # fix this
    db_info_finder.upsert_users(message_id=str(call.message.message_id), chat_id=str(call.message.chat.id), title=film_title, flags=input_dict.get('flags'))
    bot.send_message(chat_id=call.message.chat.id, text="You will be informed when the tickets become available to buy.")

    global upcoming_films_dict
    upcoming_films_dict = None


# %%

if __name__ == "__main__":
    logger = Logger(file_handler=True)
    logger.get_logger()

    SQL_CONNECTION_URI = get_or_raise("POSTGRES_DB_CONNECTION_URI")

    db_info_finder = FilmInfoFinder(SQL_CONNECTION_URI)

    logging.info("----- Bot starts to run! -----")

    bot.infinity_polling()
