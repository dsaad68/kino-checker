# Bot Service

Telegram bot that:

- Lists upcoming and showing films; users can subscribe to be notified when a film becomes available.
- Answers natural-language questions about films using a Langchain SQL agent and the shared PostgreSQL database.
- Sends voice replies via the Eleven Labs API.

Entry point: `python -m bot.main`. Logging is configured via `common.logging_config` (loguru).
