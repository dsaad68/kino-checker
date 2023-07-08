FROM python:3.11.3-slim-bullseye

# Set the Timezone
ENV TZ="Europe/Berlin"
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt update && apt upgrade -y && apt install gcc -y

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the src directory contents into the container at /app/src
COPY . .

# Expose the port the app runs on
EXPOSE 80

CMD [ "python", "bot.py" ]