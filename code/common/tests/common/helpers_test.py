from common.helpers import reverse_dict_search, deduplicate_list_dict

def test_reverse_dict_search():
    # Test 1: Value is present
    assert reverse_dict_search({'a': 1, 'b': 2, 'c': 3}, 2) == 'b'

    # Test 2: Value is not present
    assert reverse_dict_search({'a': 1, 'b': 2, 'c': 3}, 4) is None

    # Test 3: Multiple keys with same value, should return the first key found
    test_dict = {'a': 1, 'b': 1, 'c': 2}
    expected_key = next(iter([k for k, v in test_dict.items() if v == 1]))  # Get the first key with value 1
    assert reverse_dict_search(test_dict, 1) == expected_key

    # Test 4: Empty dictionary
    assert reverse_dict_search({}, 1) is None

    # Test 5: Non-string keys
    assert reverse_dict_search({1: 'a', 2: 'b', 3: 'c'}, 'b') == 2

    print("All tests passed!")

def test_deduplicate_list_dict():

    list_of_dicts = [{'title': 'Example 1', 'value': 123},
                    {'title': 'Example 2', 'value': 456},
                    {'title': 'Example 1', 'value': 789},  # Duplicate based on 'title'
                    {'title': 'Example 3', 'value': 101112}]

    expected_output = [{'title': 'Example 1', 'value': 789},
                        {'title': 'Example 2', 'value': 456},
                        {'title': 'Example 3', 'value': 101112}]

    deduplicated_list = deduplicate_list_dict(list_of_dicts, 'title')
    print(deduplicated_list)
    assert deduplicated_list == expected_output

def test_deduplicate_list_dict_no_duplicates():

    input_list = [
            {'title': 'Example 1', 'value': 123},
            {'title': 'Example 2', 'value': 456},
            {'title': 'Example 3', 'value': 101112}]

    deduplicated_list = deduplicate_list_dict(input_list, 'title')
    assert deduplicate_list_dict(deduplicated_list, 'title') == input_list


def test_deduplicate_list_dict__empty_list():

    input_list = []
    assert deduplicate_list_dict(input_list, 'title') == input_list
