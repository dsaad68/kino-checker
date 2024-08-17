#%%
import os
import pytest

#%%
@pytest.fixture
def schemas():
    return ["tracker"]

@pytest.fixture
def init_scripts():
    return [os.path.abspath("./code/init-db/init-db.sql"),
            os.path.abspath("./code/init-db/sample-data-cleaner.sql")]
