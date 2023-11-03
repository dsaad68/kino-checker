#%%

import asyncio

from typing import List
from telebot.async_telebot import AsyncTeleBot

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

#%%

async def send_status(users_list: List[dict], BOT_TOKEN:str):

    bot = AsyncTeleBot(BOT_TOKEN)

    tasks = [ asyncio.create_task(bot.send_message(user.get('chat_id'), message(user))) for user in users_list]

    return await asyncio.gather(*tasks)
