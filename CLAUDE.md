# CLAUDE.md for ecosim-co-scientist

This repository uses `AGENTS.md` as the canonical source of agent guidance.

If any instruction in this file differs from `AGENTS.md`, follow `AGENTS.md`.

## Quick Reference

- Project context, data assets, and workflow goals: see `AGENTS.md`.
- Agent skill inventory and descriptions: see the **Agent Skills (Source of Truth)** section in `AGENTS.md`.
- Skill files live in `.claude/skills/`.
- MCP configuration lives in `.claude/.mcp.json`.

## Development Rules

- Use `uv` for dependency management and execution.
- Prefer `just` targets (`just test`, `just test-full`) for validation.
- Use pytest functional style and doctests for executable examples.
