# Cleaner Service

Background service that:

- Marks upcoming films as released when their release date has passed.
- Marks old released films as non-trackable after a configurable number of days (see `common.constants.CLEANER_POLL_INTERVAL` and the `update_trackable_rows` parameter).

Entry point: `python -m cleaner.main`. Logging via loguru.
