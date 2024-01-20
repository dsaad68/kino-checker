
-- Sample data for films table
INSERT INTO tracker.films ("film_id", "title", "name", "production_year", "length_in_minutes", "nationwide_start", "image_url", "last_updated") VALUES
('2EE63000012BHGWDVI', 'Wish', 'Wish', 2022, 95, '2023-11-30', 'https://contentservice.cineorder.shop/contents/img?q=fDJ8M3w3fDEwMjI3OTZfL3JDQ3JHNHN3a3hnRlpmbHVwNTZzeDZ5bWs1aS5qcGdffA', '2023-11-13 19:14:38.574222'),
('58E63000012BHGWDVI', 'Creator', 'Creator', 2022, 134, '2023-09-28', 'https://contentservice.cineorder.shop/contents/img?q=683jXDv0IV9SmgAABHGWNjb', '2023-11-13 19:14:38.574222'),
('A6D63000012BHGWDVI', 'Wonka', 'Wonka', 2021, 120, '2023-12-07', 'https://contentservice.cineorder.shop/contents/img?q=fDJ8M3w3fDc4NzY5OV8vZXQxT2ZSdmZ3V21Ua1lpandxYUR3S0ZnWTFsLmpwZ19kZXw', '2023-11-13 19:14:38.574222'),
('DCC63000012BHGWDVI', 'The Marvels', 'The Marvels', 2020, 105, '2023-11-09', 'https://contentservice.cineorder.shop/contents/img?q=683jXDP2IV9SmgAABHGWJjb', '2023-11-13 19:14:38.574222'),
('FCE63000012BHGWDVI', 'Saw X', 'Saw X', 2022, 119, '2023-11-30', 'https://contentservice.cineorder.shop/contents/img?q=683jXDH0IV9SmgAABHGWJjb', '2023-11-13 19:14:38.574222');

-- Sample data for upcoming_films table
INSERT INTO tracker.upcoming_films ("title", "release_date", "film_id", "last_updated", "is_released", "is_trackable") VALUES
('Napoleon', '2023-11-23', NULL, NULL, 'f', 't'),
('SAW X', '2023-11-30', NULL, NULL, 'f', 't'),
('Wish', '2023-11-30', NULL, NULL, 'f', 't'),
('Raus aus dem Teich', '2023-12-21', NULL, NULL, 'f', 't');

-- Sample data for performances table
-- INFO: performance_datetime performance_datetime is always 10 days from current date
INSERT INTO tracker.performances ("performance_id", "film_id", "film_id_p", "performance_datetime", "performance_date", "performance_time", "release_type", "is_imax", "is_ov", "is_3d", "auditorium_id", "auditorium_name", "last_updated") VALUES
('71D45000023UHQLKCP', 'A6D63000012BHGWDVI', 'A6D63000012BHGWDVI', CURRENT_TIMESTAMP + INTERVAL '10 days', CURRENT_DATE + INTERVAL '10 days', '17:15:00', 'englisch/OV', 'f', 't', 'f', '10000000015UHQLKCP', 'Kino 1', '2023-11-13 19:14:38.658222'),
('61D45000023UHQLKCP', 'A6D63000012BHGWDVI', 'A6D63000012BHGWDVI', CURRENT_TIMESTAMP + INTERVAL '10 days', CURRENT_DATE + INTERVAL '10 days', '20:00:00', 'IMAX/Digital', 't', 'f', 'f', '30000000015UHQLKCP', 'Kino 3', '2023-11-13 19:14:38.658222'),
('C9C45000023UHQLKCP', 'DCC63000012BHGWDVI', 'DCC63000012BHGWDVI', '2023-11-13 20:00:00', '2023-11-13', '20:00:00', 'englisch/IMAX/OV/3D', 't', 't', 't', '30000000015UHQLKCP', 'Kino 3', '2023-11-13 19:14:38.658222'),
('B5C45000023UHQLKCP', 'DCC63000012BHGWDVI', 'DCC63000012BHGWDVI', '2023-11-14 17:00:00', '2023-11-14', '17:00:00', 'englisch/IMAX/OV/3D', 't', 't', 't', '30000000015UHQLKCP', 'Kino 3', '2023-11-13 19:14:38.658222');

-- Sample data for users table
INSERT INTO tracker.users ("chat_id", "message_id", "film_id", "title", "notified") VALUES
('222211111', '1010', NULL, 'Wish', 'f'),
('222211111', '1020', 'A6D63000012BHGWDVI', 'Wonka', 'f'),
('222211111', '1030', NULL, 'Napoleon', 'f');
