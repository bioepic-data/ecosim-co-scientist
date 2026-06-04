# Query Patterns and Safety Rules

Reference guidance for constructing safe, performant BERDL queries.

## Mandatory Validation Checklist

Before executing any query, verify all items:

- Partition/key filter present on large tables (for example species/org/genome IDs)
- Large-table guard applied before joins
- Result set bounded (`LIMIT`, aggregation, or narrow `WHERE`)
- String-typed numerics cast before comparison
- Annotation NULL/sentinel values filtered (`-`, `NULL`) where relevant
- `ORDER BY` present for pagination
- JOIN keys validated

## Performance Tiers

| Expected Result Size | Strategy |
|---|---|
| Small | Bounded SQL; transfer summarized rows |
| Medium | Filter and aggregate in SQL first |
| Large | Run in Spark environment and write outputs to storage |

## Common Safe Patterns

### Species-first filtering

```sql
SELECT gtdb_species_clade_id, GTDB_species
FROM kbase.ke_pangenome.gtdb_species_clade
WHERE GTDB_species LIKE '%Escherichia_coli%'
LIMIT 5;
```

Use the resolved exact ID in downstream queries.

### Annotation query with NULL filtering

```sql
SELECT gc.gene_cluster_id, ann.COG_category, ann.EC
FROM kbase.ke_pangenome.gene_cluster gc
LEFT JOIN kbase.ke_pangenome.eggnog_mapper_annotations ann
  ON gc.gene_cluster_id = ann.query_name
WHERE gc.gtdb_species_clade_id = '<species_id>'
  AND ann.COG_category IS NOT NULL
  AND ann.COG_category != '-';
```

### Aggregate before transfer

```sql
SELECT ann.COG_category, COUNT(*) AS gene_count
FROM kbase.ke_pangenome.gene_cluster gc
JOIN kbase.ke_pangenome.eggnog_mapper_annotations ann
  ON gc.gene_cluster_id = ann.query_name
WHERE gc.gtdb_species_clade_id = '<species_id>'
GROUP BY ann.COG_category
ORDER BY gene_count DESC;
```

## Troubleshooting Notes

When a query fails or performs unexpectedly, capture reusable lessons with `pitfall-capture` into `/memories/repo/berdl-pitfalls.md`.
