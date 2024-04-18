#%%
import os
import pytest

from datetime import datetime, timedelta

#%%

@pytest.fixture
def schemas():
    return ["tracker"]

@pytest.fixture
def init_scripts():
    return [os.path.abspath("./code/init-db/init-db.sql"),
            os.path.abspath("./code/init-db/sample-data.sql")]

@pytest.fixture
def date_ten_days_in_future_date():
    """ It returns a date 10 days in the future """
    return datetime.now().date() + timedelta(days=10)
