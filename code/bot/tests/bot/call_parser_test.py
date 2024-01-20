#%%

from bot.utils.call_parser import CallParser

#%%

def test_call_parser_simple():
    # Case 1: Simple example
    # prepare
    expected_result = {
        "film_id": "A6D63000012BHGWDVI",
        "is_ov": True,
        "is_imax": True,
        "is_3d": False,
        "date": "2023-12-10",
        "time": "10:25"}

    # execute
    input_string = "A6D63000012BHGWDVI,fid|1,ov|1,imax|0,3d|2023-12-10|10:25"
    result = CallParser.parse(input_string)

    # verify
    assert result == expected_result

def test_call_parser_two_flag():
    # Case 2: With 0s
    # prepare
    expected_result = {
        "film_id": "A6D63000012BHGWDVI",
        "is_ov": True,
        'is_3d': False,
        "date": "2023-12-10",
        "time": "10:25"}

    # execute
    input_string = "A6D63000012BHGWDVI,fid|1,ov|2,imax|0,3d|2023-12-10|10:25"
    result = CallParser.parse(input_string)

    print(result)
    # verify
    assert result == expected_result
