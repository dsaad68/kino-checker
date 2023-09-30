-- Create the kino schema
CREATE SCHEMA IF NOT EXISTS kino;

-- Create the films table
CREATE TABLE kino.films (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  link TEXT,
  img_link TEXT,
  last_checked TIMESTAMP,
  availability BOOLEAN DEFAULT FALSE,
  availability_date TIMESTAMP,
  imax_3d_ov BOOLEAN DEFAULT FALSE,
  imax_ov BOOLEAN DEFAULT FALSE,
  hd_ov BOOLEAN DEFAULT FALSE,
  last_update BOOLEAN DEFAULT FALSE,
  trackable BOOLEAN DEFAULT TRUE
 );

-- Create the users table
CREATE TABLE kino.users (
  id SERIAL PRIMARY KEY,
  chat_id VARCHAR(255) NOT NULL,
  message_id VARCHAR(255) NOT NULL,
  title VARCHAR(255) NOT NULL,
  notified BOOLEAN DEFAULT FALSE
 );
