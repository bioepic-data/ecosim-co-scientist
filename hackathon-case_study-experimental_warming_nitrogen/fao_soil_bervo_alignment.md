# FAO Soil Example Variables - BERVO Alignment Analysis

## Overview

This document provides an analysis of the FAO soil mapping unit variables from `fao_soil_example.csv` and their alignment with terms in the Biogeochemical EcoSIM Research Variables Ontology (BERVO).

## Data Source

**File**: `fao_soil_example.csv`
**Description**: FAO soil mapping unit data for two soil units:
- Dominant: Akroskeletic Acrisol (WRB 2022)
- Secondary: Cambic Umbrisols (WRB 2022)

**Data Structure**: Soil properties measured at 7 depth layers (0-5, 5-15, 15-30, 30-60, 60-100, 100-150, 150-200 cm)

## Variable Alignment Analysis

### 1. Soil Organic Carbon (SOC)

**FAO Variable**: `SOC (g per kg soil)`
**BERVO Alignment**: 
- **BERVO:0000141** - Cation exchange capacity of soil organic carbon
  - *Definition*: The capacity of soil organic carbon to hold and exchange positively charged ions including calcium, magnesium, potassium, and sodium through functional groups on organic matter surfaces.
  - *Units*: eqv (gC)^-1
  - *Category*: Constants for specific chemical reactions
  - *Note*: This BERVO term refers to CEC properties of SOC rather than SOC content itself

**Gap Identified**: No direct BERVO term for soil organic carbon content/concentration exists in the current ontology.

**Recommended BERVO Extension**: A new term should be added for "Soil organic carbon content" or "Soil organic carbon concentration" with units g/kg or %.

### 2. Total Nitrogen

**FAO Variable**: `Total N (g per kg soil)`
**BERVO Alignment**: 
- **BERVO:0000324** - Total soil nitrogen
  - *Definition*: The cumulative mass of nitrogen gas stored in soil air spaces across all soil layers in a modeling domain.
  - *Units*: g d-2
  - *Category*: Sum data type
  - *Note*: This refers to nitrogen gas, not total soil nitrogen content

**Gap Identified**: No direct BERVO term for total soil nitrogen content exists.

**Recommended BERVO Extension**: A new term should be added for "Total soil nitrogen content" with units g/kg or mg/kg.

### 3. pH

**FAO Variable**: `pH`
**BERVO Alignment**: 
- **BERVO:0000025** - Equilibrium constant for H2O=H(+)+OH(-)
  - *Definition*: The equilibrium constant for the autoionization of water into hydrogen and hydroxide ions, representing the fundamental acid-base chemistry of aqueous systems. This constant governs hydrogen ion activity and solution pH in terrestrial and aquatic environments.
  - *Category*: Constants for specific chemical reactions
  - *Note*: This is related to pH through hydrogen ion activity but is not soil pH itself

**Gap Identified**: No direct BERVO term for soil pH exists.

**Recommended BERVO Extension**: A new term should be added for "Soil pH" or "Soil hydrogen ion activity".

### 4. Bulk Density

**FAO Variable**: `Bulk density (g per cm³)`
**BERVO Alignment**: **No matching terms found**

**Gap Identified**: No BERVO term for soil bulk density exists.

**Recommended BERVO Extension**: A new term should be added for "Soil bulk density" with units g/cm³ or kg/m³.

### 5. Clay, Silt, Sand Content

**FAO Variables**: 
- `USDA clay (%)`
- `USDA silt (%)`
- `USDA sand (%)`

**BERVO Alignment**: **No matching terms found**

**Gap Identified**: No BERVO terms for soil texture fractions exist.

**Recommended BERVO Extension**: New terms should be added for:
- "Soil clay fraction" (%)
- "Soil silt fraction" (%)
- "Soil sand fraction" (%)

### 6. Cation Exchange Capacity (CEC)

**FAO Variable**: `CEC (cmol+ per kg soil)`
**BERVO Alignment**: 
- **BERVO:0000141** - Cation exchange capacity of soil organic carbon
  - *Definition*: The capacity of soil organic carbon to hold and exchange positively charged ions including calcium, magnesium, potassium, and sodium through functional groups on organic matter surfaces.
  - *Units*: eqv (gC)^-1
  - *Category*: Constants for specific chemical reactions
  - *Note*: This is specific to organic carbon CEC, not total soil CEC

- **BERVO:0000036** - Equilibrium constant for X-OH1=X-O(-)+H(+)
  - *Definition*: The equilibrium constant for the deprotonation of neutral surface hydroxyl groups to negatively charged surface groups on mineral and organic surfaces. This reaction determines the development of negative surface charge at higher pH values and controls cation exchange capacity and nutrient retention in soils.
  - *Note*: Related to CEC mechanisms but not CEC measurement itself

**Partial Alignment**: BERVO has mechanistic terms related to CEC but no direct measurement term.

**Recommended BERVO Extension**: A new term should be added for "Soil cation exchange capacity" with units cmol+/kg or meq/100g.

### 7. Base Saturation

**FAO Variable**: `Base saturation (%)`
**BERVO Alignment**: **No matching terms found**

**Gap Identified**: No BERVO term for base saturation exists.

**Recommended BERVO Extension**: A new term should be added for "Soil base saturation" with units %.

### 8. Aluminum Saturation

**FAO Variable**: `Al sat (%)`
**BERVO Alignment**: Multiple aluminum-related equilibrium constants exist in BERVO:
- **BERVO:0000026** - Equilibrium constant for AlOH3(s)=Al(3+)+3OH(-)
- **BERVO:0000042** - Equilibrium constant for AlOH(2+)=Al(3+)+OH(-)
- **BERVO:0000043** - Equilibrium constant for Al(OH)2(+)=AlOH(2+)+OH(-)
- And others (BERVO:0000044, 0000045, 0000046)

**Note**: These are all equilibrium constants for aluminum chemical reactions, not aluminum saturation measurements.

**Gap Identified**: No direct BERVO term for aluminum saturation exists.

**Recommended BERVO Extension**: A new term should be added for "Soil aluminum saturation" with units %.

### 9. Soil Texture Classification

**FAO Variable**: `Soil texture` (Clay loam)
**BERVO Alignment**: **No matching terms found**

**Gap Identified**: No BERVO terms for soil texture classes exist.

**Recommended BERVO Extension**: New terms should be added for various soil texture classes (clay, clay loam, sandy loam, etc.).

## Summary of Gaps and Recommendations

### Existing BERVO Categories Relevant to Soil Properties

BERVO contains several categories that could accommodate soil physical and chemical properties:

1. **Soil biogeochemical data type** - Contains concentration and content terms for nutrients
2. **Soil and water data type** - Could be expanded for physical properties  
3. **Constants for specific chemical reactions** - Contains soil chemistry equilibrium constants

### Missing Soil Physical/Chemical Properties in BERVO

The following fundamental soil properties from the FAO dataset are not represented in BERVO:

1. **Soil Physical Properties**:
   - Soil bulk density
   - Clay fraction/content
   - Silt fraction/content  
   - Sand fraction/content
   - Soil texture classification

2. **Soil Chemical Properties**:
   - Soil pH
   - Soil organic carbon content
   - Total soil nitrogen content
   - Soil cation exchange capacity (total)
   - Base saturation
   - Aluminum saturation

### Recommended BERVO Extensions

To better support soil data like the FAO soil mapping units, BERVO should be extended with new categories and terms:

#### New Category: "Soil Physical Data Type"
- Soil bulk density (g/cm³)
- Clay fraction (%)
- Silt fraction (%)
- Sand fraction (%)
- Soil texture class (categorical)

#### New Category: "Soil Chemical Data Type"  
- Soil pH (pH units)
- Soil organic carbon content (g/kg, %)
- Total soil nitrogen content (g/kg, mg/kg)
- Soil cation exchange capacity (cmol+/kg)
- Base saturation (%)
- Aluminum saturation (%)

#### Integration with Existing BERVO Structure

These new terms should follow BERVO's existing patterns:
- Use consistent ID numbering (BERVO:XXXXXXX)
- Include standardized fields: Definition, Units, Category, EcoSIM Variable Name (if applicable)
- Link to related existing terms where appropriate
- Follow the measurement context structure (measured_in, measurement_of, contexts)

## Conclusion

While BERVO contains extensive biogeochemical process variables and chemical equilibrium constants, it currently lacks fundamental soil physical and chemical property measurements that are standard in soil surveys and databases. The FAO soil example reveals significant gaps that should be addressed to make BERVO a comprehensive soil science ontology suitable for EcoSIM parameterization and broader soil modeling applications.

The alignment analysis identifies 9 distinct soil property types where only partial or no BERVO terms exist, highlighting the need for systematic expansion of the ontology to include standard soil survey measurements.