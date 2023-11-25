# %%

import os
import telebot
import logging

from telebot import types

from my_logger import Logger

# from utils.answers import answer
from utils.db_info_finder import FilmInfoFinder
# %%

def filter_upcoming_films(message: types.Message, upcoming_films_list: list[str]) -> types.Message | None:
    if upcoming_films_list is None:
        return None
    if message.text in upcoming_films_list:
        return message

def filter_showing_films(message: types.Message, showing_films_list: list[str]) -> types.Message | None:
    if showing_films_list is None:
        return None
    if message.text in showing_films_list:
        return message

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

    film_id = db_info_finder.get_film_id_by_title(message.text)

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Yes', callback_data=f'{film_id}|is_ov'))
    keyboard.add(types.InlineKeyboardButton(text='No', callback_data=f'{film_id}|is_ov'))
    keyboard.add(types.InlineKeyboardButton(text='Doesn\'t matter', callback_data=f'{film_id}|is_ov'))

    bot.send_message(message.chat.id, "Are you looking for OV Version?:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.endswith(('is_ov')))
def showing_films_imax_filter_callback(call):

    logging.info(f"Call Data: {call.data}")
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Yes', callback_data=f'{call.message.text}|is_imax'))
    keyboard.add(types.InlineKeyboardButton(text='No', callback_data=f'{call.message.text}|is_imax'))
    keyboard.add(types.InlineKeyboardButton(text='Doesn\'t matter', callback_data=f'{call.message.text}|is_imax'))

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Are you looking for IMAX Version?", reply_markup=keyboard)


# def restart(message):
#     new_message = "Do you want to restart or do you want to go back to the films list?"

#     markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
#     markup.add(telebot.types.KeyboardButton("/restart"))
#     markup.add(telebot.types.KeyboardButton("/Upcoming_Films"))
#     markup.add(telebot.types.KeyboardButton("/Showing_Films"))
#     bot.send_message(message.chat.id, new_message, reply_markup=markup)


# %%

if __name__ == "__main__":
    logger = Logger(file_handler=True)
    logger.get_logger()

    SQL_CONNECTION_URI = get_or_raise("POSTGRES_CONNECTION_URI")

    db_info_finder = FilmInfoFinder(SQL_CONNECTION_URI)

    logging.info("----- Bot starts to run! -----")

    bot.infinity_polling()
