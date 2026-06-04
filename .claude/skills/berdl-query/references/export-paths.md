# Export Path Conventions

Use stable, timestamped paths for large result exports.

Example pattern:

`s3a://cdm-lake/users-general-warehouse/<user>/exports/<YYYYMMDD>-<topic>/`

## Format Choices

- `parquet`: preferred for large structured outputs
- `csv`: use for interoperability when size is manageable

Use explicit write mode (`overwrite` or `append`) and document which was used.
