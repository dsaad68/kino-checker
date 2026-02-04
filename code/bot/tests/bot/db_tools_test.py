"""Tests for the cinema agent database tools."""

from __future__ import annotations

from datetime import timedelta

from bot.genai.db_tools import build_db_tools


def test_build_db_tools_returns_four_tools(db_connection_uri_with_sample_data: str) -> None:
    tools = build_db_tools(db_connection_uri_with_sample_data)
    assert len(tools) == 4
    names = {t.name for t in tools}
    assert "run_sql_query" in names
    assert "list_available_films" in names
    assert "search_by_characteristics" in names
    assert "search_by_date" in names


def test_run_sql_query_select_allowed(db_connection_uri_with_sample_data: str) -> None:
    tools = build_db_tools(db_connection_uri_with_sample_data)
    run_sql = next(t for t in tools if t.name == "run_sql_query")
    result = run_sql.invoke({"query": "SELECT title FROM tracker.films LIMIT 2"})
    assert "Only SELECT" not in result
    assert "Query failed" not in result or "tracker" in result


def test_run_sql_query_insert_rejected(db_connection_uri_with_sample_data: str) -> None:
    tools = build_db_tools(db_connection_uri_with_sample_data)
    run_sql = next(t for t in tools if t.name == "run_sql_query")
    result = run_sql.invoke({"query": "INSERT INTO tracker.films (film_id, title) VALUES ('x','y')"})
    assert "Only SELECT" in result or "forbidden" in result.lower()


def test_list_available_films_showing(db_connection_uri_with_sample_data: str) -> None:
    tools = build_db_tools(db_connection_uri_with_sample_data)
    list_avail = next(t for t in tools if t.name == "list_available_films")
    result = list_avail.invoke({"list_type": "showing"})
    assert "Wonka" in result or "currently showing" in result or "No films" in result


def test_list_available_films_upcoming(db_connection_uri_with_sample_data: str) -> None:
    tools = build_db_tools(db_connection_uri_with_sample_data)
    list_avail = next(t for t in tools if t.name == "list_available_films")
    result = list_avail.invoke({"list_type": "upcoming"})
    assert "Napoleon" in result or "Wish" in result or "Upcoming" in result or "No upcoming" in result


def test_list_available_films_invalid_type(db_connection_uri_with_sample_data: str) -> None:
    tools = build_db_tools(db_connection_uri_with_sample_data)
    list_avail = next(t for t in tools if t.name == "list_available_films")
    result = list_avail.invoke({"list_type": "invalid"})
    assert "showing" in result and "upcoming" in result


def test_search_by_characteristics(db_connection_uri_with_sample_data: str) -> None:
    tools = build_db_tools(db_connection_uri_with_sample_data)
    search = next(t for t in tools if t.name == "search_by_characteristics")
    result = search.invoke({"film_title": "Wonka", "is_imax": True})
    assert "No film" not in result or "Wonka" in result
    assert "Performances" in result or "No performances" in result


def test_search_by_characteristics_unknown_film(db_connection_uri_with_sample_data: str) -> None:
    tools = build_db_tools(db_connection_uri_with_sample_data)
    search = next(t for t in tools if t.name == "search_by_characteristics")
    result = search.invoke({"film_title": "Nonexistent Film XYZ"})
    assert "No film" in result


def test_search_by_date(db_connection_uri_with_sample_data: str) -> None:
    tools = build_db_tools(db_connection_uri_with_sample_data)
    search = next(t for t in tools if t.name == "search_by_date")
    from datetime import date

    future = (date.today() + timedelta(days=10)).strftime("%Y-%m-%d")
    result = search.invoke({"date_from": future})
    assert "Please provide" not in result
    assert "YYYY-MM-DD" not in result or "Performances" in result


def test_search_by_date_missing(db_connection_uri_with_sample_data: str) -> None:
    tools = build_db_tools(db_connection_uri_with_sample_data)
    search = next(t for t in tools if t.name == "search_by_date")
    result = search.invoke({"date_from": None})
    assert "date_from" in result or "YYYY-MM-DD" in result
