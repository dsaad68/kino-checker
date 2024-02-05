from common.helpers import reverse_dict_search

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
