-- Create the tracker schema
CREATE SCHEMA IF NOT EXISTS tracker;

-- Create the films table
CREATE TABLE tracker.films (
    film_id VARCHAR(255) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    production_year INTEGER,
    length_in_minutes INTEGER,
    nationwide_start VARCHAR(255),
    image_url VARCHAR(255),
    last_updated TIMESTAMP
);

CREATE TABLE tracker.performances (
    performance_id VARCHAR(255) PRIMARY KEY,
    film_id VARCHAR(255),
    film_id_p VARCHAR(255),
    performance_datetime TIMESTAMP,
    performance_date DATE,
    performance_time TIME,
    release_type VARCHAR(255),
    is_imax BOOLEAN,
    is_ov BOOLEAN,
    is_3d BOOLEAN,
    auditorium_id VARCHAR(255),
    auditorium_name VARCHAR(255),
    last_updated TIMESTAMP,
    FOREIGN KEY (film_id) REFERENCES tracker.films(film_id)
);

-- Create the upcoming films table
CREATE TABLE tracker.upcoming_films (
    upcoming_film_id SERIAL PRIMARY KEY,
    -- Add a unique constraint to the title column
    title VARCHAR(255) NOT NULL UNIQUE,
    release_date DATE,
    film_id VARCHAR(255),
    last_updated TIMESTAMP,
    is_released BOOLEAN DEFAULT FALSE,
    is_trackable BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (film_id) REFERENCES tracker.films(film_id)
);

-- Create the users table
CREATE TABLE tracker.users (
    user_id SERIAL PRIMARY KEY,
    chat_id VARCHAR(255) NOT NULL,
    message_id VARCHAR(255) NOT NULL,
    film_id VARCHAR(255),
    title VARCHAR(255) NOT NULL,
    notified BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (film_id) REFERENCES tracker.films(film_id)
);
