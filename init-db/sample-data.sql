
-- Sample data for films table
INSERT INTO "kino"."films" ("id", "title", "link", "img_link", "last_checked", "availability", "imax_3d_ov", "imax_ov", "hd_ov", "last_update") VALUES
(25, 'The Equalizer 3', 'https://www.filmpalast.net/film/the-equalizer-3.html', 'https://www.filmpalast.net/fileadmin/_processed_/4/6/the-equalizer-3.jpg', '2023-07-20 00:04:53', 't', 'f', 'f', 't', 'f');

INSERT INTO "kino"."films" ("id", "title", "link", "img_link", "last_checked", "availability", "imax_3d_ov", "imax_ov", "hd_ov", "last_update") VALUES
(26, 'Oppenheimer', 'https://www.filmpalast.net/film/oppenheimer.html', 'https://www.filmpalast.net/img/film/oppenheimer.jpg', Null, 't', 'f', 't', 't', 'f');

INSERT INTO "kino"."films" ("id", "title", "link", "img_link", "last_checked", "availability", "imax_3d_ov", "imax_ov", "hd_ov", "last_update") VALUES
(15, 'The Flash', 'https://www.filmpalast.net/film/the-flash.html', 'https://www.filmpalast.net/fileadmin/_processed_/1/6/the_flash.jpg', Null, 'f', 'f', 'f', 'f', 'f');

INSERT INTO "kino"."films" ("id", "title", "link", "img_link", "last_checked", "availability", "imax_3d_ov", "imax_ov", "hd_ov", "last_update") VALUES
(11, 'Transformers - Aufstieg der Bestien', 'https://www.filmpalast.net/film/transformers-aufstieg-der-bestien.html', 'https://www.filmpalast.net/fileadmin/_processed_/8/6/transformers_aufstieg_der_bestien.jpg', '2023-06-08 00:03:14', 't', 't', 'f', 'f', 't');

-- Sample data for users table
INSERT INTO "kino"."users" ("id", "chat_id", "message_id", "title", "notified") VALUES
(5, '200788221', '1073', 'The Equalizer 3', 'f');
