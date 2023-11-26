#%%
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src/"))
from bot.utils.call_parser import CallParser # noqa: E402

#%%

def test_call_parser_simple():
    # Case 1: Simple example
    # prepare
    expected_result = {
        "film_id": "100100100200",
        "is_ov": True,
        "is_imax": True,
        "is_3d": False,
        "date": "2023-12-10",
        "hour": "10:25"}

    # execute
    input_string = "[100100100200]film_id|[true]is_ov|[true]is_imax|[false]is_3d|[2023-12-10]date|[10:25]hour"
    result = CallParser.parse(input_string)

    # verify
    assert result == expected_result

def test_call_parser_zero():
    # Case 2: With 0s
    # prepare
    expected_result = {
        "film_id": "100100100200",
        "is_ov": True,
        'is_3d': False,
        "date": "2023-12-10",
        "hour": "10:25"}

    # execute
    input_string = "[100100100200]film_id|[true]is_ov|[0]is_imax|[false]is_3d|[2023-12-10]date|[10:25]hour"
    result = CallParser.parse(input_string)

    # verify
    assert result == expected_result
