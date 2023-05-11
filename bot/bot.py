#%%

import os
import telebot
import logging
import time

from bot_helpers.info_finder import session_maker, get_films_list_db, get_film_info_db, update_users_db
from bot_helpers.answers import answer

from logger.custom_logger import Logger

#%%

TOKEN = os.environ.get('Telegram_Dev_Bot')
bot = telebot.TeleBot(TOKEN)

#%%

@bot.message_handler(commands=['start'])
def send_welcome(message):

    markup_start= telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup_start.add( telebot.types.KeyboardButton('/ZKM_Films_List') )

    bot.reply_to(message, f"Howdy {message.from_user.first_name}, please choose from the list?", reply_markup=markup_start)


@bot.message_handler(commands=['ZKM_Films_List'])
def echo_all(message):

    films_list = get_films_list_db(Session_Maker = Session_Maker)

    global films_list_state
    films_list_state = films_list.copy()

    markup_films = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for film in films_list:
        markup_films.add( telebot.types.KeyboardButton(film) )

    bot.send_message(message.chat.id, "Choose a film:", reply_markup=markup_films)

@bot.message_handler(func=lambda message: message if message.text in films_list_state else False)
def handle_not_url_message(message):

    film_info = get_film_info_db(title = message.text, Session_Maker = Session_Maker)

    if film_info.get("availability", False):
        new_message = answer(film_info)
        bot.reply_to(message, new_message)
    else:
        new_message = answer(film_info)
        bot.reply_to(message, new_message)
        update_users_db(message_id = message.message_id , chat_id = message.chat.id, title = message.text, Session_Maker = Session_Maker)
        bot.send_message(chat_id = message.chat.id, text = "You will be informed when the tickets become available.")

    global films_list_state
    del films_list_state

#%%

if __name__ == "__main__":

    logger = Logger(file_handler=True)
    logger.get_logger()

    SQL_CONNECTION_URI = os.environ.get('KINO_POSTGRES_CONNECTION_URI')
    Session_Maker = session_maker(SQL_CONNECTION_URI)

    logging.info("----- Bot starts to run! -----")

    bot.infinity_polling()