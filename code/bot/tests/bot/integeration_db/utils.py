#%%
from datetime import datetime, date, time

#%%

def str_2_datetime(datetime_string: str) -> datetime:
    """string to datetime"""
    return datetime.strptime(datetime_string, "%Y-%m-%d %H:%M:%S")

def str_2_date(date_string:str) -> date:
    """string to date"""
    return datetime.strptime(date_string, "%Y-%m-%d").date()

def str_2_time(time_string:str) -> time:
    """string to time"""
    return datetime.strptime(time_string, "%H:%M:%S").time()
