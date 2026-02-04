# %%

from miner.utils.film_db_manager import FilmDatabaseManager
from miner.utils.film_notifier import FilmReleaseNotification

# %%


def test_format_name_for_url():

    # Create an instance of the FilmReleaseNotification class
    # Use a valid token format for testing (doesn't need to be real)
    film_notifier = FilmReleaseNotification("123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890")

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


def test_message(db_connection_uri_with_sample_data):
    expected_message = (
        "✅🎥 Creator is now available! 🎥✅\n\n"
        "🎟️🎟️🎟️ Link to buy tickets: 🎟️🎟️🎟️\n\n"
        "📅 2023-11-15 ⌚ 20:00:00 🎥 IMAX 🕶️ 3D 💂🏻 OV:\n"
        "https://cineorder.filmpalast.net/zkm/movie/imax-creator-ov-3d/58E63000012BHGWDVI/performance/88D45000023UHQLAAA\n"
        "\n📅 2023-11-16 ⌚ 17:00:00 🎥 IMAX 💂🏻 OV:\n"
        "https://cineorder.filmpalast.net/zkm/movie/imax-creator-ov/58E63000012BHGWDVI/performance/99D45000023UHQLAAA\n"
    )

    # Execute
    film_db_manager = FilmDatabaseManager(db_connection_uri_with_sample_data)  # type: ignore
    user_list = film_db_manager.get_users_to_notify()

    user_dict = {item.user_id: item for item in user_list}
    user = user_dict.get(5)

    film_release_notification = FilmReleaseNotification("123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890")
    test_message = film_release_notification._message(user)

    # Verify
    assert test_message == expected_message
