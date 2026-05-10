-- =============================================================================
-- 03_artist_dominance.sql
-- =============================================================================
-- Question: For each country, who is the single most-dominant artist on its
-- chart, and what share of total chart appearances do they hold?
-- =============================================================================

WITH eligible_regions AS (
    -- Same fairness filter as Q1: only countries with at least 1,500 days of data
    SELECT region
    FROM charts
    WHERE chart = 'top200'
    GROUP BY region
    HAVING COUNT(DISTINCT date) >= 1500
),

artist_appearances AS (
    -- Count how often each artist appears in each country's chart
    SELECT
        region,
        artist,
        COUNT(*) AS appearances
    FROM charts
    WHERE chart = 'top200'
      AND artist IS NOT NULL
      AND region IN (SELECT region FROM eligible_regions)
    GROUP BY region, artist
),

ranked AS (
    -- Rank artists within each country and compute country totals
    SELECT
        region,
        artist,
        appearances,
        ROW_NUMBER() OVER (PARTITION BY region ORDER BY appearances DESC) AS rank,
        SUM(appearances) OVER (PARTITION BY region) AS country_total
    FROM artist_appearances
)

SELECT
    region,
    artist AS top_artist,
    appearances AS top_artist_appearances,
    country_total,
    ROUND(appearances * 100.0 / country_total, 2) AS top_artist_share_pct
FROM ranked
WHERE rank = 1
ORDER BY top_artist_share_pct DESC;