#%%
import os

from typing import Any, Optional

#%%

def get_or_raise(env_name: str) -> str:
    """get an environment variable or raise an error

    Parameters
    ----------
    env_name : str
        Name of the environment variable

    Returns
    -------
    str
        Value of the environment variable

    Raises
    ------
    ValueError
        If the environment variable is not set
    """
    value = os.environ.get(env_name)
    if value is not None:
        return value
    else:
        raise ValueError(f"Missing environment variable {env_name}")

#%%
def reverse_dict_search(input_dict: dict, value: Any) -> Optional[Any]:
    """Reverse dictionary search
    Search for the first key in the dictionary based on the given value.

    Parameters
    ----------
    input_dict : dict
        Dictionary with key-value pairs.
    value : Any
        Value to search for.

    Returns
    -------
    Optional[Any]
        The first key associated with the value if found, None otherwise.
    """

    return next((key for key, val in input_dict.items() if val == value), None)
