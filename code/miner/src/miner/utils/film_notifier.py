# %%

import re
import logging
import asyncio

from telebot.async_telebot import AsyncTeleBot

from common.db.db_model import UsersFilmInfo

# %%

class FilmReleaseNotification:
    """ This class sends a notification about a release of a film to all the users in the list """

    def __init__(self, BOT_TOKEN: str):
        self.bot = AsyncTeleBot(BOT_TOKEN)

    async def send_notification(self, users_list: list[UsersFilmInfo]):
        """Sends a notification about a release of a film to all the users in the list """

        tasks = [ asyncio.create_task(self.bot.send_message(chat_id=user.chat_id, text=self._message(user)))
                for user in users_list]

        return await asyncio.gather(*tasks)

    async def shutdown(self):
        try:
            logging.info("Bot session is closing.")
            await self.bot.close_session()
            logging.info("Bot session is closed.")
        except Exception as error:
            logging.error(f"An error occurred while closing the bot session: {error}", exc_info=True)

    # TODO: Improve this
    @staticmethod
    def _message(user: UsersFilmInfo) -> str:
        """ Message to be sent to the user. """
        return  f"""✅🎥 {user.title} became availabe! 🎥✅\n
                \n
                \n
                🎟️🎟️🎟️link to buy tickets: {user.url}🎟️🎟️🎟️\n
                """

    @staticmethod
    def _format_name_for_url(input_string: str) -> str:
        """Format name for url."""

        # Convert to lowercase
        formatted_string = input_string.lower()

        # Replace specific characters with their desired representations
        # This can be adjusted or extended based on further rules or exceptions
        formatted_string = formatted_string.replace('&', '%26')

        # Replace sequences of characters not in the allowed set with a single hyphen
        # Allowed characters are letters, numbers, hyphens, percent signs, exclamation marks, and parentheses
        formatted_string = re.sub(r"[^a-z0-9-%!()´.üäöß]+", '-', formatted_string)

        # Remove potential leading or trailing hyphens
        formatted_string = formatted_string.strip('-')

        return formatted_string
