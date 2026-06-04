---
name: suggest-research
description: Review repository evidence and propose high-impact next research directions for EcoSIM, emphasizing warming-nitrogen mechanisms, data readiness, and methodological feasibility.
allowed-tools: Bash, Read, Write, Edit, WebSearch, AskUserQuestion
user-invocable: true
---

# Suggest Research Skill

Identify and prioritize the next research topic using available EcoSIM-relevant data and completed analyses in this repository.

## Compatibility Modes

- Full mode: BERDL data access plus MCP literature tooling available.
- Limited mode: rely on repository-local evidence and web literature fallback.

## Usage

```text
/suggest-research
```

## Workflow

### Step 1: Inventory Available Evidence

Read and summarize key inputs:
- `derived/*.tsv` datasets
- `derived/*/summary.md` and `derived/*/metadata.yaml`
- `bervo/bervo-terms.tsv`
- `hackathon-case_study-experimental_warming_nitrogen/derived/*.tsv`
- `PLANT_TRAITS.md` and `hackathon-case_study-experimental_warming_nitrogen/plant_traits.json`

### Step 2: Extract Reusable Findings and Gaps

From summaries and metadata, capture:
- Repeated findings across ecosystems
- Common missing variables
- Methodological limitations
- Sites or ecosystems with sparse coverage

### Step 3: Assess Data Readiness

For each candidate topic, check:
- Do we have benchmark observations?
- Do we have required climate/soil/trait inputs?
- Is BERVO mapping available for required variables?
- Can EcoSIM plausibly simulate the process?

### Step 4: Optional User Constraints

If the user has not specified preferences, ask:
- Theme preference (for example: nitrification, denitrification, soil moisture)
- Effort preference (low/medium/high)
- Extension of existing analyses vs novel direction

### Step 5: Score Candidate Topics

Use this rubric:

| Criterion | Weight |
|---|---|
| Scientific novelty | High |
| Data readiness | High |
| Potential impact | High |
| Feasibility | Medium |
| Reuse of existing assets | Medium |
| Effort fit | Low |

Pick one primary recommendation plus one alternative.

### Step 6: Novelty Check

Run `literature-review` for the top candidate to confirm:
- What is already known
- What is unresolved
- Where this repository can contribute uniquely

### Step 7: Present Recommendation

Provide:
- Topic title
- Research question
- Hypotheses (H1, H0, optional H2)
- Why now
- Required datasets and variables
- Planned approach
- Expected impact
- Risks and dependencies
- Effort estimate
- Alternative topic

### Step 8: Optional Backlog Update

If user approves, append to `docs/research_ideas.md` (create if missing) with status `PROPOSED`.
Do not require BERIL-specific project scaffolding commands.

## Integration

- Reads from: repository data products and summaries
- Calls: `literature-review` for novelty checks
- Optionally writes: `docs/research_ideas.md`

## Pitfall Handling

If blocked by missing inputs or contradictory metadata, record concise notes in repo memory and surface assumptions in the recommendation.
