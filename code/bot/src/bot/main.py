# %%

import telebot
import logging

from telebot import types

from my_logger import Logger

from common.call_parser import CallParser
from common.helpers import get_or_raise, reverse_dict_search

from bot.genai.agent import AnswerWithVoice
from bot.utils.db_info_finder import FilmInfoFinder
from bot.utils.filters import filter_upcoming_films #, filter_showing_films


from telebot import custom_filters
from telebot.handler_backends import State, StatesGroup #States

# States storage
from telebot.storage import StateMemoryStorage

#%%

OPENAI_API_KEY = get_or_raise("OPENAI_API_KEY")
ELEVEN_API_KEY = get_or_raise("ELEVEN_API_KEY")
SQL_CONNECTION_URI = get_or_raise("TEST_POSTGRES_DB_CONNECTION_URI")
DB_DILECT_CONNECTION_URI = get_or_raise("TEST_POSTGRES_DB_CONNECTION_URI")
TOKEN = get_or_raise("TEST_TELEGRAM_BOT_TOKEN")

#%%

upcoming_films_dict = None
upcoming_films_list = None

state_storage = StateMemoryStorage() # you can init here another storage
bot = telebot.TeleBot(TOKEN, state_storage=state_storage)

class MyStates(StatesGroup):
    # Just name variables differently
    answer = State()

#%%

# INFO: Works fine
@bot.message_handler(commands=["start", "restart"])
def send_welcome(message):
    """Sends a welcome message and show level 1 menu."""
    markup_start = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup_start.add(telebot.types.KeyboardButton("/Upcoming_Films"))
    markup_start.add(telebot.types.KeyboardButton("/Ask"))
    # markup_start.add(telebot.types.KeyboardButton("/Showing_Films"))

    bot.reply_to(message, f"Howdy {message.from_user.first_name}, please choose from the list?", reply_markup=markup_start)

@bot.message_handler(commands=["Ask"])
def response_to_ask_command(message):
    """Sends a response to the ask command."""

    bot.set_state(message.from_user.id, MyStates.answer, message.chat.id)
    bot.reply_to(message, f"Howdy {message.from_user.first_name}, ask me your question?")

@bot.message_handler(state=MyStates.answer)
def process_question(message):
    agent = AnswerWithVoice(db_dilect_connection_uri=DB_DILECT_CONNECTION_URI, open_ai_api_key=OPENAI_API_KEY, eleven_api_key=ELEVEN_API_KEY)
    agent.answer(bot, message)
    bot.delete_state(message.from_user.id, message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data == "restart")
def restart(call):
    """Sends a welcome message and show level 1 menu."""
    markup_start = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup_start.add(telebot.types.KeyboardButton("/Upcoming_Films"))
    # markup_start.add(telebot.types.KeyboardButton("/Showing_Films"))

    bot.send_message(call.message.chat.id, "Please choose from the list?", reply_markup=markup_start)

@bot.message_handler(commands=["Upcoming_Films"])
def upcoming_films(message):
    """Shows the list of upcoming films."""

    films_list = db_info_finder.get_upcomings_films_list()
    films_dict = {film['upcoming_film_id']: film['title'].lower() for film in films_list}

    global upcoming_films_dict
    upcoming_films_dict = films_dict.copy()

    global upcoming_films_list
    upcoming_films_list = list(upcoming_films_dict.values())

    markup_films = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for film in upcoming_films_list:
        markup_films.add(telebot.types.KeyboardButton(film))

    bot.send_message(message.chat.id, "Choose a film:", reply_markup=markup_films)

# IDEA: Use STATES For steps instead of callback_data
@bot.message_handler(func=lambda message: filter_upcoming_films(message, upcoming_films_list))
def upcoming_films_ov_filter(message):
    """Inline keyboard for filtering upcoming films based on OV availability."""

    logging.info(f"Message: {message.text}")

    film_id = reverse_dict_search(upcoming_films_dict, message.text)

    logging.info(f"film_id: {film_id}")

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='✅ Yes', callback_data=f'{film_id},uf|1,ov'))
    keyboard.add(types.InlineKeyboardButton(text='⛔ No', callback_data=f'{film_id},uf|0,ov'))
    keyboard.add(types.InlineKeyboardButton(text="🤷 Doesn't matter", callback_data=f'{film_id},uf|2,ov'))
    # IDEA: Go back button instead of restart
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

    global upcoming_films_dict
    global upcoming_films_list

    logging.info(f"Call Data: {call.data}")

    input_dict = CallParser.parse_for_input(call.data)

    film_title = upcoming_films_dict.get(input_dict.get('uf'))

    db_info_finder.upsert_users(message_id=str(call.message.message_id), chat_id=str(call.message.chat.id), title=film_title, flags=input_dict.get('flags'))
    bot.send_message(chat_id=call.message.chat.id, text="You will be informed when the tickets become available to buy.")

    upcoming_films_dict = None
    upcoming_films_list = None


# %%

if __name__ == "__main__":
    logger = Logger(file_handler=True)
    logger.get_logger()

    db_info_finder = FilmInfoFinder(SQL_CONNECTION_URI)

    logging.info("----- Bot starts to run! -----")
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.infinity_polling()
