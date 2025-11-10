# Plant Traits Documentation

## Overview

This document describes the plant trait data available for EcoSIM parameterization and its relationship to the BERVO ontology. The plant traits are essential for configuring EcoSIM simulations, particularly for defining Plant Functional Types (PFTs) in NetCDF input files.

## Data Source

**File**: `hackathon-case_study-experimental_warming_nitrogen/plant_traits.json`

**Structure**: JSON array of trait objects, each containing:
- `variable`: Name of the physiological/morphological trait
- `plant_type`: Plant functional type or species
- `unit`: Measurement unit
- `low value`: Lower bound of typical range
- `high value`: Upper bound of typical range
- `Reference`: Array of literature citations and calculation notes

## Summary Statistics

- **Total trait entries**: 231
- **Unique plant types**: 13
- **Unique trait variables**: 20
- **Unique units**: 17

## Plant Functional Types Covered

The dataset includes trait data for the following plant types, ordered by number of traits:

1. **Maize (C4 Monocot)**: 20 traits
2. **C4 perennial grass**: 20 traits
3. **Alfalfa (C3 Dicot)**: 18 traits
4. **C3 needle leaf tree**: 18 traits
5. **Clover (C3 Dicot)**: 18 traits
6. **Cotton (C3 Dicot)**: 18 traits
7. **Oats (C3 Monocot)**: 18 traits
8. **Sedge grass (Monocot)**: 18 traits
9. **Soybean (C3 Dicot)**: 18 traits
10. **Winter Wheat (C3 Monocot)**: 18 traits
11. **temperate C3 grass**: 18 traits
12. **C3 annual grass**: 18 traits
13. **temperate C3 grass (Temperate oceanic climate)**: 11 traits

### Ecological Coverage

The plant types span major functional groups relevant to the warming/nitrogen experiments:
- **Agricultural crops**: Maize, wheat, oats, alfalfa, clover, cotton, soybean
- **Natural grasslands**: C3 and C4 grasses, sedges
- **Forests**: Needle leaf trees

This coverage aligns well with the experimental ecosystems in the meta-analysis (grasslands, heathlands, forests, agricultural systems).

## Trait Variables

### 1. Photosynthesis Parameters

#### Maximum Carboxylation Rate (Vcmax)
- **Variable**: `typical Maximum carboxylation rate by Rubisco at 25oC`
- **Unit**: `umol CO2 s-1 m-2 leaf area`
- **Description**: The maximum rate of CO2 fixation by Rubisco enzyme at standard temperature
- **Typical ranges**:
  - C3 plants: 50-180 µmol CO2 m⁻² s⁻¹
  - C4 plants: 40-100 µmol CO2 m⁻² s⁻¹
- **Ecological significance**: Primary determinant of photosynthetic capacity and plant productivity

#### Maximum Electron Transport Rate (Jmax)
- **Variable**: `typical Maximum electron transport rate at 25oC`
- **Unit**: `umol e- s-1 m-2 leaf area`
- **Typical ranges**:
  - C3 plants: 90-300 µmol e⁻ m⁻² s⁻¹
  - C4 plants: 150-300 µmol e⁻ m⁻² s⁻¹
- **Ecological significance**: Determines light-saturated photosynthetic rate

#### Saturated Specific Carboxylation Rate
- **Variable**: `Saturated specific carboxylation rate by Rubisco at 25oC`
- **Unit**: `umol CO2 (g rubisco)-1 s-1`
- **Description**: Catalytic efficiency of Rubisco enzyme
- **Ecological significance**: Links leaf nitrogen investment to photosynthetic capacity

#### Intercellular CO2 Ratio (Ci/Ca)
- **Variable**: `typical Intercellular-to-atmospheric CO2 concentration ratio (Ci/Ca)`
- **Unit**: `unitless`
- **Typical ranges**: 0.3-0.8 (varies by C3/C4 pathway and water stress)
- **Ecological significance**: Indicator of stomatal conductance and water use efficiency

### 2. Leaf Structural Properties

#### Specific Leaf Area (SLA)
- **Variable**: `typical Specific leaf area vs mass`
- **Unit**: `m2 gC-1`
- **Typical ranges**: 0.01-0.1 m² gC⁻¹
- **Ecological significance**: Key trait linking leaf economics spectrum to resource use strategy

#### Protein Carbon Mass
- **Variable**: `typical Protein carbon mass per unit of leaf area`
- **Unit**: `gC m-2 leaf area`
- **Typical ranges**: 2-8 gC m⁻²
- **Ecological significance**: Determines nitrogen allocation to photosynthetic machinery

#### Rubisco to Total Protein Ratio
- **Variable**: `typical Carbon mass ratio of rubisco enzyme to total leaf protein`
- **Unit**: `gC rubisco / gC protein (unitless)`
- **Typical ranges**: 0.15-0.5
- **Ecological significance**: Fraction of leaf nitrogen invested in primary carboxylase

#### Chlorophyll Content
- **Variable**: `typical Cholorophyll carbon in mesophyll`
- **Unit**: `mgC m-2 leaf area`
- **Typical ranges**: 100-600 mgC m⁻²
- **Additional for C4**: `typical Cholorophyll carbon in bundle sheath`
- **Ecological significance**: Light harvesting capacity

#### Specific Chlorophyll Activity
- **Variable**: `Specific chlorophyll activity (at light saturation)`
- **Unit**: `umol e- (gC chl)-1 s-1`
- **Typical ranges**: 400-1000 µmol e⁻ gC⁻¹ s⁻¹
- **Ecological significance**: Efficiency of light energy conversion

### 3. Canopy Structure

#### Leaf Area Index (LAI)
- **Variable**: `typical Leaf area index`
- **Unit**: `m2 m-2 (unitless)`
- **Typical ranges**: 1-8 m² m⁻²
- **Ecological significance**: Total canopy light interception capacity
- **BERVO alignment**: Strong match to BERVO:0000696 (Total leaf area)

### 4. Nitrogen Uptake Kinetics

#### Ammonium Uptake
- **Variable**: `typical Maximum NH4 uptake rate (Vmax)`
- **Unit**: `umolN h-1 (gC root)-1`
- **Typical ranges**: 0.5-3 µmol h⁻¹ gC⁻¹
- **Variable**: `typical Half saturation Km for root uptake of NH4`
- **Unit**: `uM`
- **Typical ranges**: 5-50 µM

#### Nitrate Uptake
- **Variable**: `typical Maximum NO3 uptake rate (Vmax)`
- **Unit**: `umolN h-1 (gC root)-1`
- **Typical ranges**: 0.5-3 µmol h⁻¹ gC⁻¹
- **Variable**: `typical Half saturation Km for root uptake of NO3`
- **Unit**: `uM`
- **Typical ranges**: 5-100 µM

**Ecological significance**: Critical for modeling nitrogen limitation and plant response to warming-induced changes in soil nitrogen availability (central to the warming/nitrogen meta-analysis use case).

### 5. Root Hydraulic Properties

#### Axial Resistivity
- **Variable**: `typical Axial resistivity per m root length for water uptake`
- **Unit**: `MPa h m-4`
- **Typical ranges**: 10⁷-10¹⁰ MPa h m⁻⁴
- **Ecological significance**: Controls water transport efficiency through root xylem

#### Radial Resistance
- **Variable**: `typical Radial resistance per m2 root surface area for water uptake`
- **Unit**: `MPa h m-1`
- **Typical ranges**: 10³-10⁵ MPa h m⁻¹
- **Ecological significance**: Controls water uptake from soil to root interior

### 6. Root Morphology

#### Root Branching
- **Variable**: `typical fine root branching frequency`
- **Unit**: `m-1` (branches per meter)
- **Ecological significance**: Determines soil exploration efficiency

#### Root Hairs
- **Variable**: `typical root hair frequency on fine roots`
- **Unit**: `m-1` (hairs per meter)
- **Ecological significance**: Increases surface area for nutrient and water uptake

### 7. Productivity

#### Gross Primary Production (GPP)
- **Variable**: `typical annual Gross Primary Production (GPP)`
- **Unit**: `gC m-2 yr-1`
- **Typical ranges**: 500-5000 gC m⁻² yr⁻¹
- **Ecological significance**: Total carbon fixation capacity, validation target for model output

## Alignment with BERVO Ontology

### BERVO Overview

**File**: `hackathon-case_study-experimental_warming_nitrogen/bervo/bervo-terms.tsv`

BERVO is an ontology derived from EcoSIM's internal data structures, containing **2,076 terms** organized into **70 categories**.

#### Key BERVO Categories Relevant to Plant Traits

1. **Plant trait data type**: 143 terms (from `PlantTraitDataType.txt`)
2. **Plant data rate type**: 101 terms (from `PlantDataRateType.txt`)
3. **Canopy data type**: 148 terms (from `CanopyDataType.txt`)
4. **Root data type**: 75 terms (from `RootDataType.txt`)
5. **Plant growth parameters**: 73 terms (from `GrosubPars.txt`)

**Total plant-related terms**: ~1,232 (59% of entire ontology)

### Mapping Challenges

Direct mapping between `plant_traits.json` variables and BERVO terms is **challenging** due to:

1. **Granularity mismatch**:
   - `plant_traits.json` focuses on intensive physiological parameters (Vcmax, Jmax, enzyme kinetics)
   - BERVO includes these but also extensive structural variables, state variables, and ratios

2. **Naming conventions**:
   - `plant_traits.json` uses descriptive English names
   - BERVO uses EcoSIM internal variable names (e.g., `Eco_NetRad_col`)

3. **Semantic coverage**:
   - Some `plant_traits.json` variables have no direct BERVO equivalents
   - BERVO contains many model-specific variables not in the trait database

### Successful Alignments

Based on semantic similarity analysis, these mappings have >0.5 confidence:

| plant_traits.json Variable | BERVO Term | BERVO ID | Similarity |
|----------------------------|------------|----------|------------|
| typical Leaf area index | Total leaf area | BERVO:0000696 | 0.68 |
| typical Leaf area index | Canopy leaf area | BERVO:0000692 | 0.62 |
| typical Maximum electron transport rate | Maximum leaf nitrogen to carbon ratio | BERVO:0000727 | 0.55 |
| typical Cholorophyll carbon in mesophyll | Stalk phosphorous to carbon ratio | BERVO:0000737 | 0.52 |

### Gaps and Opportunities

#### Variables in plant_traits.json NOT well-represented in BERVO:
- Specific carboxylation rates (Vcmax per unit Rubisco)
- Chlorophyll-specific electron transport rates
- Detailed nutrient uptake kinetics (Vmax, Km for NH4/NO3)

#### BERVO terms NOT in plant_traits.json:
- Phenological parameters (leafout timing, cold/heat requirements)
- Grain/seed properties (for crops)
- Allocation fractions to woody vs. fine litter
- Thermal adaptation zones
- Management-related traits (planting depth, maturity groups)

## Use Case: Completing NetCDF Files for Plant Functional Types

### Objective

Use `plant_traits.json` to populate EcoSIM NetCDF input files with scientifically-grounded parameter values for simulating warming/nitrogen experiments.

### Workflow

1. **Identify target PFTs** from experimental metadata:
   - Map experimental ecosystems to EcoSIM PFTs
   - Example: "temperate heathland" → C3 grasses + dwarf shrubs

2. **Extract trait ranges** from `plant_traits.json`:
   - Use `low value` and `high value` for parameter uncertainty
   - Prioritize traits matched to BERVO terms for correct NetCDF variable naming

3. **Populate NetCDF variables** using BERVO mappings:
   - Cross-reference BERVO `EcoSIM Variable Name` field
   - Ensure units match NetCDF specifications
   - Document provenance in metadata

4. **Handle missing traits**:
   - Use BERVO defaults from `PlantTraitDataType.txt`
   - Apply allometric relationships (e.g., Vcmax ~ leaf N)
   - Flag assumptions for sensitivity analysis

5. **Validate parameter combinations**:
   - Check physiological consistency (e.g., Jmax/Vcmax ratios)
   - Ensure values fall within BERVO-defined bounds
   - Test against observed GPP ranges

### Priority Traits for Warming/Nitrogen Experiments

Given the meta-analysis focus, these traits are **critical**:

1. **Nitrogen uptake kinetics** (Vmax and Km for NH4/NO3)
   - Directly determines plant response to warming-altered N availability
   - High uncertainty in literature

2. **Photosynthetic capacity** (Vcmax, Jmax)
   - Controls NPP response to increased N availability
   - Temperature-sensitive parameters (Q10 effects)

3. **Specific Leaf Area (SLA)**
   - Links leaf N content to photosynthetic area
   - Often shifts under warming

4. **Root morphology** (branching, root hairs)
   - Affects N foraging efficiency
   - May respond plastically to warming

5. **Leaf Area Index (LAI)**
   - Scales leaf-level processes to ecosystem
   - Observable validation target

### Example: Parameterizing C3 Grassland for Danish Heathland Site

From experiment metadata (Larsen et al. 2011):
- **Location**: Denmark (55°53'N, 11°58'E)
- **Ecosystem**: Temperate heathland (dominated by *Deschampsia* grass + dwarf shrubs)
- **Warming**: +1.5°C nighttime warming
- **Duration**: 18 months

#### Step 1: Select matching PFT
Best match: `temperate C3 grass` from `plant_traits.json`

#### Step 2: Extract relevant traits

```json
{
  "variable": "typical Maximum carboxylation rate by Rubisco at 25oC",
  "plant_type": "temperate C3 grass",
  "unit": "umol CO2 s-1 m-2 leaf area",
  "low value": 50,
  "high value": 120
}
```

#### Step 3: Map to BERVO (if available)
- Check BERVO `PlantTraitDataType.txt` for Vcmax variable
- Use BERVO variable name in NetCDF file
- If no direct match, document as custom parameter

#### Step 4: Complete NetCDF
Populate climate data from ERA5, soil from HWSD, and plant traits from JSON.

#### Step 5: Validate
Compare simulated vs. observed:
- N2O emissions (treatment: 0.031 ± 0.012 gN m⁻² yr⁻¹)
- Net N mineralization changes
- Soil moisture effects

## Data Quality and Provenance

### Strengths
- **Literature-backed**: All values include peer-reviewed references
- **Uncertainty quantified**: Low/high ranges provided
- **Diverse PFTs**: Covers major functional groups
- **Calculation transparency**: Notes on assumptions (e.g., C mass fractions)

### Limitations
- **Taxonomic specificity**: Some PFTs are broad (e.g., "C3 needle leaf tree")
- **Geographic bias**: Many values from temperate zone studies
- **Phenotypic plasticity not captured**: Fixed ranges don't represent acclimation
- **Inter-trait correlations not documented**: Traits treated independently

### Recommendations for Use

1. **Treat ranges as uncertainty bounds**, not absolute limits
2. **Prioritize local calibration** when site-specific data available
3. **Use ensemble simulations** varying traits within ranges
4. **Validate against multiple response variables** (not just one)
5. **Document all parameter choices** for reproducibility

## Integration with EcoSIM Co-Scientist Workflows

The AI agent system should:

1. **Automated trait extraction**:
   - Parse `plant_traits.json` for user-specified PFT
   - Generate summary statistics and visualizations
   - Flag traits with high uncertainty

2. **BERVO-guided NetCDF population**:
   - Use BERVO mappings to correctly name variables
   - Validate units and value ranges against BERVO constraints
   - Auto-complete interdependent parameters (e.g., calculate Jmax from Vcmax using typical ratios)

3. **Gap analysis**:
   - Identify which BERVO-required parameters are missing from `plant_traits.json`
   - Suggest literature searches or default values
   - Rank missing parameters by sensitivity to model outputs

4. **Sensitivity analysis**:
   - Vary traits within documented ranges
   - Identify high-leverage parameters for calibration
   - Suggest targeted measurements to reduce uncertainty

5. **Provenance tracking**:
   - Link each NetCDF value to source reference
   - Maintain audit trail of all assumptions
   - Enable reproducible parameter sets

## Future Enhancements

### Expanding the Trait Database

1. **Add missing PFTs**:
   - Tundra species (sedges, dwarf shrubs, mosses)
   - Wetland plants
   - Tropical species

2. **Include phenological parameters**:
   - Cold/heat requirements for leafout
   - Critical daylengths
   - Maturity schedules

3. **Add temperature response curves**:
   - Q10 values for respiration
   - Temperature optima for photosynthesis
   - Acclimation parameters

4. **Document trait correlations**:
   - Leaf economic spectrum relationships
   - Root:shoot allocation patterns
   - C:N:P stoichiometry

### Improving BERVO Alignment

1. **Manual curation**:
   - Expert-reviewed mappings for key traits
   - Resolve naming ambiguities
   - Add exact synonyms to BERVO

2. **Semantic enrichment**:
   - Link BERVO to external ontologies (PO, TO, PATO)
   - Add text definitions to more terms
   - Improve hierarchical organization

3. **Automated mapping pipeline**:
   - NLP-based similarity matching
   - Unit conversion tables
   - Validation against EcoSIM documentation

## References

All trait values are documented with references in the JSON file. Key sources include:
- Evans, J. R. (1989). Oecologia - Rubisco content relationships
- Wright et al. (2004). Nature - Global leaf economics spectrum
- Reich et al. (1997). PNAS - Root trait spectra
- Plant-specific literature cited in each trait entry

## Contact and Contribution

This documentation is part of the EcoSIM Co-Scientist project. For questions or contributions:
- See main project documentation in `AGENTS.md`
- Trait data issues: check provenance references in JSON
- BERVO questions: consult EcoSIM model documentation

---

**Last updated**: 2025-11-10
**Analysis scripts**: `analyze_traits.py`, `analyze_bervo.py`, `map_traits_to_bervo.py`
