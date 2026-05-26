/* @bruin
name: reports.games_top
type: duckdb.sql
connection: duckdb-default
description: |
  Game titles (free/paid) with estimated number of owners (= copies installed/sold).

depends:
  - staging.games_summary

materialization:
  type: table
strategy: replace

@bruin */

SELECT 
    app_id, 
    app_name, 
    release_year, 
    min_owners, 
    max_owners, 
    is_free, 
    app_price
FROM staging.games_summary
WHERE min_owners > 0
ORDER BY max_owners DESC, is_free ASC  
