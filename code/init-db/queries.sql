-- Released Films
SELECT *
FROM tracker.films AS films
WHERE films.title IN ( SELECT title
					   FROM tracker.upcoming_films
					   WHERE is_trackable=TRUE AND is_released=FALSE);


-- Update Released Films
UPDATE tracker.upcoming_films
SET
    film_id = f.film_id,
    is_released = TRUE
FROM tracker.films f
WHERE
    tracker.upcoming_films.title = f.title
    AND tracker.upcoming_films.is_trackable = TRUE;

-- Update Users with Released Films
UPDATE tracker.users u
SET film_id = f.film_id
FROM tracker.films f
JOIN tracker.upcoming_films uf ON f.title = uf.title
WHERE uf.is_trackable = TRUE
AND uf.is_released = FALSE
AND u.title = f.title;


WITH film_info AS (
    SELECT
        f.film_id,
        f.title,
        f.length_in_minutes,
        f.last_updated,
        f.nationwide_start,
        BOOL_OR(p.is_imax) AS is_imax,
        BOOL_OR(p.is_ov) AS is_ov,
        BOOL_OR(p.is_3d) AS is_3d
    FROM
        tracker.films f
    JOIN
        tracker.performances p ON f.film_id = p.film_id
    GROUP BY
        f.film_id
)
SELECT
    u.chat_id,
    u.message_id,
    fi.title,
    fi.length_in_minutes,
    fi.last_updated,
    fi.nationwide_start,
    fi.is_imax,
    fi.is_ov,
    fi.is_3d
FROM
    tracker.users u
LEFT JOIN
    film_info fi ON u.film_id = fi.film_id
WHERE
    u.film_id IS NOT NULL
    AND NOT u.notified;
