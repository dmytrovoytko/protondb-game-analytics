/* @bruin
name: reports.games_working_top
type: duckdb.sql
connection: duckdb-default
description: |
  Game titles (free/paid) having highest number of positive verdicts.

depends:
  - staging.games_summary
  - ingest.protondb

materialization:
  type: table
strategy: replace

@bruin */

WITH VerdictCounts AS (
    SELECT 
        app_steam_appid, 
        app_title, 
        COUNT(*) AS positive_verdict_count
    FROM ingest.protondb
    WHERE responses_verdict = 1
    GROUP BY app_steam_appid, app_title
)
SELECT 
    v.app_steam_appid,
    v.app_title,
    v.positive_verdict_count,
    g.is_free
FROM VerdictCounts v
JOIN staging.games_summary g 
    ON v.app_steam_appid = g.app_id
ORDER BY v.positive_verdict_count DESC
LIMIT 100;