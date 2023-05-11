# Kino Tracker BOT

## How to create the SQL Tables

```sql
CREATE TABLE kino.films (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  link TEXT,
  img_link TEXT,
  last_checked TIMESTAMP,
  availability BOOLEAN DEFAULT FALSE,
  imax_3d_ov BOOLEAN DEFAULT FALSE,
  imax_ov BOOLEAN DEFAULT FALSE,
  hd_ov BOOLEAN DEFAULT FALSE,
  last_update BOOLEAN DEFAULT FALSE
 );
```

```sql
CREATE TABLE kino.users (
  id SERIAL PRIMARY KEY,
  chat_id VARCHAR(255) NOT NULL,
  message_id VARCHAR(255) NOT NULL,
  title VARCHAR(255) NOT NULL,
  notified BOOLEAN DEFAULT FALSE
 );
```