# Cross-Database Query Patterns

Patterns for combining BERDL datasets and linking outputs to external resources.

## Typical Linkage Routes

- Pangenome annotations (`EC`, `KEGG_*`) -> biochemistry reaction catalogs
- Genome metadata -> external NCBI accessions
- Species clades -> taxonomy-driven grouping and joins

## Pattern 1: Pangenome to Biochemistry via EC

```sql
SELECT gc.gene_cluster_id, ann.EC
FROM kbase.ke_pangenome.gene_cluster gc
JOIN kbase.ke_pangenome.eggnog_mapper_annotations ann
  ON gc.gene_cluster_id = ann.query_name
WHERE gc.gtdb_species_clade_id = '<species_id>'
  AND ann.EC IS NOT NULL
  AND ann.EC != '-';
```

Then use EC-aware matching against the target biochemistry table.

## Pattern 2: Pathway-centric summaries

```sql
SELECT ann.KEGG_Pathway, COUNT(*) AS n
FROM kbase.ke_pangenome.gene_cluster gc
JOIN kbase.ke_pangenome.eggnog_mapper_annotations ann
  ON gc.gene_cluster_id = ann.query_name
WHERE gc.gtdb_species_clade_id = '<species_id>'
  AND ann.KEGG_Pathway IS NOT NULL
  AND ann.KEGG_Pathway != '-'
GROUP BY ann.KEGG_Pathway
ORDER BY n DESC;
```

## Pattern 3: Join discipline

- Filter large tables before multi-way joins
- Start from the smallest constrained relation
- Validate key compatibility (`string` vs `numeric`, canonical IDs)
- Keep exploratory joins bounded and paginated

## Output Strategy

- Keep exploratory outputs small and inspectable
- For larger outputs, write partitioned results and post-process downstream

## Pitfalls

Cross-database joins are a common source of type and key mismatches. Record reusable fixes using `pitfall-capture` in `/memories/repo/berdl-pitfalls.md`.
