/* @bruin
name: staging.games_summary
type: duckdb.sql
connection: duckdb-default
description: |
  Transforms and normalizes Steam games data from raw.

depends:
  - ingest.games

materialization:
  type: table
strategy: replace

@bruin */

SELECT 
    app_id, 
    name AS app_name, 
    CAST(RIGHT(release_date, 4) AS INTEGER) AS release_year, 
    CAST(SPLIT_PART(estimated_owners, ' - ', 1) AS INTEGER) AS min_owners, 
    CAST(SPLIT_PART(estimated_owners, ' - ', 2) AS INTEGER) AS max_owners, 
    CASE WHEN price = 0 THEN 1 ELSE 0 END AS is_free, 
    price AS app_price
FROM ingest.games 
WHERE min_owners > 0
ORDER BY max_owners DESC, is_free ASC  
