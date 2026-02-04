# %%

from helper import do

from my_logger import Logger

# %%

if __name__ == "__main__":
    logger = Logger(
        username="Tester", OS="Windows", local="local", custom_dimensions={"job_id": 2020}, file_handler=True
    )
    logger.get_logger()

    do()
