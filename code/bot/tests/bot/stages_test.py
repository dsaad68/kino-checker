from bot.utils.states import State

def test_states():
    assert State.BUY.go_back() == State.TIME
    assert State.TIME.go_back() == State.DATE
    assert State.DATE.go_back() == State._3d
    assert State._3d.go_back() == State.IMAX
    assert State.IMAX.go_back() == State.OV
    assert State.OV.go_back() == State.FILM
    assert State.FILM.go_back() == State.START
    assert State.BOOK.go_back() == State.OUTCOMING
    assert State.OUTCOMING.go_back() == State.START
    assert State.START.go_back() == State.START
