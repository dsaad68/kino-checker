# API Documentation

Kino-Checker does not expose a REST API. Interaction is through:

- **Telegram Bot** — Users send commands and messages to the bot; the bot responds with text and voice (Eleven Labs). Commands include `/start`, `/Upcoming_Films`, `/Ask`, etc.
- **Database** — Services share a PostgreSQL database; schema and tables are defined in [code/init-db/init-db.sql](../code/init-db/init-db.sql).

For programmatic use of the database, see the SQLAlchemy models and `DBManager` in `code/common/src/common/db/`.
