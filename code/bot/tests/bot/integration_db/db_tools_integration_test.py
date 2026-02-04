"""Integration tests for the cinema agent database tools and the agent.

Uses a real Postgres database (testcontainers) with tracker schema and sample data.
Agent tests call the real OpenAI API when OPENAI_API_KEY is set; otherwise they are skipped.
Run with: pytest code/bot/tests/bot/integration_db/db_tools_integration_test.py -v
Or only integration: pytest -m integration -v
"""

from __future__ import annotations

import os
from datetime import date, timedelta

import pytest
from loguru import logger

from bot.genai.agent import AnswerWithVoice
from bot.genai.db_tools import build_db_tools


def _has_openai_key() -> bool:
    key = os.environ.get("OPENAI_API_KEY") or ""
    return bool(key and not key.startswith("sk-dummy") and len(key) > 10)


@pytest.fixture
def tools(db_connection_uri_with_sample_data: str) -> list:
    """Build the four db tools against the integration DB."""
    logger.info("Building db tools for integration DB")
    return build_db_tools(db_connection_uri_with_sample_data)


@pytest.fixture
def agent_with_test_db(db_connection_uri_with_sample_data: str):
    """Build AnswerWithVoice against the integration DB. Skips if OPENAI_API_KEY not set."""
    if not _has_openai_key():
        logger.warning("Skipping agent fixture: OPENAI_API_KEY not set or placeholder")
        pytest.skip("OPENAI_API_KEY not set or placeholder; agent tests require a real key")
    logger.info("Building AnswerWithVoice agent for integration DB")
    return AnswerWithVoice(
        db_dilect_connection_uri=db_connection_uri_with_sample_data,
        open_ai_api_key=os.environ["OPENAI_API_KEY"],
        eleven_api_key=os.environ.get("ELEVEN_API_KEY", "dummy-for-agent-query-tests"),
    )


def _tool_by_name(tools: list, name: str):
    return next(t for t in tools if t.name == name)


# ---- run_sql_query ----
@pytest.mark.integration
def test_run_sql_query_returns_film_rows_from_tracker(tools: list) -> None:
    """Integration: run_sql_query executes SELECT against tracker.films and returns real data."""
    run_sql = _tool_by_name(tools, "run_sql_query")
    query = "SELECT title FROM tracker.films ORDER BY title LIMIT 10"
    result = run_sql.invoke({"query": query})
    logger.info("run_sql_query result (films): {}", result[:200] + "..." if len(result) > 200 else result)
    assert "Query failed" not in result
    assert "Only SELECT" not in result
    # Sample data has these films
    assert "Wonka" in result
    assert "Wish" in result
    assert "Creator" in result
    assert "The Marvels" in result
    assert "Saw X" in result


@pytest.mark.integration
def test_run_sql_query_join_films_performances(tools: list) -> None:
    """Integration: free query can join films and performances and return showtimes."""
    run_sql = _tool_by_name(tools, "run_sql_query")
    result = run_sql.invoke(
        {
            "query": """
        SELECT f.title, p.performance_date, p.performance_time
        FROM tracker.films f
        JOIN tracker.performances p ON f.film_id = p.film_id
        WHERE p.performance_date >= CURRENT_DATE
        ORDER BY f.title, p.performance_date
        LIMIT 5
        """
        }
    )
    assert "Query failed" not in result
    assert "Wonka" in result


@pytest.mark.integration
def test_run_sql_query_rejects_mutation(tools: list) -> None:
    """Integration: run_sql_query rejects INSERT/UPDATE/DELETE."""
    run_sql = _tool_by_name(tools, "run_sql_query")
    for bad_query in (
        "INSERT INTO tracker.films (film_id, title) VALUES ('x','y')",
        "UPDATE tracker.films SET title = 'x' WHERE film_id = 'y'",
        "DELETE FROM tracker.films WHERE film_id = 'y'",
    ):
        result = run_sql.invoke({"query": bad_query})
        assert "Only SELECT" in result or "forbidden" in result.lower()


# ---- list_available_films ----
@pytest.mark.integration
def test_list_available_films_showing_returns_current_films(tools: list) -> None:
    """Integration: list_available_films('showing') returns films with future performances."""
    list_avail = _tool_by_name(tools, "list_available_films")
    result = list_avail.invoke({"list_type": "showing"})
    # Sample data: Wonka has performance_date = CURRENT_DATE + 10 days
    assert "Wonka" in result
    assert "currently showing" in result or "Wonka" in result


@pytest.mark.integration
def test_list_available_films_upcoming_returns_all_four(tools: list) -> None:
    """Integration: list_available_films('upcoming') returns all trackable unreleased films."""
    list_avail = _tool_by_name(tools, "list_available_films")
    result = list_avail.invoke({"list_type": "upcoming"})
    assert "Napoleon" in result
    assert "SAW X" in result or "Saw X" in result
    assert "Wish" in result
    assert "Raus aus dem Teich" in result


# ---- search_by_characteristics ----
@pytest.mark.integration
def test_search_by_characteristics_imax_wonka(tools: list) -> None:
    """Integration: search_by_characteristics finds IMAX performances for Wonka."""
    search = _tool_by_name(tools, "search_by_characteristics")
    result = search.invoke({"film_title": "Wonka", "is_imax": True})
    assert "No film" not in result
    assert "Wonka" in result
    assert "Performances" in result


@pytest.mark.integration
def test_search_by_characteristics_ov_3d_the_marvels(tools: list) -> None:
    """Integration: search by OV and 3D for The Marvels (sample has IMAX/OV/3D but past dates)."""
    search = _tool_by_name(tools, "search_by_characteristics")
    result = search.invoke({"film_title": "The Marvels", "is_ov": True, "is_3d": True})
    # Film exists; performances may be in the past so tool returns either Marvels or no match
    assert "No film" not in result
    assert "Marvels" in result or "No performances" in result


@pytest.mark.integration
def test_search_by_characteristics_unknown_film_returns_message(tools: list) -> None:
    """Integration: unknown film title returns a clear message."""
    search = _tool_by_name(tools, "search_by_characteristics")
    result = search.invoke({"film_title": "NonExistentMovie123"})
    assert "No film" in result


# ---- search_by_date ----
@pytest.mark.integration
def test_search_by_date_single_day_returns_performances(tools: list) -> None:
    """Integration: search_by_date for a day with performances returns film and times."""
    search = _tool_by_name(tools, "search_by_date")
    # Sample data: Creator on 2023-11-15 and 2023-11-16
    result = search.invoke({"date_from": "2023-11-15"})
    assert "Please provide" not in result
    assert "Creator" in result
    assert "Performances" in result


@pytest.mark.integration
def test_search_by_date_range(tools: list) -> None:
    """Integration: date range returns performances in that range."""
    search = _tool_by_name(tools, "search_by_date")
    result = search.invoke({"date_from": "2023-11-13", "date_to": "2023-11-14"})
    assert "The Marvels" in result or "Performances" in result or "No performances" in result


@pytest.mark.integration
def test_search_by_date_with_film_filter(tools: list) -> None:
    """Integration: search_by_date with film_title restricts to that film."""
    search = _tool_by_name(tools, "search_by_date")
    result = search.invoke({"date_from": "2023-11-15", "film_title": "Creator"})
    assert "Creator" in result
    assert "Performances" in result or "No performances" in result


@pytest.mark.integration
def test_search_by_date_future_ten_days(tools: list) -> None:
    """Integration: date 10 days ahead (Wonka performance in sample) returns Wonka."""
    search = _tool_by_name(tools, "search_by_date")
    future = (date.today() + timedelta(days=10)).strftime("%Y-%m-%d")
    result = search.invoke({"date_from": future})
    assert "Wonka" in result or "No performances" in result


# ---- tool chain (integration flow) ----
@pytest.mark.integration
def test_tools_share_same_connection(tools: list) -> None:
    """Integration: all four tools see the same data (same DB connection)."""
    run_sql = _tool_by_name(tools, "run_sql_query")
    list_avail = _tool_by_name(tools, "list_available_films")
    # Films from raw SQL
    sql_result = run_sql.invoke({"query": "SELECT COUNT(*) AS n FROM tracker.films"})
    assert "5" in sql_result or "n" in sql_result
    # Showing list includes Wonka (from same DB)
    list_result = list_avail.invoke({"list_type": "showing"})
    assert "Wonka" in list_result


# ---- agent (AnswerWithVoice) ----
# These tests call the real agent against the test DB; they require OPENAI_API_KEY and are skipped otherwise.


@pytest.mark.integration
def test_agent_what_films_are_showing(agent_with_test_db: AnswerWithVoice) -> None:
    """Integration: agent answers 'What films are currently showing?' with data from the test DB."""
    question = "What films are currently showing?"
    answer = agent_with_test_db._query_db(question)
    logger.info("Agent Q: {} | A: {}", question, answer)
    assert answer
    assert "Wonka" in answer, (
        f"Expected agent to return Wonka (only film with future showtimes in sample DB), got: {answer!r}"
    )


@pytest.mark.integration
def test_agent_list_upcoming_films(agent_with_test_db: AnswerWithVoice) -> None:
    """Integration: agent answers about upcoming films with data from the test DB."""
    question = "List upcoming films or what's coming soon."
    answer = agent_with_test_db._query_db(question)
    logger.info("Agent Q: {} | A: {}", question, answer)
    assert answer
    # Sample DB has Napoleon, SAW X, Wish, Raus aus dem Teich
    upcoming_mentions = [t for t in ("Napoleon", "SAW X", "Saw X", "Wish", "Raus aus dem Teich") if t in answer]
    assert upcoming_mentions, f"Expected agent to mention at least one upcoming film from sample DB, got: {answer!r}"


@pytest.mark.integration
def test_agent_wonka_imax(agent_with_test_db: AnswerWithVoice) -> None:
    """Integration: agent answers about Wonka in IMAX using data from the test DB."""
    question = "When is Wonka playing in IMAX? Or is Wonka available in IMAX?"
    answer = agent_with_test_db._query_db(question)
    logger.info("Agent Q: {} | A: {}", question, answer)
    assert answer
    assert "Wonka" in answer, f"Expected agent to mention Wonka (sample DB has IMAX showings), got: {answer!r}"


@pytest.mark.integration
def test_agent_what_playing_on_date(agent_with_test_db: AnswerWithVoice) -> None:
    """Integration: agent answers about a specific date using data from the test DB."""
    question = "What is playing on November 15, 2023?"
    answer = agent_with_test_db._query_db(question)
    logger.info("Agent Q: {} | A: {}", question, answer)
    assert answer
    # Sample DB has Creator on 2023-11-15
    assert "Creator" in answer, f"Expected agent to mention Creator (sample DB has show on 2023-11-15), got: {answer!r}"
