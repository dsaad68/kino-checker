-- Create the kino schema
CREATE SCHEMA IF NOT EXISTS tracker;

-- Create the films table
-- CREATE TABLE kino.films (
--   id SERIAL PRIMARY KEY,
--   title VARCHAR(255) NOT NULL,
--   link TEXT,
--   img_link TEXT,
--   last_checked TIMESTAMP,
--   availability BOOLEAN DEFAULT FALSE,
--   availability_date TIMESTAMP,
--   imax_3d_ov BOOLEAN DEFAULT FALSE,
--   imax_ov BOOLEAN DEFAULT FALSE,
--   hd_ov BOOLEAN DEFAULT FALSE,
--   last_update BOOLEAN DEFAULT FALSE,
--   trackable BOOLEAN DEFAULT TRUE
--  );


-- TODO: Update the table
-- Create the users table
CREATE TABLE tracker.users (
  id SERIAL PRIMARY KEY,
  chat_id VARCHAR(255) NOT NULL,
  message_id VARCHAR(255) NOT NULL,
  title VARCHAR(255) NOT NULL,
  notified BOOLEAN DEFAULT FALSE
 );


-- TODO: Update the film table
CREATE TABLE tracker.films (
    film_id VARCHAR(255) PRIMARY KEY,
    production_year INT,
    name VARCHAR(255),
    title VARCHAR(255),
    original_title VARCHAR(255),
    length_in_minutes INT,
    image_url VARCHAR(255),
    nationwide_start DATE,
    age_rating INT
);

-- TODO: Update the performance table
CREATE TABLE tracker.performance (
    performance_id VARCHAR(255) PRIMARY KEY,
    film_id VARCHAR(255),
    title VARCHAR(255),
    performance_date_time DATETIME,
    cinema_date DATE,
    auditorium_name VARCHAR(255),
    auditorium_number INT,
    auditorium_id VARCHAR(255),
    release_type_name VARCHAR(255),
    is_3D BOOLEAN,
    weekfilm_sort_order_prio INT,
    FOREIGN KEY (film_id) REFERENCES film_information(film_id)
);
