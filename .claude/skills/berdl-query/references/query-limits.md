# Query Size Guidance

## Suggested Thresholds

- Small: <= 10k rows or <= 10 MB
- Medium: 10k-500k rows or 10-200 MB
- Large: > 500k rows or > 200 MB

## Recommended Mode

- Small: return inline
- Medium: inline only if user explicitly needs it; otherwise export
- Large: export to object storage

Always include `LIMIT` in exploratory queries unless the user explicitly requests full scans.
