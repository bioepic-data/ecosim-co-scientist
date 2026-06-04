# EcoSIM Co-Scientist

An AI-powered research assistant for working with [EcoSIM](https://github.com/jinyun1tang/EcoSIM), a biogeochemical modeling library that simulates ecosystem processes including carbon and nitrogen cycling, soil-plant-atmosphere interactions, microbial dynamics, and nutrient transformations.

This project aims to create an intelligent co-pilot that assists with the entire ecosystem modeling workflow: data preparation, parameter calibration, simulation execution, and results analysis.

## =� Quick Start

This project uses `uv` for dependency management:

```bash
# Install dependencies
uv sync

# Run tests
just test

# See all available commands
just --list
```

## =� Repository Structure

### Data and Analysis

- **[`hackathon-case_study-experimental_warming_nitrogen/`](hackathon-case_study-experimental_warming_nitrogen/)** - Meta-analysis of experimental warming effects on nitrogen cycling
  - [`sources/`](hackathon-case_study-experimental_warming_nitrogen/sources/) - 50 peer-reviewed papers from warming experiments across ecosystems (Arctic tundra, boreal forests, grasslands, etc.)
  - [`ecosim-inputs-netcdf/`](hackathon-case_study-experimental_warming_nitrogen/ecosim-inputs-netcdf/) - EcoSIM NetCDF input files (climate, grid, plant functional types, soil)
  - `experimental_warming_nitrogen-benchmark_data.xlsx` - Meta-analysis database with 626 nitrogen measurements from 51 warming experiments

- **[`derived/`](derived/)** - TSV exports from the Excel meta-analysis database for programmatic access:
  - `sources.tsv` - Literature sources with DOIs and citations
  - `experiment-metadata.tsv` - Geographic coordinates, ecosystem types, warming methods, temperature increases
  - `N_measurements.tsv` - 626 observations of N2O emissions, mineralization, nitrification, denitrification
  - `response_variables.tsv` - Definitions of nitrogen response variables
  - `ecosim_input-netcdf_variables.tsv` - 264 NetCDF variable specifications
  - `ecosim-plant_names-forPFTs.tsv` - 31 plant functional types for EcoSIM
  - `climate-soil_datasources.tsv` - Data source documentation

- **[`bervo/`](bervo/)** - **B**iogeochemical **E**coSIM **R**esearch **V**ariables **O**ntology
  - `bervo-terms.tsv` - 2,076 standardized terms spanning ~70 categories covering all EcoSIM variables and parameters
  - Provides controlled vocabulary, unit standardization, and semantic infrastructure for automated parameter population
  - See [`PLANT_TRAITS.md`](PLANT_TRAITS.md) for details on BERVO-trait alignment

- **[`gSSURGO_gridded/`](gSSURGO_gridded/)** - Gridded soil survey data (SSURGO)

- **[`scripts/`](scripts/)** - Utility scripts for NetCDF analysis and data processing
  - `extract_netcdf_metadata.py` - Extract variable metadata from NetCDF files to CSV
  - `test_xarray_netcdf.py`, `test_climate_data.py`, `test_pft_data.py` - NetCDF testing utilities

### Source Code

- **`src/ecosim_co_scientist/`** - Python package for EcoSIM workflows (in development)
- **`tests/`** - Test suite using pytest

## <� Current Focus: Warming Experiments & Nitrogen Cycling

The initial implementation focuses on using meta-analysis data to:

1. **Calibrate** EcoSIM parameters for nitrogen cycling under warming scenarios
2. **Validate** model predictions against 626 observations from 51 warming experiments
3. **Synthesize** understanding of nitrogen-warming interactions across ecosystems
4. **Predict** responses to future warming scenarios

### Key Datasets

- **626 nitrogen measurements** from warming experiments spanning:
  - Arctic/alpine tundra, boreal/temperate forests, grasslands, heathlands, agricultural systems
  - Temperature increases: 0.5-5�C
  - Experiment durations: 1-98 months
  - Warming methods: greenhouses, nighttime curtains, infrared heaters, heating cables

- **Climate forcing**: ERA5 reanalysis (Blodget site, 2012-2022)
- **Soil data**: Harmonized World Soil Database (HWSD), SSURGO
- **Plant traits**: Physiological parameters for 31 plant functional types

## AI Skills

This repository includes specialized agent skills for BERIL and EcoSIM workflows.

Source of truth: see the **Agent Skills (Source of Truth)** section in [`AGENTS.md`](AGENTS.md).

Current catalog: **10 skills total** (8 BERIL-derived + 2 EcoSIM).

### Complete Skill Catalog

- BERIL-derived: [`berdl`](.claude/skills/berdl/SKILL.md), [`berdl-query`](.claude/skills/berdl-query/SKILL.md), [`berdl-discover`](.claude/skills/berdl-discover/SKILL.md), [`berdl-minio`](.claude/skills/berdl-minio/SKILL.md), [`pitfall-capture`](.claude/skills/pitfall-capture/SKILL.md), [`literature-review`](.claude/skills/literature-review/SKILL.md), [`synthesize`](.claude/skills/synthesize/SKILL.md), [`suggest-research`](.claude/skills/suggest-research/SKILL.md)
- EcoSIM: [`era5-download`](.claude/skills/era5-download/SKILL.md), [`netcdf-metadata`](.claude/skills/netcdf-metadata/SKILL.md)

### BERIL-derived Skills

- [`berdl`](.claude/skills/berdl/SKILL.md): Query BERDL databases for pangenome, genome statistics, annotations, and biochemistry data.
- [`berdl-query`](.claude/skills/berdl-query/SKILL.md): Run off-cluster SQL queries against BERDL Spark compute.
- [`berdl-discover`](.claude/skills/berdl-discover/SKILL.md): Discover and document BERDL databases and schemas.
- [`berdl-minio`](.claude/skills/berdl-minio/SKILL.md): Transfer BERDL query artifacts via MinIO and manage credentials.
- [`pitfall-capture`](.claude/skills/pitfall-capture/SKILL.md): Capture reusable errors, caveats, and performance gotchas in repo memory.
- [`literature-review`](.claude/skills/literature-review/SKILL.md): Search and review biological literature with PubMed and paper-search MCP tools.
- [`synthesize`](.claude/skills/synthesize/SKILL.md): Compare analysis outputs with literature and draft findings.
- [`suggest-research`](.claude/skills/suggest-research/SKILL.md): Suggest high-impact next research directions based on prior project outputs and BERDL data.

### Existing EcoSIM Skills

- [`era5-download`](.claude/skills/era5-download/SKILL.md): Download ERA5 climate forcing data from Copernicus CDS.
- [`netcdf-metadata`](.claude/skills/netcdf-metadata/SKILL.md): Extract NetCDF variable metadata and attributes to CSV.

### Skill Prerequisites

- MCP servers are configured in [`.claude/.mcp.json`](.claude/.mcp.json): `ols-mcp`, `pubmed`, and `paper-search`.
- BERDL access generally requires `KBASE_AUTH_TOKEN` and environment setup described in BERDL skill docs.
- BERDL skills include compatibility fallbacks when helper scripts or full BERDL infrastructure are unavailable.

## =, About EcoSIM

[EcoSIM](https://github.com/jinyun1tang/EcoSIM) is a biogeochemical modeling library spun off from the ECOSYS model. It simulates:

- **Carbon & nitrogen cycling** - CO2, CH4, N2O fluxes; mineralization, nitrification, denitrification
- **Soil-plant-atmosphere interactions** - Water, energy, and gas exchange
- **Microbial dynamics** - Decomposition, enzyme kinetics, microbial competition
- **Plant growth** - Photosynthesis, allocation, phenology under varying environmental conditions

EcoSIM is written in Fortran, uses NetCDF input formats, and supports parallel simulations via MPI.

## <� Vision: The AI Co-Scientist

Long-term capabilities under development:

### 1. Literature Integration
- Extract experimental designs and measurements from papers
- Build structured databases from unstructured literature
- Track data provenance to original sources

### 2. Data Preparation
- Convert diverse formats to EcoSIM-compatible NetCDF
- Harmonize units, spatial scales, temporal resolutions
- Query climate and soil databases by coordinates

### 3. Parameter Calibration
- Optimize parameters against observational benchmarks
- Bayesian uncertainty quantification
- Multi-objective calibration across response variables

### 4. Simulation Execution
- Generate EcoSIM configuration files
- Execute on local or HPC systems
- Manage simulation ensembles

### 5. Results Analysis
- Statistical model-data comparison
- Spatiotemporal visualization
- Mechanistic interpretation

### 6. Hypothesis Generation
- Suggest experiments based on model predictions
- Design optimal sampling strategies
- Identify high-leverage measurements

### 7. Documentation
- Generate reproducible technical reports
- Create publication-quality visualizations
- Maintain audit trails of modeling decisions

## =� Technology Stack

- **Python 3.12+** with Fortran interoperability
- **Data handling**: xarray (NetCDF), pandas, openpyxl
- **Data models**: Pydantic or LinkML for type-safe structures
- **Testing**: pytest with doctests
- **Dependencies**: `uv` package manager
- **Documentation**: mkdocs

## =� Current Status

This is an early-stage project emerging from a hackathon. Immediate priorities:

1. Data loaders for warming/nitrogen meta-analysis
2. NetCDF metadata extraction tooling
3. EcoSIM input generators from experimental metadata
4. Validation frameworks for model-data comparison
5. Agent workflows for common modeling tasks

Future development will expand toward the full co-scientist vision as use cases mature.

## Documentation

- [`AGENTS.md`](AGENTS.md) - Canonical agent and workflow guidance, including the source-of-truth skill list
- [`PLANT_TRAITS.md`](PLANT_TRAITS.md) - Plant traits database and BERVO ontology details
- [`docs/agent-skills.md`](docs/agent-skills.md) - Skill prerequisites and fallback behavior matrix
- [`.claude/skills/`](.claude/skills/) - Skill definitions for BERIL and EcoSIM workflows
- [`.github/copilot-instructions.md`](.github/copilot-instructions.md) - Copilot instruction overlay aligned to `AGENTS.md`

## >� Testing

```bash
# Run unit tests, doctests, and linting
just test

# Run all tests including integration tests
just test-full
```

Tests follow pytest functional style with extensive doctests for documentation and validation.

## =� License

[License information to be added]

## =O Acknowledgments

- EcoSIM model: [Jinyun Tang](https://github.com/jinyun1tang/EcoSIM)
- Warming experiment data: 50 research papers (see [`sources/`](hackathon-case_study-experimental_warming_nitrogen/sources/))
- Climate data: ERA5 reanalysis
- Soil data: HWSD, SSURGO
