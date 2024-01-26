# %%

import asyncio

# from telebot import types
from telebot.async_telebot import AsyncTeleBot

from miner.utils.db_model import UsersFilmInfo

# %%

class FilmReleaseNotification:
    """ This class sends a notification about a release of a film to all the users in the list """

    def __init__(self, BOT_TOKEN: str):
        self.bot = AsyncTeleBot(BOT_TOKEN)

    # TODO: Improve this
    async def send_notification(self, users_list: list[UsersFilmInfo]):
        """ Sends a notification about a release of a film to all the users in the list """

        # keyboard = types.InlineKeyboardMarkup(
        #     keyboard=[
        #         [types.InlineKeyboardButton(text='Get Showtimes', callback_data='example')],
        #         [types.InlineKeyboardButton(text='Cancel', callback_data='ExAmPLe')]
        #     ]
        # )
        # tasks = [asyncio.create_task(self.bot.send_message(user.chat_id, self._message(user), reply_markup=keyboard)) for user in self.users_list]
        tasks = [asyncio.create_task(self.bot.send_message(user.chat_id, self._message(user))) for user in users_list]
        return await asyncio.gather(*tasks)

    async def run(self, users_list: list[UsersFilmInfo]):
        """ Runs the notification. """
        try:
            await self.send_notification(users_list)
        finally:
            await self.bot.close_session()

    # TODO: Improve this
    @staticmethod
    def _message(user: UsersFilmInfo) -> str:
        """ Message to be sent to the user. """
        return  f"✅🎥 {user.title} became availabe! 🎥✅\n"
