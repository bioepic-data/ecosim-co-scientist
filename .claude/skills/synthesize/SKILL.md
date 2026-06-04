---
name: synthesize
description: Read analysis outputs, compare against literature, and draft findings for EcoSIM-focused reports in this repository.
allowed-tools: Bash, Read, Write, Edit, WebSearch, AskUserQuestion
user-invocable: true
---

# Synthesis Skill

Synthesize analysis outputs into a report that connects numerical results, literature context, and implications for EcoSIM calibration and validation.

## Usage

```text
/synthesize [topic-or-folder]
```

If no argument is provided, infer scope from the current directory and recent modified analysis artifacts.

## Workflow

### Step 1: Gather Context

Collect:
- Analysis outputs under `derived/`, `output/`, `netcdf/`, and relevant notebooks
- Study summaries (`derived/*/summary.md`)
- Metadata (`derived/*/metadata.yaml`)
- Existing benchmark tables in `hackathon-case_study-experimental_warming_nitrogen/derived/`

### Step 2: Extract Results

From CSV/TSV/notebook outputs, summarize:
- Main effect sizes and uncertainty
- Directional results by ecosystem/site
- Statistical significance or confidence ranges
- Any anomalies or missingness patterns

### Step 3: Validate Interpretation with User

Present a draft interpretation and ask for corrections before finalizing report text.

### Step 4: Literature Cross-Reference

Call `literature-review` for supporting/contradictory evidence and methodological context.

### Step 5: Draft Report

Write or update a report at one of:
- `docs/reports/<topic>.md` (preferred)
- `output/reports/<topic>.md`
- `derived/<study-id>/summary.md` (when extending an existing packet)

Suggested structure:

```markdown
# Report: <title>

## Key Findings
- <finding with numbers>

## Results
- <tables/figures and interpretation>

## Literature Context
- <agreement, disagreement, novelty>

## Limitations
- <coverage, assumptions, confounders>

## Relevance to EcoSIM
- <parameterization, forcing, validation implications>

## Next Steps
1. <next analysis>
2. <data needed>
3. <model experiment>

## References
- <citations>
```

### Step 6: Update Pointers

If creating a new report, add a short link/reference in `README.md` or the relevant `derived/*/summary.md`.

## Integration

- Reads: repo-local analysis artifacts and metadata
- Calls: `literature-review`
- Produces: report markdown for decision-making and follow-on modeling

## Pitfall Handling

Document major surprises, constraints, and assumptions explicitly in the report. Prefer transparent caveats over silent omission.
