---
name: literature-review
description: Search and review ecosystem and biogeochemical literature using MCP tools (PubMed, arXiv, bioRxiv, Google Scholar), with optional full-text reading and citation snowballing. Use when the user needs evidence, citations, methods comparison, or novelty checks for EcoSIM and warming-nitrogen hypotheses.
allowed-tools: Bash, Read, Write, WebSearch, Agent
user-invocable: true
---

# Literature Review Skill

Search, read, and synthesize literature relevant to EcoSIM modeling, warming experiments, nitrogen cycling, and related ecosystem biogeochemistry.

## Compatibility Modes

- Full mode: MCP servers available (`pubmed`, `paper-search`) for richer search and full text.
- Limited mode: WebSearch + DOI fallback with explicit reduced-coverage note.

## Prerequisites

Preferred servers are configured in `.claude/.mcp.json`:
- `pubmed` for rich biomedical search and PMC full text
- `paper-search` for arXiv, bioRxiv, medRxiv, and Google Scholar search/read

If MCP servers are unavailable, fall back to WebSearch and DOI landing pages.

## Scope

Prioritize evidence for:
- Experimental warming impacts on nitrogen processes
- Soil moisture-temperature interactions
- N2O emissions, nitrification, denitrification, mineralization
- EcoSIM-relevant forcing/parameterization methods
- Ecosystem-specific effects (tundra, forest, grassland, agricultural)

## Review Tiers

| Tier | Papers | Full text | Citation expansion | When to use |
|---|---|---|---|---|
| Quick scan | 5-10 | No | No | Fast orientation |
| Standard review | 20-30 | Top 10 | Yes | Default for project work |
| Deep review | 50+ | Top 20 | Yes | Comprehensive synthesis |

Default: `quick` for ad-hoc questions, `standard` for project work, `deep` only when explicitly requested.

## Workflow

### Step 1: Clarify the Question

Capture:
- Topic and hypothesis
- Organisms/ecosystems
- Time horizon (recent vs historical)
- Whether methods comparison is required

### Step 2: Build Query Set

Construct 3 query families:
- Core process query (for example: warming + nitrification)
- Ecosystem query (for example: tundra + soil nitrogen)
- Methods query (for example: incubation, isotope tracing, flux chamber)

### Step 3: Discover, Deduplicate, Rank

Search across PubMed, bioRxiv, arXiv, and Google Scholar.
Deduplicate by DOI/PMID.
Rank by EcoSIM relevance:
- HIGH: directly measures N-cycling or climate-soil controls used in EcoSIM workflows
- MEDIUM: adjacent mechanisms or methods transferable to EcoSIM
- LOW: tangential background

### Step 4: Optional Deep Reading

For standard/deep tiers, read top papers in full text where available.
Extract:
- Study design and sample sizes
- Quantitative outcomes (effect sizes, p-values, uncertainty)
- Limitations and caveats
- Variables that map to EcoSIM or BERVO terms

### Step 5: Summarize

Produce:
- Thematic findings
- Methods comparison table
- Key quantitative results table
- Evidence quality notes
- Knowledge gaps and contested findings

Use this structure:

```markdown
## Literature Review: <topic>

Review depth: <quick|standard|deep>
Papers found: <N>
Full text read: <N>
Sources searched: <list>

### Summary
<2-3 sentence synthesis>

### Key Findings by Theme
- <Author Year>: <finding> (DOI/PMID)

### Methods Comparison
| Study | Ecosystem | Method | Sample size | Key metric |
|---|---|---|---|---|

### Key Quantitative Results
| Finding | Value | Study | Evidence quality |
|---|---|---|---|

### Gaps in Current Knowledge
- <gap>

### Relevance to EcoSIM
- <variables, parameters, forcing constraints, benchmark opportunities>
```

### Step 6: Store References

If a project location is known, append references to a repo-local file such as:
- `docs/references/<topic>.md` or
- `derived/<study-id>/summary.md` (when extending an existing study packet)

Do not require a BERIL `projects/{id}` layout.

## Integration

- Called by: `suggest-research`, `synthesize`
- Inputs from: `derived/*.tsv`, study summaries, user hypotheses
- Outputs: a citation-backed review and optional reference file updates

## Fallback

If MCP is unavailable:
- Use WebSearch with source constraints (`site:pubmed.ncbi.nlm.nih.gov`, DOI URLs)
- Note reduced coverage and lack of robust full-text retrieval
