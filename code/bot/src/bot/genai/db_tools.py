# %%
"""Database tools for the cinema agent. Build tools with build_db_tools(connection_uri)."""

from __future__ import annotations

import re
from datetime import date, datetime

from langchain_core.tools import tool

# Lazy imports inside build_db_tools to avoid circular imports and heavy deps at module load
# %%


_FORBIDDEN_SQL = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE|GRANT|REVOKE|EXECUTE)\b",
    re.IGNORECASE,
)


def _validate_readonly_sql(query: str) -> str | None:
    """Return None if query is allowed, else an error message."""
    stripped = query.strip()
    if not stripped.upper().startswith("SELECT"):
        return "Only SELECT queries are allowed."
    if _FORBIDDEN_SQL.search(query):
        return "Query contains forbidden keyword (e.g. INSERT, UPDATE, DELETE, DROP)."
    return None


def build_db_tools(connection_uri: str) -> list:
    """Build the four database tools for the agent. Pass the same connection_uri used by the bot."""
    from langchain_community.utilities.sql_database import SQLDatabase

    from bot.utils.db_info_finder import FilmInfoFinder

    sql_db = SQLDatabase.from_uri(connection_uri)
    finder = FilmInfoFinder(connection_uri)

    @tool
    def run_sql_query(query: str) -> str:
        """Execute a read-only SQL SELECT on the cinema database.
        Use this for arbitrary questions when other tools do not fit.
        Schema: tracker.films (film_id, title, name, production_year, length_in_minutes, nationwide_start, image_url),
        tracker.performances (performance_id, film_id, performance_datetime, performance_date, performance_time,
        release_type, is_imax, is_ov, is_3d, auditorium_id, auditorium_name),
        tracker.upcoming_films (upcoming_film_id, title, release_date, film_id, is_released, is_trackable).
        Join performances with films on performances.film_id = films.film_id.
        Always add LIMIT 10 (or similar) and return only result rows, not the SQL.
        """
        err = _validate_readonly_sql(query)
        if err:
            return err
        try:
            return sql_db.run(query) or "No rows returned."
        except Exception as e:
            return f"Query failed: {e!s}"

    @tool
    def list_available_films(list_type: str = "showing") -> str:
        """List what is currently available: films now showing or upcoming films.
        list_type must be 'showing' (films with performances from today onward) or 'upcoming' (films not yet released).
        """
        if list_type not in ("showing", "upcoming"):
            return "list_type must be 'showing' or 'upcoming'."
        if list_type == "showing":
            titles = finder.get_showing_films_list()
            if not titles:
                return "No films currently showing."
            return "Films currently showing: " + ", ".join(titles)
        # upcoming
        rows = finder.get_upcomings_films_list()
        if not rows:
            return "No upcoming films."
        return "Upcoming films: " + ", ".join(r.get("title", str(r)) for r in rows)

    @tool
    def search_by_characteristics(
        film_title: str | None = None,
        is_imax: bool | None = None,
        is_3d: bool | None = None,
        is_ov: bool | None = None,
    ) -> str:
        """Filter performances by format: IMAX, 3D, or OV (original language/English).
        Pass film_title to restrict to one film, and set is_imax/is_3d/is_ov to True to filter by format.
        """
        from sqlalchemy import and_, func
        from sqlalchemy.sql import select

        from common.db.db_model import Films, Performances

        conditions = [Performances.performance_date >= func.current_date()]
        if film_title:
            film_id = finder.get_film_id_by_title(film_title)
            if not film_id:
                return f"No film found with title like '{film_title}'."
            conditions.append(Performances.film_id == film_id)
        if is_imax is True:
            conditions.append(Performances.is_imax.is_(True))
        if is_3d is True:
            conditions.append(Performances.is_3d.is_(True))
        if is_ov is True:
            conditions.append(Performances.is_ov.is_(True))

        stmt = (
            select(Films.title, Performances.performance_date, Performances.performance_time)
            .join(Performances, Films.film_id == Performances.film_id)
            .where(and_(*conditions))
            .order_by(Films.title, Performances.performance_date, Performances.performance_time)
        )
        rows = finder.execute_query_mapping_all(stmt)
        if not rows:
            return "No performances match the requested characteristics."
        lines = []
        for r in rows[:15]:
            title = r.get("title", "")
            d = r.get("performance_date")
            t = r.get("performance_time")
            date_str = d.strftime("%Y-%m-%d") if isinstance(d, date) else str(d)
            time_str = t.strftime("%H:%M") if hasattr(t, "strftime") else str(t)
            lines.append(f"{title} on {date_str} at {time_str}")
        return "Performances: " + "; ".join(lines)

    @tool
    def search_by_date(
        date_from: str | None = None,
        date_to: str | None = None,
        film_title: str | None = None,
    ) -> str:
        """Find performances by date or date range. Dates in YYYY-MM-DD format.
        Use date_from and optionally date_to for a range; if only date_from is set, that single day is used.
        Optionally pass film_title to restrict to one film.
        """
        from sqlalchemy import and_
        from sqlalchemy.sql import select

        from common.db.db_model import Films, Performances

        if not date_from:
            return "Please provide at least date_from (YYYY-MM-DD)."
        try:
            d_from = datetime.strptime(date_from, "%Y-%m-%d").date()
        except ValueError:
            return "date_from must be YYYY-MM-DD."
        d_to = d_from
        if date_to:
            try:
                d_to = datetime.strptime(date_to, "%Y-%m-%d").date()
            except ValueError:
                return "date_to must be YYYY-MM-DD."
        if d_to < d_from:
            return "date_to must be on or after date_from."

        conditions = [
            Performances.performance_date >= d_from,
            Performances.performance_date <= d_to,
        ]
        if film_title:
            film_id = finder.get_film_id_by_title(film_title)
            if not film_id:
                return f"No film found with title like '{film_title}'."
            conditions.append(Performances.film_id == film_id)

        stmt = (
            select(Films.title, Performances.performance_date, Performances.performance_time)
            .join(Performances, Films.film_id == Performances.film_id)
            .where(and_(*conditions))
            .order_by(Performances.performance_date, Performances.performance_time)
        )
        rows = finder.execute_query_mapping_all(stmt)
        if not rows:
            return "No performances found for the given date(s)."
        lines = []
        for r in rows[:15]:
            title = r.get("title", "")
            d = r.get("performance_date")
            t = r.get("performance_time")
            date_str = d.strftime("%Y-%m-%d") if isinstance(d, date) else str(d)
            time_str = t.strftime("%H:%M") if hasattr(t, "strftime") else str(t)
            lines.append(f"{title} on {date_str} at {time_str}")
        return "Performances: " + "; ".join(lines)

    return [run_sql_query, list_available_films, search_by_characteristics, search_by_date]
