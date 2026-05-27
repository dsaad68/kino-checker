# Notifier Redesign

## Goal

When a user subscribes to a film via the Telegram bot:

1. **On release** — send one notification that the film is now available,
   regardless of whether their preferred version (IMAX / OV / 3D) exists
   yet. If matching performances already exist at release time, include
   them in the same message.
2. **As preferred showtimes appear** — for every subsequent performance
   that matches their preferences, send a notification.

This covers all three cases: preferred version present at release,
preferred version added later, preferred version never appears (the user
at least knows the film came out).

---

## What's there today

Notifications live **inside the miner**
(`code/miner/src/miner/main.py:79-101`, `utils/film_notifier.py`,
`utils/film_db_manager.py:279-373`).

Flow:

1. Bot writes one row to `tracker.users` per `(chat_id, film_title)` with an
   encoded flag string like `1,ov|0,imax|2,3d` and `notified=FALSE`
   (`bot/utils/db_info_finder.py:76-100`).
2. Every 20 min the miner upserts `films` + `performances` from the
   Filmpalast API, scrapes `upcoming_films`, then runs
   `update_released_films_in_upcoming_films_table` →
   `update_users_table` → `get_users_to_notify` → send → flip
   `notified=TRUE`.
3. The trigger is **film release** (title appears in `films`), not ticket
   availability. After the first notification per `(user, film)`, that
   subscription is dead.

---

## Gaps

- **One-shot per film, not per matching performance.** A later-added IMAX
  showtime never reaches the subscriber — `notified=TRUE` already.
- **Notifier is fused into the miner.** Same loop, same process, same DB
  connection. A Telegram failure blocks the next mine; a scraper hiccup
  delays sends.
- **`users.flags` is a delimited string** (`1,ov|0,imax|2,3d`). Can't filter
  in SQL, can't index, hard to extend.
- **No retry, no audit log, no rate-limit handling.** `asyncio.gather`
  swallows per-user failures into the aggregate.
- **No preference management** — no list / edit / cancel commands.

---

## Target architecture

Split a dedicated **notifier** service (sibling of `miner` / `cleaner` /
`bot`) whose only job is: send release announcements and per-performance
match notifications, log the outcome. The miner becomes a pure scraper.

The notifier sends **two kinds of notifications** per subscription:

- **`release`** — fires once, when the film first transitions from
  upcoming to showing (i.e. `films.film_id` becomes resolvable from
  `subscriptions.title`). Always fires, regardless of preference match. If
  matching performances exist at release time, they ride along in the
  same message (and corresponding `match` rows are written so they don't
  re-notify).
- **`match`** — fires once per `(subscription, performance)` pair for any
  performance that satisfies the user's preferences, deduped by the
  unique key on `notifications`. Only runs after the `release` row
  exists, so users never get a match notification before they've been
  told the film is out.

Dedup lives entirely in the `notifications` table — there's no
`notified` flag on the subscription. `LEFT JOIN notifications` is what
makes new showtimes flow through automatically and gives a real audit
trail.

### Schema

Replace `tracker.users` with two normalized tables.

```sql
CREATE TABLE tracker.subscriptions (
  subscription_id  SERIAL PRIMARY KEY,
  chat_id          VARCHAR(255) NOT NULL,
  title            VARCHAR(255) NOT NULL,         -- film user picked from upcoming list
  film_id          VARCHAR(255) REFERENCES tracker.films(film_id), -- resolved on release
  want_imax        BOOLEAN,                       -- NULL = don't care
  want_ov          BOOLEAN,
  want_3d          BOOLEAN,
  is_active        BOOLEAN DEFAULT TRUE,
  message_id       VARCHAR(255),                  -- bot's reply, for editing later
  created_at       TIMESTAMP DEFAULT NOW(),
  updated_at       TIMESTAMP DEFAULT NOW(),
  UNIQUE (chat_id, title)
);

CREATE TABLE tracker.notifications (
  notification_id    BIGSERIAL PRIMARY KEY,
  subscription_id    INT REFERENCES tracker.subscriptions(subscription_id) ON DELETE CASCADE,
  performance_id     VARCHAR(255) REFERENCES tracker.performances(performance_id) ON DELETE CASCADE,
  notification_type  VARCHAR(16) NOT NULL,        -- 'release' | 'match'
  chat_id            VARCHAR(255) NOT NULL,       -- denormalized for fast send
  status             VARCHAR(16) NOT NULL,        -- 'sent' | 'failed'
  telegram_msg_id    VARCHAR(255),
  error              TEXT,
  sent_at            TIMESTAMP DEFAULT NOW(),
  CHECK (
    (notification_type = 'release' AND performance_id IS NULL) OR
    (notification_type = 'match'   AND performance_id IS NOT NULL)
  )
);

-- one release per subscription
CREATE UNIQUE INDEX uq_notif_release
  ON tracker.notifications(subscription_id)
  WHERE notification_type = 'release';

-- one match per (subscription, performance)
CREATE UNIQUE INDEX uq_notif_match
  ON tracker.notifications(subscription_id, performance_id)
  WHERE notification_type = 'match';

CREATE INDEX idx_notifications_sub ON tracker.notifications(subscription_id);
CREATE INDEX idx_subscriptions_active_film
  ON tracker.subscriptions(is_active, film_id) WHERE is_active;
```

Killing the `flags` string is the biggest cleanup — `NULL` / `TRUE` /
`FALSE` lets the match happen in SQL instead of Python.

### New service layout

`code/notifier/` mirrors `cleaner/` and `miner/`:

```
code/notifier/
  src/notifier/
    main.py
    utils/
      matcher.py        # the SQL match query + record writes
      sender.py         # AsyncTeleBot wrapper with retry/backoff
      message.py        # message text + URL builder (moved from miner)
  pyproject.toml
  Dockerfile
```

Add it to `docker-compose.yml` alongside the miner. Reuses `common/` for
DB, config, logging.

### Main loop

Poll every ~60 s (LISTEN/NOTIFY can come later if polling pressure shows
up). Each tick runs three steps in order:

```python
while True:
    matcher.resolve_film_ids()                          # 1
    pending_release = matcher.find_pending_releases()   # 2
    if pending_release:
        asyncio.run(sender.send_releases(pending_release, bot_token))
    pending_match = matcher.find_pending_matches()      # 3
    if pending_match:
        asyncio.run(sender.send_matches(pending_match, bot_token))
    time.sleep(NOTIFIER_POLL_INTERVAL)
```

Step ordering matters: a subscription must have a `release` notification
before any `match` rows are written, so that the user always hears
"film is out" first.

### Step 1 — resolve `film_id`

Subscriptions are created with `film_id IS NULL` (the bot only knows the
title from the upcoming list). Once the film appears in `tracker.films`,
fill the FK in:

```sql
UPDATE tracker.subscriptions s
SET film_id = f.film_id, updated_at = NOW()
FROM tracker.films f
WHERE s.is_active
  AND s.film_id IS NULL
  AND lower(s.title) = lower(f.title);
```

### Step 2 — release announcements

Find every active subscription whose film has resolved but which has no
`release` row yet:

```sql
SELECT s.subscription_id, s.chat_id, s.title, s.film_id,
       s.want_imax, s.want_ov, s.want_3d, f.name
FROM tracker.subscriptions s
JOIN tracker.films f ON f.film_id = s.film_id
LEFT JOIN tracker.notifications n
       ON n.subscription_id = s.subscription_id
      AND n.notification_type = 'release'
WHERE s.is_active
  AND s.film_id IS NOT NULL
  AND n.notification_id IS NULL;
```

For each row, the notifier:

1. Queries currently-available matching performances for the subscription
   (same preference filter as Step 3).
2. Sends one Telegram message:
   - **With matches:** *"X is now available! Your IMAX showtimes: …"*
   - **Without matches:** *"X is now available. No IMAX showings yet —
     we'll let you know when one is added."*
3. Writes a `release` row with `performance_id = NULL`.
4. Writes a `match` row for each performance included in the message, so
   Step 3 doesn't re-notify them.

All four DB writes for one subscription happen in a single transaction to
keep the bookkeeping consistent on send failures.

### Step 3 — match notifications

Same shape as the original match query, with two extra clauses: only
subscriptions that already have a `release` row, and dedup against
`match`-type rows:

```sql
SELECT s.subscription_id, s.chat_id, f.film_id, f.name, f.title,
       p.performance_id, p.performance_date, p.performance_time,
       p.is_imax, p.is_ov, p.is_3d
FROM tracker.subscriptions s
JOIN tracker.films f         ON f.film_id = s.film_id
JOIN tracker.performances p  ON p.film_id = s.film_id
JOIN tracker.notifications r                        -- release must exist
       ON r.subscription_id = s.subscription_id
      AND r.notification_type = 'release'
LEFT JOIN tracker.notifications m
       ON m.subscription_id = s.subscription_id
      AND m.performance_id  = p.performance_id
      AND m.notification_type = 'match'
WHERE s.is_active
  AND m.notification_id IS NULL              -- never matched this pair
  AND (s.want_imax IS NULL OR s.want_imax = p.is_imax)
  AND (s.want_ov   IS NULL OR s.want_ov   = p.is_ov)
  AND (s.want_3d   IS NULL OR s.want_3d   = p.is_3d)
  AND p.performance_datetime > NOW();        -- skip past shows
```

This is the engine for *"the preferred version arrived later"* — any new
performance the miner inserts that matches preferences shows up here on
the next tick.

### Send + record

One row per send, success or failure. Same shape for both `release` and
`match`:

```python
for item in pending:
    try:
        msg = await bot.send_message(item.chat_id, build_text(item))
        db.record(item, status='sent', telegram_msg_id=msg.message_id)
    except ApiTelegramException as e:
        db.record(item, status='failed', error=str(e))
        # 429 → respect retry-after; 403 → mark subscription inactive
```

Per-send recording: a Telegram failure for one user doesn't lose other
sends and doesn't block re-attempts later (no row in `notifications`
means the item is still pending and will be picked up next tick).

### Miner becomes pure scraper

Strip everything after line ~70 in `miner/main.py` — release detection,
user notification, `notified` updates all go away. The miner only keeps
`films` / `performances` / `upcoming_films` fresh; the notifier reads
from those tables and owns all user-facing logic.

### Cleaner adds subscription expiry

The `cleaner` already marks `upcoming_films.is_trackable = FALSE` 120
days after release. Add one extra statement so dormant subscriptions
don't accumulate:

```sql
UPDATE tracker.subscriptions s
SET is_active = FALSE, updated_at = NOW()
FROM tracker.upcoming_films uf
WHERE s.is_active
  AND lower(s.title) = lower(uf.title)
  AND uf.is_trackable = FALSE;
```

### Bot changes

- `upsert_users()` → `upsert_subscription()` writes `want_imax / want_ov /
  want_3d` as `True / False / None` instead of the encoded string.
- New commands:
  - `/mysubs` — list active subscriptions.
  - `/unsub` — deactivate by film (sets `is_active = FALSE`).
  - Optional: `/pause`, `/resume`.

---

## Migration plan

Two safe phases.

**Phase 1 — add alongside.**

1. Create `subscriptions` and `notifications` tables (keep `users` intact).
2. Backfill: `INSERT INTO subscriptions … SELECT … FROM users`, using a
   one-shot parser for the `flags` string to populate `want_imax /
   want_ov / want_3d`.
3. Backfill `notifications` from `users WHERE notified = TRUE`: insert
   one `release` row per already-notified user-film pair so they don't
   get a duplicate release announcement after the cutover. `match` rows
   are *not* backfilled — we accept that the very first notifier tick
   may send `match` notifications for performances that were already
   bundled into the original release message. The alternative
   (best-effort historical reconstruction) is brittle and not worth the
   complexity.
4. Deploy the new notifier service. Stop the miner's notification step
   in the same release.
5. Update the bot to write to `subscriptions` and add `/mysubs` /
   `/unsub`.
6. Update the cleaner to deactivate subscriptions for untrackable films.

**Phase 2 — drop old table.** After the notifier runs clean for ~1 week,
drop `tracker.users`.

---

## Suggested commit order

1. Schema + migration SQL (`init-db/init-db.sql` + one-shot migration
   script).
2. New `notifier/` service + Docker wiring (release step + match step).
3. Bot updates (`upsert_subscription`, `/mysubs`, `/unsub`).
4. Strip notification code from the miner.
5. Cleaner subscription expiry.
6. Drop `tracker.users`.
