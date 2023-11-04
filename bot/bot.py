#%%

import os
import telebot
import logging

from bot_helpers.info_finder import DBInfoFinder
from bot_helpers.answers import answer

from my_logger import Logger

#%%

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

#%%

def restart(message):

    new_message = "Do you want to restart or do you want to go back to the films list?"

    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add( telebot.types.KeyboardButton('/restart') )
    markup.add( telebot.types.KeyboardButton('/ZKM_Films_List') )

    bot.send_message(message.chat.id, new_message, reply_markup = markup)

#%%

@bot.message_handler(commands=['start','restart'])
def send_welcome(message):

    markup_start= telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup_start.add( telebot.types.KeyboardButton('/ZKM_Films_List') )

    bot.reply_to(message, f"Howdy {message.from_user.first_name}, please choose from the list?", reply_markup=markup_start)


@bot.message_handler(commands=['ZKM_Films_List'])
def echo_all(message):

    films_list = db_info_finder.get_films_list_db()

    global films_list_state
    films_list_state = films_list.copy()

    markup_films = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for film in films_list:
        markup_films.add( telebot.types.KeyboardButton(film) )

    bot.send_message(message.chat.id, "Choose a film:", reply_markup=markup_films)

@bot.message_handler(func=lambda message: message if message.text in films_list_state else False)
def handle_not_url_message(message):

    film_info = db_info_finder.get_film_info_db(title = message.text)

    if film_info.get("availability", False):
        new_message = answer(film_info)
        bot.reply_to(message, new_message)
    else:
        new_message = answer(film_info)
        bot.reply_to(message, new_message)
        db_info_finder.update_users_db(message_id = message.message_id , chat_id = message.chat.id, title = message.text)
        bot.send_message(chat_id = message.chat.id, text = "You will be informed when the tickets become available.")

    restart(message)

    global films_list_state
    del films_list_state

#%%

if __name__ == "__main__":

    logger = Logger(file_handler=True)
    logger.get_logger()

    SQL_CONNECTION_URI = os.environ.get('POSTGRES_CONNECTION_URI')

    db_info_finder = DBInfoFinder(SQL_CONNECTION_URI)

    logging.info("----- Bot starts to run! -----")

    bot.infinity_polling()
