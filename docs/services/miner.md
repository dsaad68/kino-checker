# Miner Service

Background service that:

- Fetches film and performance data from cinema APIs and scrapes upcoming releases.
- Updates the shared database (films, performances, upcoming_films).
- Marks released films, updates user-film links, and sends Telegram notifications to subscribed users.
- Runs in a loop with a configurable poll interval (see `common.constants.MINER_POLL_INTERVAL`).

Entry point: `python -m miner.main`. Logging via loguru.
