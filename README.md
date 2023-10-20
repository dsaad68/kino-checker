[![Python Test and Lint](https://github.com/dsaad68/kino-checker/actions/workflows/main.yml/badge.svg)](https://github.com/dsaad68/kino-checker/actions/workflows/main.yml)
# Kino Tracker Bot

Kino Tracker Bot is a Telegram bot that tracks the availability of movies in a selected cinemas and notifies users when a movie becomes available.

Features
* Tracks the availability of movies in selected cinemas
* Notifies users when a movie becomes available

*This bot requires a PostgreSQL database to store the user data. The database is not included in this repository.*

## How to run the bot

1. Create symlinks to my_logger folder for each service in docker-compose.yml
`mklink /D my_logger ..\my_logger``
2. *Set the environment variables*\n
Use the .env file to add environment variables for Docker Compose.
3. *Initialize the database*\n
Use `init-db\init-db.sql` to init the database.
4. *To start a the bot, you can use the docker-compose up command in the terminal.*\n
```shell
docker compose up
```

## How to install pre-commit

```sh
pre-commit install
```
