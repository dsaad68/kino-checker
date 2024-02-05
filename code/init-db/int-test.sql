-- add an upcoming film to upcoming_films table
INSERT INTO "tracker"."upcoming_films" ("upcoming_film_id", "title", "release_date", "film_id", "last_updated", "is_released", "is_trackable") VALUES
(100, 'test film', '2024-08-29', NULL, '2024-02-04 23:49:20.025985', 'f', 't');

-- add a film to films table
INSERT INTO "tracker"."films" ("film_id", "title", "name", "production_year", "length_in_minutes", "nationwide_start", "image_url", "last_updated") VALUES
('FFF088ETEG3IZPTOQF', 'test film', 'test film', 2022, 97, '2024-01-25', 'https://contentservice.cineorder.shop/contents/img?q=683jXDH0IV9SmgAABHGWKjb', '2024-02-04 21:29:59.176581');

-- add a performance to performances table
INSERT INTO "tracker"."performances" ("performance_id", "film_id", "film_id_p", "performance_datetime", "performance_date", "performance_time", "release_type", "is_imax", "is_ov", "is_3d", "auditorium_id", "auditorium_name", "last_updated") VALUES
('PPP088ETEG3IZPTOQF', 'FFF088ETEG3IZPTOQF', 'FFF088ETEG3IZPTOQF', '2024-02-07 20:15:00', '2024-02-07', '20:15:00', 'IMAX/englisch', 't', 't', 'f', '30000000015UHQLKCP', 'Kino 3', '2024-02-04 21:09:38.075234');
