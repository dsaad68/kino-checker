-- Sample data for upcoming_films table
INSERT INTO tracker.upcoming_films ("title", "release_date", "film_id", "last_updated", "is_released", "is_trackable") VALUES
('Napoleon', CURRENT_TIMESTAMP - INTERVAL '130 days', NULL, NULL, 't', 't'),
('SAW X', CURRENT_TIMESTAMP - INTERVAL '150 days', NULL, NULL, 't', 'f'),
('Wish', CURRENT_TIMESTAMP + INTERVAL '10 days', NULL, NULL, 't', 't'),
('Raus aus dem Teich', CURRENT_TIMESTAMP + INTERVAL '10 days', NULL, NULL, 'f', 't');
