#%%

import logging
import asyncio

from typing import List
from telebot.async_telebot import AsyncTeleBot

from tables.tables_model import Films, Users

#%%

def message(user: dict) -> str:

    positive: str = "✅🎥 You Can Buy Ticket Now!🎥✅\n"
    negative: str = "❌ Not Available Now!❌\n"
    buy_tick: str = "\n🎟️🎟️🎟️ Buy Ticks here: 🎟️🎟️🎟️\n"

    return (f'{ positive if user.get("availability") else negative }'
            f'\nFilm is available: { "✅" if user.get("availability") else "❌"}\n'
            f'IMAX 3D OV: {"✅" if user.get("imax_3d_ov") else "❌"}\n'
            f'IMAX OV: {"✅" if user.get("imax_ov") else "❌"}\n'
            f'HD OV: {"✅" if user.get("hd_ov") else "❌"}\n'
            f'\nLast time check:\n'
            f'{user.get("last_checked")}\n'
            f'{buy_tick if user.get("availability") else ""}'
            f'{user.get("link") if user.get("availability") else ""}')

def get_films_db_status(Session_Maker) -> List[dict]:

    try:

        with Session_Maker() as session:

            subquery = session.query(Films.title).filter(Films.availability != Films.last_update , Films.availability == True)

            results = ( session.query(Users.chat_id, Users.message_id, Users.title, Films.availability, Films.imax_3d_ov, Films.imax_ov, Films.hd_ov, Films.last_checked, Films.link)
                       .join(Films, Films.title == Users.title)
                       .filter(Users.title.in_(subquery))
                       ).all()

            return [{'chat_id': row.chat_id,
                    'title':row.title,
                    'message_id':row.message_id,
                    'availability':row.availability,
                    'imax_3d_ov':row.imax_3d_ov,
                    'imax_ov':row.imax_ov,
                    'hd_ov':row.hd_ov,
                    'last_checked':row.last_checked,
                    'link':row.link}
                    for row in results]

    except Exception as error:
            logging.error(f'ERROR : {error}', exc_info=True)


#%%

async def send_status(users_list: List[dict], BOT_TOKEN:str):

    bot = AsyncTeleBot(BOT_TOKEN)

    tasks = [ asyncio.create_task(bot.send_message(user.get('chat_id'), message(user)))
             for user in users_list]

    return await asyncio.gather(*tasks)
