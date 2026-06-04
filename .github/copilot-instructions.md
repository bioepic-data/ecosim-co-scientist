# Copilot Instructions for ecosim-co-scientist

`AGENTS.md` is the source of truth for project context, priorities, constraints, and skill inventory. If this file and `AGENTS.md` differ, follow `AGENTS.md`.

## Project Scope

EcoSIM Co-Scientist is a Python-first repository for ecosystem modeling workflows around EcoSIM, with a near-term focus on experimental warming and nitrogen cycling.

## Repository Conventions

- Use `uv` for dependencies and execution (`uv run ...`).
- Prefer `just` targets for routine workflows:
  - `just --list`
  - `just test`
  - `just test-full`
- Code lives in `src/ecosim_co_scientist/`.
- Tests live in `tests/` and should use pytest functional style.
- Favor doctests for executable examples.

## Agent Skills

Skill files are under `.claude/skills/<skill-name>/SKILL.md`.

BERIL-derived skills:
- `berdl`
- `berdl-query`
- `berdl-discover`
- `berdl-minio`
- `literature-review`
- `synthesize`
- `suggest-research`

Existing EcoSIM skills:
- `era5-download`
- `netcdf-metadata`

## MCP and Access Notes

- MCP configuration is in `.claude/.mcp.json`.
- BERDL workflows generally require `KBASE_AUTH_TOKEN` and environment checks in BERDL skill docs.
- Literature workflows use `pubmed` and `paper-search` MCP servers.

## Documentation Alignment Rule

When updating docs or instructions that describe agent capabilities, update `AGENTS.md` first, then propagate the same information to:
- `README.md`
- `.github/copilot-instructions.md`
