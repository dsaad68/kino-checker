# %%
from __future__ import annotations

from pathlib import Path

import telebot
from bot.context import BotContext
from bot.genai.agent import AnswerWithVoice
from bot.utils.filters import filter_upcoming_films  # , filter_showing_films
from common.call_parser import CallParser
from common.helpers import get_or_raise, reverse_dict_search
from common.logging_config import setup_logger
from loguru import logger
from telebot import custom_filters, types
from telebot.handler_backends import State, StatesGroup  # States


class MyStates(StatesGroup):
    # Just name variables differently
    answer = State()


def setup_handlers(ctx: BotContext) -> None:
    """Setup all bot message and callback handlers with context."""
    bot = ctx.bot

    # INFO: Works fine
    @bot.message_handler(commands=["start", "restart"])
    def send_welcome(message: types.Message) -> None:
        """Sends a welcome message and show level 1 menu."""
        markup_start = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup_start.add(telebot.types.KeyboardButton("/Upcoming_Films"))
        markup_start.add(telebot.types.KeyboardButton("/Ask"))
        # markup_start.add(telebot.types.KeyboardButton("/Showing_Films"))

        bot.reply_to(
            message, f"Howdy {message.from_user.first_name}, please choose from the list?", reply_markup=markup_start
        )

    @bot.message_handler(commands=["Ask"])
    def response_to_ask_command(message: types.Message) -> None:
        """Sends a response to the ask command."""
        # Rate limiting for voice/query commands
        if ctx.voice_limiter.is_rate_limited(message.from_user.id):
            seconds = ctx.voice_limiter.get_time_until_reset(message.from_user.id)
            bot.reply_to(
                message, f"Too many voice requests. Please wait {seconds} seconds before asking another question."
            )
            return

        bot.set_state(message.from_user.id, MyStates.answer, message.chat.id)
        bot.reply_to(message, f"Howdy {message.from_user.first_name}, ask me your question?")

    @bot.message_handler(state=MyStates.answer)
    def process_question(message: types.Message) -> None:
        agent = AnswerWithVoice(
            db_dilect_connection_uri=ctx.db_dialect_connection_uri,
            open_ai_api_key=ctx.openai_api_key,
            eleven_api_key=ctx.eleven_api_key,
        )
        agent.answer(bot, message)
        bot.delete_state(message.from_user.id, message.chat.id)

    @bot.callback_query_handler(func=lambda call: call.data == "restart")
    def restart(call: types.CallbackQuery) -> None:
        """Sends a welcome message and show level 1 menu."""
        markup_start = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup_start.add(telebot.types.KeyboardButton("/Upcoming_Films"))
        # markup_start.add(telebot.types.KeyboardButton("/Showing_Films"))

        bot.send_message(call.message.chat.id, "Please choose from the list?", reply_markup=markup_start)

    @bot.message_handler(commands=["Upcoming_Films"])
    def upcoming_films(message: types.Message) -> None:
        """Shows the list of upcoming films."""
        # Rate limiting for command requests
        if ctx.command_limiter.is_rate_limited(message.from_user.id):
            seconds = ctx.command_limiter.get_time_until_reset(message.from_user.id)
            bot.reply_to(message, f"Too many requests. Please wait {seconds} seconds before trying again.")
            return

        films_list = ctx.db_info_finder.get_upcomings_films_list()
        films_dict = {film["upcoming_film_id"]: film["title"].lower() for film in films_list}

        ctx.set_upcoming_films(films_dict)

        markup_films = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for film in ctx.get_upcoming_films_list():
            markup_films.add(telebot.types.KeyboardButton(film))

        bot.send_message(message.chat.id, "Choose a film:", reply_markup=markup_films)

    # IDEA: Use STATES For steps instead of callback_data
    @bot.message_handler(func=lambda message: filter_upcoming_films(message, ctx.get_upcoming_films_list()))
    def upcoming_films_ov_filter(message: types.Message) -> None:
        """Inline keyboard for filtering upcoming films based on OV availability."""
        logger.info(f"Message: {message.text}")

        film_id = reverse_dict_search(ctx.get_upcoming_films_dict(), message.text)

        logger.info(f"film_id: {film_id}")

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="✅ Yes", callback_data=f"{film_id},uf|1,ov"))
        keyboard.add(types.InlineKeyboardButton(text="⛔ No", callback_data=f"{film_id},uf|0,ov"))
        keyboard.add(types.InlineKeyboardButton(text="🤷 Doesn't matter", callback_data=f"{film_id},uf|2,ov"))
        # IDEA: Go back button instead of restart
        keyboard.add(types.InlineKeyboardButton(text="🔙 Restart!", callback_data="restart"))

        bot.send_message(message.chat.id, "Are you looking for OV Version?", reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: call.data.endswith("ov"))
    def upcoming_films_imax_filter_callback(call: types.CallbackQuery) -> None:
        """Inline keyboard for filtering upcoming films based on IMAX availability."""
        logger.info(f"Call Data: {call.data}")

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="✅ Yes", callback_data=f"{call.data}|1,imax"))
        keyboard.add(types.InlineKeyboardButton(text="⛔ No", callback_data=f"{call.data}|0,imax"))
        keyboard.add(types.InlineKeyboardButton(text="🤷 Doesn't matter", callback_data=f"{call.data}|2,imax"))
        keyboard.add(types.InlineKeyboardButton(text="🔙 Restart!", callback_data="restart"))

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Are you looking for IMAX Version?",
            reply_markup=keyboard,
        )

    @bot.callback_query_handler(func=lambda call: call.data.endswith("imax"))
    def upcoming_films_3d_filter_callback(call: types.CallbackQuery) -> None:
        """Inline keyboard for filtering upcoming films based on 3D availability."""
        logger.info(f"Call Data: {call.data}")

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="✅ Yes", callback_data=f"{call.data}|1,3d"))
        keyboard.add(types.InlineKeyboardButton(text="⛔ No", callback_data=f"{call.data}|0,3d"))
        keyboard.add(types.InlineKeyboardButton(text="🤷 Doesn't matter", callback_data=f"{call.data}|2,3d"))
        keyboard.add(types.InlineKeyboardButton(text="🔙 Restart!", callback_data="restart"))

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Are you looking for 3D Version?",
            reply_markup=keyboard,
        )

    @bot.callback_query_handler(func=lambda call: call.data.endswith("3d"))
    def track_upcommings_films(call: types.CallbackQuery) -> None:
        """Tracks the availability of upcoming films."""
        logger.info(f"Call Data: {call.data}")

        input_dict = CallParser.parse_for_input(call.data)

        film_title = ctx.get_upcoming_films_dict().get(input_dict.get("uf"))

        ctx.db_info_finder.upsert_users(
            message_id=str(call.message.message_id),
            chat_id=str(call.message.chat.id),
            title=film_title,
            flags=input_dict.get("flags"),
        )
        bot.send_message(
            chat_id=call.message.chat.id, text="You will be informed when the tickets become available to buy."
        )

        ctx.clear_upcoming_films()

    # Register custom filters
    bot.add_custom_filter(custom_filters.StateFilter(bot))


def main() -> None:
    """Main entry point for the bot."""
    setup_logger(
        service_name="bot",
        log_level="INFO",
        log_file=Path("logs/bot.log"),
    )

    # Create bot context with all dependencies
    ctx = BotContext.create(
        token=get_or_raise("TELEGRAM_BOT_TOKEN"),
        sql_connection_uri=get_or_raise("POSTGRES_DB_CONNECTION_URI"),
        db_dialect_connection_uri=get_or_raise("POSTGRES_DB_CONNECTION_URI"),
        openai_api_key=get_or_raise("OPENAI_API_KEY"),
        eleven_api_key=get_or_raise("ELEVEN_API_KEY"),
    )

    # Setup all handlers with context
    setup_handlers(ctx)

    logger.info("----- Bot starts to run! -----")
    ctx.bot.infinity_polling()


if __name__ == "__main__":
    main()
