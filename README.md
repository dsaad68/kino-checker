# Kino Tracker Bot

Kino Tracker Bot is a Telegram bot that tracks the availability of movies in selected cinemas and notifies users when a movie becomes available.

Features
* Tracks the availability of movies in selected cinemas
* Notifies users when a movie becomes available

*This bot requires a PostgreSQL database to store the user data. The database is not included in this repository.*

## How to run the bot

1. *Set the environment variables*\n
Use the .env file to add environment variables for Docker Compose.
2. *Initialize the database*\n
Use `init-db\init-db.sql` to init the database.
3. *To start a the bot, you can use the docker-compose up command in the terminal.*\n
```shell
docker compose up
```