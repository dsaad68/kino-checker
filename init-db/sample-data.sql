
-- Sample data for films table
INSERT INTO "kino"."films" ("id", "title", "link", "img_link", "last_checked", "availability", "imax_3d_ov", "imax_ov", "hd_ov", "last_update") VALUES
(25, 'Barbie', 'https://www.filmpalast.net/film/barbie.html', 'https://www.filmpalast.net/fileadmin/_processed_/4/6/csm_DE_Barbie_Teaser_jpg_700_f2e24a3a5a.jpg', '2023-07-20 00:04:53', 't', 'f', 'f', 't', 't');
INSERT INTO "kino"."films" ("id", "title", "link", "img_link", "last_checked", "availability", "imax_3d_ov", "imax_ov", "hd_ov", "last_update") VALUES
(26, 'Oppenheimer', 'https://www.filmpalast.net/film/oppenheimer.html', 'https://www.filmpalast.net/fileadmin/_processed_/3/9/csm_Oppenheimer-Motiv2-A4-RGB_s_bcc508854d.jpg', '2023-07-20 00:04:54', 't', 'f', 't', 't', 't');
INSERT INTO "kino"."films" ("id", "title", "link", "img_link", "last_checked", "availability", "imax_3d_ov", "imax_ov", "hd_ov", "last_update") VALUES
(15, 'The Flash', 'https://www.filmpalast.net/film/the-flash.html', 'https://www.filmpalast.net/fileadmin/_processed_/1/6/csm_DE_TFLSH_VERT_INTL_Montage_2764x4096_5be5ee627a.jpg', '2023-06-15 00:03:11', 't', 'f', 't', 't', 't');
INSERT INTO "kino"."films" ("id", "title", "link", "img_link", "last_checked", "availability", "imax_3d_ov", "imax_ov", "hd_ov", "last_update") VALUES
(11, 'Transformers - Aufstieg der Bestien', 'https://www.filmpalast.net/film/transformers-aufstieg-der-bestien.html', 'https://www.filmpalast.net/fileadmin/_processed_/8/6/csm_TF7_INTL_DGTL_Payoff_Digital_Key_Art_Unite_2480x3508_GER_4520281759.jpg', '2023-06-08 00:03:14', 't', 't', 'f', 'f', 't');

-- Sample data for users table
INSERT INTO "kino"."users" ("id", "chat_id", "message_id", "title", "notified") VALUES
(5, '200788221', '1073', 'Barbie', 'f');
INSERT INTO "kino"."users" ("id", "chat_id", "message_id", "title", "notified") VALUES
(28, '200788221', '1147', 'Spider-Man: Across the Spider-Verse türkische Fassung', 'f');
INSERT INTO "kino"."users" ("id", "chat_id", "message_id", "title", "notified") VALUES
(4, '200788221', '388', 'Insidious: The Red Door', 'f');