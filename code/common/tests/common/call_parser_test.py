#%%

from common.call_parser import CallParser

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

    # verify
    assert result == expected_result

def test_call_parser_without_film_id():
    # Case 2: Without film_id
    # prepare
    expected_result = {
        "is_ov": True,
        'is_3d': False}

    # execute
    input_string = "1,ov|2,imax|0,3d"
    result = CallParser.parse(input_string)

    # verify
    assert result == expected_result


def test_call_parser_upcoming_film_id():
    # Case 2: With upcoming film_id
    # prepare
    expected_result = {
        "uf": 1212,
        "is_ov": True,
        'is_3d': False}

    # execute
    input_string = "1212,uf|1,ov|2,imax|0,3d"
    result = CallParser.parse(input_string)

    # verify
    assert result == expected_result

def test_call_parser_for_input():
    # Case 2: With 0s
    # prepare
    expected_result_1 = {'uf': 1212 , "flags": "1,ov|2,imax|1,3d"}
    expected_result_2 = {'uf': 4343 , "flags": "1,ov|2,imax|0,3d"}

    # execute & verify
    assert expected_result_1 == CallParser.parse_for_input("1212,uf|1,ov|2,imax|1,3d")
    assert expected_result_2 == CallParser.parse_for_input("4343,uf|1,ov|2,imax|0,3d")
