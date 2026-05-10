-- =============================================================================
-- 01_market_concentration.sql
-- =============================================================================
-- Question: Which countries have the most concentrated music charts?
-- Method: For each country, count total chart appearances and the share that
-- comes from the top 10 most-charting artists.
-- =============================================================================

WITH eligible_regions AS (
    SELECT region
    FROM charts
    WHERE chart = 'top200'
    GROUP BY region
    HAVING COUNT(DISTINCT date) >= 1500
),

artist_appearances AS (
    SELECT
        region,
        artist,
        COUNT(*) AS total_appearances
    FROM charts
    WHERE chart = 'top200'
      AND artist IS NOT NULL
      AND region IN (SELECT region FROM eligible_regions)
    GROUP BY region, artist
),

ranked AS (
    SELECT
        region,
        artist,
        total_appearances,
        ROW_NUMBER() OVER (
            PARTITION BY region
            ORDER BY total_appearances DESC
        ) AS artist_rank,
        SUM(total_appearances) OVER (PARTITION BY region) AS country_total
    FROM artist_appearances
)

SELECT
    region,
    SUM(CASE WHEN artist_rank <= 10 THEN total_appearances ELSE 0 END) AS top10_appearances,
    MAX(country_total) AS total_appearances,
    ROUND(
        SUM(CASE WHEN artist_rank <= 10 THEN total_appearances ELSE 0 END) * 100.0
        / MAX(country_total),
        2
    ) AS pct_from_top10
FROM ranked
GROUP BY region
ORDER BY pct_from_top10 DESC;