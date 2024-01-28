# %%

# import logging
import asyncio

# from telebot import types
from telebot.async_telebot import AsyncTeleBot

from miner.utils.db_model import UsersFilmInfo

# %%

# class FilmReleaseNotification:
#     """ This class sends a notification about a release of a film to all the users in the list """

#     def __init__(self, BOT_TOKEN: str):
#         self.bot = AsyncTeleBot(BOT_TOKEN)

#     async def _send_message_task(self, user):
#         """Sends a notification about a release of a film to an user."""
#         try:
#             await self.bot.send_message(user.chat_id, self._message(user))
#         except Exception as e:
#             logging.error(f"Failed to send message to {user.chat_id}: {e}")

#     # TODO: Improve this
#     async def send_notification(self, users_list: list[UsersFilmInfo]):
#         """Sends a notification about a release of a film to all the users in the list """

#         tasks = [asyncio.create_task(self._send_message_task(user)) for user in users_list]
#         return await asyncio.gather(*tasks)

#     async def run(self, users_list: list[UsersFilmInfo]):
#         """Runs the notification. """
#         try:
#             if not users_list:
#                 await self.send_notification(users_list)
#         except Exception as e:
#             logging.error(f"An error occurred: {e}")

#     async def shutdown(self):
#         try:
#             logging.info("Bot session is closing.")
#             await self.bot.close_session()
#             logging.info("Bot session is closed.")
#         finally:
#             logging.info("Bot session is already closed.")

#     # TODO: Improve this
#     @staticmethod
#     def _message(user: UsersFilmInfo) -> str:
#         """ Message to be sent to the user. """
#         return  f"✅🎥 {user.title} became availabe! 🎥✅\n"


#%%

async def send_status(users_list: list[UsersFilmInfo], BOT_TOKEN:str):

    bot = AsyncTeleBot(BOT_TOKEN)

    tasks = [ asyncio.create_task(bot.send_message(chat_id=user.chat_id, text=message(user)))
            for user in users_list]

    return await asyncio.gather(*tasks)

def message(user: UsersFilmInfo) -> str:
    """ Message to be sent to the user. """
    return  f"✅🎥 {user.title} became availabe! 🎥✅\n"
