#%%

def answer(film) -> str:

    positive = "✅🎥 You Can Buy Ticket Now!🎥✅\n"
    negative = "❌ Not Available Now!❌\n"
    buy_tick = "\n🎟️🎟️🎟️ Buy Ticks here: 🎟️🎟️🎟️\n"

    return (f'{ positive if film.get("availability") else negative }'
            f'\nFilm is available: { "✅" if film.get("availability") else "❌"}\n'
            f'IMAX 3D OV: {"✅" if film.get("imax_3d_ov") else "❌"}\n'
            f'IMAX OV: {"✅" if film.get("imax_ov") else "❌"}\n'
            f'HD OV: {"✅" if film.get("hd_ov") else "❌"}\n'
            f'\nLast time check:\n'
            f'{film.get("last_checked")}\n'
            f'{buy_tick if film.get("availability") else ""}'
            f'{film.get("link") if film.get("availability") else ""}')
