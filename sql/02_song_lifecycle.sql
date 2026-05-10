-- =============================================================================
-- 02_song_lifecycle.sql
-- =============================================================================
-- Question: For songs that reached #1 in the United States, what was their
-- chart lifecycle? Days from chart entry to peak, days at #1, total days on
-- chart. Compare the early period (2017-18) vs late period (2020-21).
-- =============================================================================

WITH us_top200 AS (
    -- Just the US top 200 chart, narrowed to relevant columns
    SELECT title, artist, date, rank
    FROM charts
    WHERE chart = 'top200'
      AND region = 'United States'
),

-- Identify every song that ever reached #1 in the US
number_one_songs AS (
    SELECT DISTINCT title, artist
    FROM us_top200
    WHERE rank = 1
),

-- Get all chart appearances for those songs only
hit_appearances AS (
    SELECT u.title, u.artist, u.date, u.rank
    FROM us_top200 u
    INNER JOIN number_one_songs n
        ON u.title = n.title
       AND u.artist = n.artist
),

-- Calculate lifecycle metrics for each hit song
lifecycle AS (
    SELECT
        title,
        artist,
        MIN(date) AS first_chart_date,
        MAX(date) AS last_chart_date,
        MIN(CASE WHEN rank = 1 THEN date END) AS first_number_one_date,
        MAX(CASE WHEN rank = 1 THEN date END) AS last_number_one_date,
        SUM(CASE WHEN rank = 1 THEN 1 ELSE 0 END) AS days_at_number_one,
        COUNT(*) AS total_days_on_chart
    FROM hit_appearances
    GROUP BY title, artist
)

SELECT
    title,
    artist,
    first_chart_date,
    first_number_one_date,
    last_chart_date,
    days_at_number_one,
    total_days_on_chart,
    DATE_DIFF('day', first_chart_date, first_number_one_date) AS days_to_reach_number_one,
    DATE_DIFF('day', first_number_one_date, last_chart_date) AS days_after_peak,
    CASE
        WHEN first_number_one_date < DATE '2019-01-01' THEN 'Early (2017-18)'
        WHEN first_number_one_date < DATE '2020-07-01' THEN 'Mid (2019-mid 2020)'
        ELSE 'Late (mid 2020-21)'
    END AS era
FROM lifecycle
WHERE DATE_DIFF('day', first_chart_date, first_number_one_date) <= 365
ORDER BY first_number_one_date;