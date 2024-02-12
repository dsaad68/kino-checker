[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Python Test and Lint](https://github.com/dsaad68/kino-checker/actions/workflows/main.yml/badge.svg)](https://github.com/dsaad68/kino-checker/actions/workflows/main.yml)
# Kino Tracker Bot (with GenAI Features)

Kino Tracker Bot is a Telegram bot that tracks the availability of movies in selected cinemas and notifies users when a movie becomes available.

With the addition of a GenAI feature, users can now inquire about upcoming and currently showing films in natural language, thanks to the integration with a langchain SQL agent.
Moreover, responses are enhanced with voice outputs generated by the Eleven Labs Voice API, providing a more interactive and engaging user experience.

Features:
- Tracks the availability of movies in selected cinemas.
- Notifies users when a movie becomes available.
- *New*: GenAI feature for asking about upcoming and showing films in natural language.
- *New*: Voice-generated answers through Eleven Labs Voice API for a more immersive experience.

## How to Run the Bot

1. *Set the environment variables*\n
Use the .env file to add environment variables for Docker Compose.
2. *To start a the bot, you can use the docker-compose up command in the terminal.*\n
```shell
docker compose up
```

## How to Install Pre-commit

To ensure your commits meet the repository's code standards, install the pre-commit hooks using the following command:

```sh
pre-commit install
```
