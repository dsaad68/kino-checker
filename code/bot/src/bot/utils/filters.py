from telebot import types

def filter_upcoming_films(message: types.Message, upcoming_films_list: list[str]) -> types.Message | None:
    """ Returns the message if the message is in the list of upcoming films list,
    returns `None` if the message is not in the list or the list is `None`.
    """
    if upcoming_films_list is None:
        return None
    if message.text in upcoming_films_list:
        return message

def filter_showing_films(message: types.Message, showing_films_list: list[str]) -> types.Message | None:
    """ Returns the message if the message is in the list of showing films list,
    returns `None` if the message is not in the list or the list is `None`.
    """
    if showing_films_list is None:
        return None
    if message.text in showing_films_list:
        return message
