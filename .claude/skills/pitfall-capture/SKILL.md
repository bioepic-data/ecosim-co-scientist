---
name: pitfall-capture
description: Capture non-obvious errors, data caveats, and performance gotchas discovered during analysis into repository memory for reuse.
allowed-tools: Read, Write
user-invocable: true
---

# Pitfall Capture Skill

Use this skill when a task reveals a non-trivial pitfall that future work should not rediscover.

## What to Capture

- Reproducible error patterns
- Access/permission caveats
- Query anti-patterns and performance traps
- Ambiguous variable semantics or unit gotchas
- Missing-data behaviors that affect interpretation

## What Not to Capture

- Obvious typos
- One-off transient outages without reusable lesson
- Sensitive secrets or credentials

## Storage Location

Default to repo memory:
- `/memories/repo/berdl-pitfalls.md`

If the file does not exist, create it.

## Entry Format

```markdown
## <short title>
- Date: YYYY-MM-DD
- Context: <task/skill>
- Symptom: <what failed or surprised>
- Cause: <root cause if known>
- Safe pattern: <what to do instead>
- Example: <optional command/query snippet>
```

Keep entries short, concrete, and reusable.
