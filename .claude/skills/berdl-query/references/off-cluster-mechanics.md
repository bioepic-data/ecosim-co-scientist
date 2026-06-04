# Off-Cluster Mechanics

## Reliability Tips

- Prefer bounded queries with explicit limits first.
- Keep an active BERDL session open while running large queries.
- Re-run a lightweight probe (`SELECT 1`) after reconnecting.

## Export Strategy

- Small/medium results: inline return.
- Large results: export to object storage and retrieve with MinIO tooling.

## If Helper Scripts Are Missing

Run equivalent `spark.sql(...)` queries directly in the active Spark environment and use DataFrame writers for exports.
