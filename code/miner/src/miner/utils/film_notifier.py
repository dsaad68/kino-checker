# %%

import logging
import asyncio

# from telebot import types
from telebot.async_telebot import AsyncTeleBot

from miner.utils.db_model import UsersFilmInfo

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
        finally:
            logging.info("Bot session is already closed.")

    # TODO: Improve this
    @staticmethod
    def _message(user: UsersFilmInfo) -> str:
        """ Message to be sent to the user. """
        return  f"✅🎥 {user.title} became availabe! 🎥✅\n"
