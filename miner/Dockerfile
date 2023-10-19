FROM python:3.11.3-slim-bullseye

# Set the Timezone
ENV TZ="Europe/Berlin"
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt update && apt upgrade -y && apt install gcc -y && apt-get clean

WORKDIR /app

# Copy the directory contents into the container at /app/
COPY ./miner .

# Install requirements
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Install the custom logger
COPY ./my_logger ./my_logger
RUN pip install --no-cache-dir ./my_logger

# Expose the port the app runs on
EXPOSE 80

CMD [ "python", "miner.py" ]
