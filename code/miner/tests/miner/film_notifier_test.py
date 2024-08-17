#%%
import pytest

from integeration_db.docker_container import Docker
from integeration_db.integration_db import IntegrationDb, EnvVar

from miner.utils.film_db_manager import FilmDatabaseManager
from miner.utils.film_notifier import FilmReleaseNotification

#%%

CONTAINER_NAME = "postgres:alpine3.18"

dckr = Docker()

#%%

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

@pytest.mark.skipif(not dckr.is_image_running(CONTAINER_NAME), reason=f"There is no container based on the {CONTAINER_NAME} is running.")
@pytest.mark.skipif(IntegrationDb.db_int_not_available(), reason=f"Missing environment variable {EnvVar.INT_DB_URL.name} containing the database URL")
def test_message(schemas, init_scripts):

    expected_message = ("✅🎥 Creator is now available! 🎥✅\n\n"
                        "🎟️🎟️🎟️ Link to buy tickets: 🎟️🎟️🎟️\n\n"
                        "📅 2023-11-15 ⌚ 20:00:00 🎥 IMAX 🕶️ 3D 💂🏻 OV:\n"
                        "https://cineorder.filmpalast.net/zkm/movie/imax-creator-ov-3d/58E63000012BHGWDVI/performance/88D45000023UHQLAAA\n"
                        "\n📅 2023-11-16 ⌚ 17:00:00 🎥 IMAX 💂🏻 OV:\n"
                        "https://cineorder.filmpalast.net/zkm/movie/imax-creator-ov/58E63000012BHGWDVI/performance/99D45000023UHQLAAA\n")

    with IntegrationDb(schemas, init_scripts) as CONNECTION_STRING:

        # Execute
        film_db_manager = FilmDatabaseManager(CONNECTION_STRING) # type: ignore
        user_list = film_db_manager.get_users_to_notify()

        user_dict = {item.user_id: item for item in user_list}
        user = user_dict.get(5)

        film_release_notification = FilmReleaseNotification("YOUR_BOT_TOKEN_HERE")
        test_message = film_release_notification._message(user)

        # Verify
        assert test_message == expected_message
