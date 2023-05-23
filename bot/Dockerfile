FROM python:3.11.3-slim-bullseye

# Set the Timezone
RUN echo "Europe/Berlin" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata

RUN echo "Europe/Berlin" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata

RUN apt update && apt upgrade -y && apt install gcc -y

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the src directory contents into the container at /app/src
COPY . .

# Set the TelegramBotToken environment variable
ENV Telegram_Dev_Bot= <BOT_TOKEN>
ENV KINO_POSTGRES_CONNECTION_URI= <POSTGRES_CONNECTION_URI>

# Expose the port the app runs on
EXPOSE 80

CMD [ "python", "bot.py" ]