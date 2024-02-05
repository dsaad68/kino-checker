#%%
from miner.utils.film_notifier import FilmReleaseNotification

def test_format_name_for_url():

    # Create an instance of the FilmReleaseNotification class
    film_notifier = FilmReleaseNotification("YOUR_BOT_TOKEN_HERE")

    # Test case 1
    input_string = "Asterix & Obelix im Reich de"
    expected_output = "asterix-%26-obelix-im-reich-de"
    assert film_notifier._format_name_for_url(input_string) == expected_output

    # Test case 2
    input_string = "Tribute v. Panem: Ballad of So"
    expected_output = "tribute-v.-panem-ballad-of-so"
    assert film_notifier._format_name_for_url(input_string) == expected_output

    # Test case 3
    input_string = "ROH: Manon"
    expected_output = "roh-manon"
    assert film_notifier._format_name_for_url(input_string) == expected_output

    # Test case 4
    input_string = "Nedelja (serb. OmU dt. UT)"
    expected_output = "nedelja-(serb.-omu-dt.-ut)"
    assert film_notifier._format_name_for_url(input_string) == expected_output

    # Test case 5
    input_string = "Das fünfte Element (Best of Ci"
    expected_output = "das-fünfte-element-(best-of-ci"
    assert film_notifier._format_name_for_url(input_string) == expected_output

    # Test case 6
    input_string = "Peppa´s Kino Party"
    expected_output = "peppa´s-kino-party"
    assert film_notifier._format_name_for_url(input_string) == expected_output

    # Test case 7
    input_string = "Aquaman: Lost Kingdom"
    expected_output = "aquaman-lost-kingdom"
    assert film_notifier._format_name_for_url(input_string) == expected_output

    # Test case 8
    input_string = "Wow! Nachricht aus dem All"
    expected_output = "wow!-nachricht-aus-dem-all"
    assert film_notifier._format_name_for_url(input_string) == expected_output
