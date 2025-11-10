# AGENTS.md for ecosim-co-scientist

## Project Overview

The **EcoSIM Co-Scientist** is an AI-powered agent system designed to assist researchers in working with EcoSIM, a biogeochemical modeling library for simulating ecosystem processes. This project aims to create an intelligent co-pilot that can help with the entire workflow of ecosystem modeling, from data preparation and parameter calibration to simulation execution and results analysis.

### What is EcoSIM?

[EcoSIM](https://github.com/jinyun1tang/EcoSIM) is a biogeochemical modeling library spun off from the ECOSYS model. It simulates complex ecosystem biogeochemical processes including:
- Carbon and nitrogen cycling
- Soil-plant-atmosphere interactions
- Microbial dynamics and decomposition
- Nutrient transformations (mineralization, nitrification, denitrification)
- Plant growth and productivity under varying environmental conditions

EcoSIM is written primarily in Fortran, uses NetCDF input formats, and can run parallel simulations via MPI.

## Hackathon Case Study: Experimental Warming and Nitrogen Response

The initial implementation focuses on a meta-analysis of experimental warming effects on nitrogen cycling in various ecosystems.

### Data Assets

Located in `hackathon-case_study-experimental_warming_nitrogen/`:

1. **Literature Sources** (`sources/`): 50 peer-reviewed papers examining warming experiments across diverse ecosystems:
   - Arctic and alpine tundra
   - Boreal and temperate forests
   - Grasslands, heathlands, and meadows
   - Agricultural systems

2. **Meta-Analysis Database**:
   - **Original**: `experimental_warming_nitrogen-benchmark_data.xlsx` (7 sheets)
   - **TSV exports**: `derived/*.tsv` (7 files, one per sheet for easier programmatic access):
     - `sources.tsv` (49 rows): Literature sources with DOIs and citations
     - `experiment-metadata.tsv` (51 rows): Geographic coordinates, ecosystem types, warming methods (greenhouses, nighttime curtains, heating cables), temperature increases (0.5-5°C), durations (1-98 months)
     - `N_measurements.tsv` (626 rows): N2O emissions, gross/net mineralization, nitrification, denitrification, soil moisture observations
     - `response_variables.tsv` (14 rows): Definitions of nitrogen response variables
     - `ecosim_input-netcdf_variables.tsv` (264 rows): NetCDF variable specifications for climate, soil, and vegetation data
     - `ecosim-plant_names-forPFTs.tsv` (31 rows): Plant functional types for EcoSIM parameterization
     - `climate-soil_datasources.tsv` (2 rows): Data source documentation

3. **Plant Traits Database** (`plant_traits.json`):
   - Physiological parameters for various plant types (e.g., Alfalfa, barley, broadleaf trees)
   - Specific leaf area, protein content, Rubisco enzyme ratios
   - Chlorophyll concentrations, maximum carboxylation rates (Vcmax), electron transport rates (Jmax)
   - Root hydraulic properties, gross primary production estimates

4. **BERVO Ontology** (`bervo/bervo-terms.tsv`):
   - **B**iogeochemical **E**coSIM **R**esearch **V**ariables **O**ntology
   - **2,076 terms** spanning ~70 categories covering all EcoSIM variables and parameters
   - Each term includes: unique ID (e.g., BERVO:0000001), label, definition, units, EcoSIM variable names, source file
   - **Major categories**:
     - Canopy data type (148 terms)
     - Plant trait data type (143 terms)
     - Constants for chemical reactions (125 terms)
     - Soil biogeochemical data type (115 terms)
     - Plant data rate type (101 terms)
     - Climate force data type (101 terms)
     - Soil and water data type (90 terms)
     - Root data type (75 terms)
     - Microbial parameters (55 terms)
     - And 60+ additional categories
   - **Key functions**:
     - Controlled vocabulary for EcoSIM modeling
     - Maps human-readable variable descriptions to EcoSIM internal variable names
     - Standardizes units and defines valid ranges
     - Links model variables to NetCDF file specifications
     - Provides semantic infrastructure for automated parameter population
   - **Curation status**: Terms include flags for group curation and definition curation, with definitions from AI-assisted sources, manual curation, and model documentation
   - See `PLANT_TRAITS.md` for details on BERVO-trait alignment

5. **EcoSIM Input Files** (`ecosim-inputs-netcdf/`):
   - Climate data (Blodget site, 2012-2022)
   - Grid specifications
   - Plant functional type parameters
   - Soil management configurations

6. **Data Sources**:
   - Climate: ERA5 reanalysis
   - Soil: Harmonized World Soil Database (HWSD), SSURGO

### Scientific Goals

1. **Calibration**: Use meta-analysis data to calibrate EcoSIM parameters for nitrogen cycling under warming scenarios
2. **Validation**: Compare EcoSIM predictions against observed nitrogen responses across ecosystems
3. **Synthesis**: Identify key mechanisms controlling nitrogen-warming interactions
4. **Prediction**: Generate projections for future warming scenarios

## Vision: The EcoSIM Co-Scientist

The long-term goal is to develop an agentic AI system that serves as a research collaborator for ecosystem modeling. Key capabilities:

### 1. Literature Integration and Knowledge Synthesis
- Automatically extract experimental designs, measurements, and environmental conditions from scientific papers
- Build structured databases from unstructured literature
- Identify knowledge gaps and suggest experiments to fill them
- Track provenance of all data back to original sources

### 2. Data Preparation and Harmonization
- Convert diverse data formats to EcoSIM-compatible NetCDF inputs
- Harmonize units, spatial scales, and temporal resolutions
- Access and process climate data (ERA5, gridded weather)
- Query soil databases (HWSD, SSURGO) based on coordinates
- Handle missing data intelligently with documented assumptions

### 3. Parameter Calibration and Uncertainty Quantification
- Automated parameter optimization against observational benchmarks
- Bayesian inference for parameter uncertainty
- Sensitivity analysis to identify influential parameters
- Multi-objective calibration balancing different response variables

### 4. Simulation Execution and Management
- Generate appropriate configuration files for EcoSIM runs
- Execute simulations locally or on HPC systems
- Monitor long-running jobs and handle failures gracefully
- Manage simulation ensembles for uncertainty propagation

### 5. Results Analysis and Interpretation
- Statistical comparison of simulations vs. observations
- Visualization of spatiotemporal patterns
- Mechanistic interpretation of model behaviors
- Identification of model-data mismatches requiring investigation

### 6. Hypothesis Generation and Experimental Design
- Suggest new experiments based on model predictions
- Design optimal sampling strategies
- Identify high-leverage measurements for reducing uncertainty
- Generate testable hypotheses about ecosystem processes

### 7. Communication and Documentation
- Generate technical reports with reproducible workflows
- Create visualizations for publications and presentations
- Maintain audit trails of all modeling decisions
- Produce documentation suitable for both experts and non-specialists

## Technical Architecture

### Agent Framework
- **Agentic AI**: Autonomous task planning and execution using LLM-based reasoning
- **Model Context Protocol (MCP)**: Integration with external tools and data sources
- **Workflow Orchestration**: Multi-step scientific workflows with error handling and checkpointing

### Core Components
- **Data Manager**: ETL pipelines for scientific data
- **EcoSIM Interface**: Python wrappers for Fortran simulation engine
- **Calibration Engine**: Optimization and uncertainty quantification
- **Analysis Toolkit**: Statistical methods and visualization
- **Knowledge Base**: Structured storage of literature, experiments, and model runs

### Technology Stack
- **Language**: Python 3.12+ (with Fortran interoperability for EcoSIM)
- **Data Models**: Pydantic or LinkML for type-safe structured data
- **Testing**: pytest with extensive doctests
- **Dependencies**: Managed via `uv`
- **Documentation**: mkdocs
- **Data Formats**: NetCDF (xarray), JSON, Excel (openpyxl)

## Current Status

This is an early-stage project emerging from a hackathon. The immediate focus is:

1. Building data loaders for the warming/nitrogen meta-analysis
2. Creating EcoSIM input generators from experimental metadata
3. Establishing validation frameworks comparing simulations to observations
4. Developing initial agent workflows for common tasks

Future development will expand to the full co-scientist vision as use cases mature.

## Repo management

This repo uses `uv` for managing dependencies. Never use commands like `pip` to add or manage dependencies.
`uv run` is the best way to run things, unless you are using `justfile` or `makefile` target

`mkdocs` is used for documentation.## This is a Python repository

Layout:

 * `src/ecosim_co_scientist/` - Code goes here
 * `docs` - mkdocs docs
 * `mkdocs.yml` - index of docs
 * `tests/input` - example files

Building and testing:

* `just --list` to see all commands
* `just test` performs unit tests, doctests, ruff/liniting
* `just test-full` as above plus integration tests

You can run the underlying commands (with `uv run ...`) but in general justfile targets should be favored.

Best practice:

* Use doctests liberally - these serve as both explanatory examples for humans and as unit tests
* For longer examples, write pytest tests
* always write pytest functional style rather than unittest OO style
* use modern pytest idioms, including `@pytest.mark.parametrize` to test for combinations of inputs
* NEVER write mock tests unless requested. I need to rely on tests to know if something breaks
* For tests that have external dependencies, you can do `@pytest.mark.integration`
* Do not "fix" issues by changing or weakening test conditions. Try harder, or ask questions if a test fails.
* Avoid try/except blocks, these can mask bugs
* Fail fast is a good principle
* Follow the DRY principle
* Avoid repeating chunks of code, but also avoid premature over-abstraction
* Pydantic or LinkML is favored for data objects
* For state in engine-style OO classes, dataclasses is favored
* Declarative principles are favored
* Always use type hints, always document methods and classes