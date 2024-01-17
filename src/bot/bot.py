# %%

import os
import re
import telebot
import logging

from telebot import types

from my_logger import Logger

# from utils.answers import answer
from utils.call_parser import CallParser
from utils.db_info_finder import FilmInfoFinder
from utils.filters import filter_upcoming_films, filter_showing_films

#%%
def get_or_raise(env_name: str) -> str:
    value = os.environ.get(env_name)
    if value is not None:
        return value
    else:
        raise ValueError(f"Missing environment variable {env_name}")

TOKEN = get_or_raise("ZKM_TRACKER_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

upcoming_films_list = None
showing_films_list = None

# INFO: Works fine
@bot.message_handler(commands=["start", "restart"])
def send_welcome(message):
    """Sends a welcome message and show level 1 menu."""
    markup_start = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup_start.add(telebot.types.KeyboardButton("/Upcoming_Films"))
    markup_start.add(telebot.types.KeyboardButton("/Showing_Films"))

    bot.reply_to(message, f"Howdy {message.from_user.first_name}, please choose from the list?", reply_markup=markup_start)

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
@bot.message_handler(func=lambda message: filter_upcoming_films(message, upcoming_films_list))
def track_upcommings_films(message):
    """Tracks the availability of upcoming films."""

    db_info_finder.upsert_users(message_id=str(message.message_id), chat_id=str(message.chat.id), title=message.text)
    bot.send_message(chat_id=message.chat.id, text="You will be informed when the tickets become available to buy.")

    global upcoming_films_list
    upcoming_films_list = None

# INFO: Works fine
@bot.message_handler(commands=["Showing_Films"])
def showing_films(message):
    """Shows the list of showing films."""

    films_list = db_info_finder.get_showing_films_list()
    global showing_films_list
    showing_films_list = films_list.copy()

    markup_films = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for film in showing_films_list:
        markup_films.add(telebot.types.KeyboardButton(film))

    bot.send_message(message.chat.id, "Choose a film:", reply_markup=markup_films)


@bot.message_handler(func=lambda message: filter_showing_films(message, showing_films_list))
def showing_films_ov_filter(message):
    """Inline keyboard for filtering showing films based on OV availability."""

    film_id = db_info_finder.get_film_id_by_title(message.text)

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='✅ Yes', callback_data=f'{film_id},fid|1,ov'))
    keyboard.add(types.InlineKeyboardButton(text='⛔ No', callback_data=f'{film_id},fid|0,ov'))
    keyboard.add(types.InlineKeyboardButton(text="🤷 Doesn't matter", callback_data=f'{film_id},fid|2,ov'))
    # Fix Go back button
    keyboard.add(types.InlineKeyboardButton(text="🔙 Go back!", callback_data=message.text))

    bot.send_message(message.chat.id, "Are you looking for OV Version?", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.endswith(('ov')))
def showing_films_imax_filter_callback(call):
    """Inline keyboard for filtering showing films based on IMAX availability."""

    logging.info(f"Call Data: {call.data}")

    query_dict = CallParser.parse(call.data)
    film_id = query_dict.pop('film_id')

    if db_info_finder.check_performance_version_availability(film_id, query_dict):

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='✅ Yes', callback_data=f'{call.data}|1,imax'))
        keyboard.add(types.InlineKeyboardButton(text='⛔ No', callback_data=f'{call.data}|0,imax'))
        keyboard.add(types.InlineKeyboardButton(text="🤷 Doesn't matter", callback_data=f'{call.data}|2,imax'))
        keyboard.add(types.InlineKeyboardButton(text="🔙 Go back!", callback_data=call.data))

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Are you looking for IMAX Version?", reply_markup=keyboard)

    else:
        bot.send_message(call.message.chat.id, "Didn't find what you are looking for. Please try again.")

@bot.callback_query_handler(func=lambda call: call.data.endswith(('imax')))
def showing_films_3d_filter_callback(call):

    logging.info(f"Call Data: {call.data}")
    query_dict = CallParser.parse(call.data)
    film_id = query_dict.pop('film_id')

    if db_info_finder.check_performance_version_availability(film_id, query_dict):

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='✅ Yes', callback_data=f'{call.data}|1,3d'))
        keyboard.add(types.InlineKeyboardButton(text='⛔ No', callback_data=f'{call.data}|0,3d'))
        keyboard.add(types.InlineKeyboardButton(text="🤷 Doesn't matter", callback_data=f'{call.data}|2,3d'))
        keyboard.add(types.InlineKeyboardButton(text="🔙 Go back!", callback_data=call.data))

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Are you looking for 3D Version?", reply_markup=keyboard)

    else:
        bot.send_message(call.message.chat.id, "Didn't find what you are looking for. Please try again.")

@bot.callback_query_handler(func=lambda call: call.data.endswith(('3d')))
def showing_films_date_filter_callback(call):

    logging.info(f"Call Data: {call.data}")
    query_dict = CallParser.parse(call.data)
    logging.info(f"Query Dict: {query_dict}")

    film_id = query_dict.pop('film_id')

    if db_info_finder.check_performance_version_availability(film_id, query_dict):

        date_list = db_info_finder.get_performance_dates_by_film_id(film_id, query_dict)

        keyboard = types.InlineKeyboardMarkup()
        for date in date_list:
            date_str = date.strftime('%Y-%m-%d')
            keyboard.add(types.InlineKeyboardButton(text=date_str, callback_data=f'{call.data}|{date_str}'))

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Choose a date:", reply_markup=keyboard)
    else:
        bot.send_message(call.message.chat.id, "Didn't find what you are looking for. Please try again.")

@bot.callback_query_handler(func = lambda call: bool(re.search(CallParser.DATE_PATTERN_ENDING, call.data)))
def showing_films_time_filter_callback(call):

    logging.info(f"Call Data: {call.data}")
    query_dict = CallParser.parse(call.data)
    # film_id = query_dict.pop('film_id')

    # TODO: Add filter for time
    logging.info(f"Query Dict: {query_dict}")

@bot.callback_query_handler(func = lambda call: bool(re.search(CallParser.TIME_PATTERN_ENDING, call.data)))
def showing_films_links(call):

    logging.info(f"Call Data: {call.data}")
    query_dict = CallParser.parse(call.data)
    # film_id = query_dict.pop('film_id')

    # TODO: Add filter
    logging.info(f"Query Dict: {query_dict}")


# %%

if __name__ == "__main__":
    logger = Logger(file_handler=True)
    logger.get_logger()

    SQL_CONNECTION_URI = get_or_raise("POSTGRES_CONNECTION_URI")

    db_info_finder = FilmInfoFinder(SQL_CONNECTION_URI)

    logging.info("----- Bot starts to run! -----")

    bot.infinity_polling()
