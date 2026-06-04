# Agent Skills Index

This index summarizes active skills, prerequisites, and fallback behavior for ecosim-co-scientist.

Source of truth for skill intent remains `AGENTS.md`.

| Skill | Primary Use | Key Prerequisites | Fallback Behavior |
|---|---|---|---|
| `berdl` | Query BERDL datasets | BERDL session/auth | Run equivalent Spark SQL in active environment where possible |
| `berdl-query` | Off-cluster BERDL SQL | `KBASE_AUTH_TOKEN`, proxy/session | Direct Spark SQL/DataFrame export if helper scripts are missing |
| `berdl-discover` | BERDL schema discovery | BERDL helper utilities | Manual `DESCRIBE`/helper discovery in active environment |
| `berdl-minio` | BERDL MinIO transfers | `mc`, BERDL access or MinIO keys | Direct `mc alias set` + env credentials |
| `pitfall-capture` | Record reusable pitfalls | Repo memory access | Capture concise notes in report/docs if memory tooling unavailable |
| `literature-review` | Evidence and citation synthesis | `pubmed` and `paper-search` MCP | WebSearch/DOI fallback with reduced-coverage note |
| `suggest-research` | Propose next studies | Repo data summaries; literature review | Use local evidence only with explicit uncertainty |
| `synthesize` | Draft findings reports | Local analysis outputs | Local-only synthesis and caveat missing literature context |
| `era5-download` | Download ERA5 forcing data | CDS credentials, `cdsapi` | Defer to manual CDS workflow if auth unavailable |
| `netcdf-metadata` | Extract NetCDF metadata | `xarray` stack | Limited extraction from available tools when conversion fails |

## Notes

- MCP configuration: `.claude/.mcp.json`
- Skill files: `.claude/skills/<skill-name>/SKILL.md`
- BERDL-specific workflows should never block EcoSIM-only workflows; use fallback modes when infrastructure is unavailable.
