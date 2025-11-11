# HWSD2 Data Schema

This directory contains schema definitions and data from the FAO Harmonized World Soil Database (HWSD) version 2.0.

## Files

### Schema Definitions

- **`hwsd2_duckdb_schema.sql`** - DuckDB database schema with all table definitions, indexes, and data loading commands
- **`hwsd2_schema.yaml`** - LinkML data dictionary with detailed column definitions, units, and enumerations

### Data Files

- **`HWSD2_csv/`** - Directory containing CSV exports from the HWSD2 database:
  - `HWSD2_LAYERS.csv` (408,836 rows) - Detailed soil layer properties
  - `HWSD2_SMU.csv` (29,539 rows) - Soil Mapping Unit summary data
  - `D_*.csv` (18 files) - Domain/lookup tables for codes and classifications
  - `WRB_*.csv` (3 files) - World Reference Base classification tables
  - `*_METADATA.csv` (2 files) - Column documentation

## Database Structure

### Main Tables

#### HWSD2_LAYERS
The most detailed table containing physical and chemical properties for each soil layer.

**Key columns:**
- **Identifiers**: `ID`, `HWSD2_SMU_ID`, `WISE30s_SMU_ID`, `HWSD1_SMU_ID`
- **Layer info**: `LAYER` (D1-D7), `TOPDEP`, `BOTDEP` (depth in cm)
- **Physical properties**:
  - Texture: `SAND`, `SILT`, `CLAY` (% weight)
  - `COARSE` (% volume), `BULK` (g/cm³)
  - `TEXTURE_USDA`, `TEXTURE_SOTER`
- **Chemical properties**:
  - Carbon/Nitrogen: `ORG_CARBON` (%), `TOTAL_N` (g/kg), `CN_RATIO`
  - `PH_WATER`
  - Cation exchange: `CEC_SOIL`, `CEC_CLAY`, `CEC_EFF`, `TEB`
  - Saturation: `BSAT`, `ALUM_SAT`, `ESP` (%)
  - Other: `TCARBON_EQ` (CaCO₃), `GYPSUM`, `ELEC_COND`
- **Classifications**: `WRB4`, `WRB2`, `FAO90`, `KOPPEN`
- **Water/roots**: `DRAINAGE`, `AWC`, `ROOT_DEPTH`, `SWR`

#### HWSD2_SMU
Soil Mapping Units with summary-level characteristics.

**Key columns:**
- **Identifiers**: `ID`, `HWSD2_SMU_ID`, `WISE30s_SMU_ID`, `HWSD1_SMU_ID`
- **Classifications**: `WRB4`, `WRB_PHASES`, `WRB2`, `FAO90`, `KOPPEN`
- **Physical**: `TEXTURE_USDA`, `BULK_DENSITY`, `REF_BULK_DENSITY`
- **Water/roots**: `DRAINAGE`, `ROOT_DEPTH`, `AWC` (mm/m)
- **Metadata**: `COVERAGE`, `SHARE` (%), `PHASE1`, `PHASE2`

### Domain Tables (Lookup Tables)

These tables define the meaning of codes used in the main tables:

- **D_ADD_PROP** - Additional properties (Gelic, Vertic)
- **D_AWC** - Available water capacity codes
- **D_COVERAGE** - Data sources (ESDB, CHINA, SOTWIS, etc.)
- **D_DRAINAGE** - Drainage classes (E=Excessively, W=Well, P=Poorly, etc.)
- **D_FAO90** - FAO 1990 soil classification
- **D_IL** - Impermeable layer depth codes
- **D_KOPPEN** - Köppen-Geiger climate zones
- **D_PHASE** - Soil phases (Stony, Lithic, Petric, etc.)
- **D_ROOTS** - Obstacle to roots depth codes
- **D_ROOT_DEPTH** - Root depth categories
- **D_SWR** - Soil water regime codes
- **D_TEXTURE**, **D_TEXTURE_SOTER**, **D_TEXTURE_USDA** - Texture classifications
- **D_WRB2**, **D_WRB4**, **D_WRB_PHASES** - World Reference Base classifications

## Usage

### Loading into DuckDB

```bash
# Start DuckDB
duckdb hwsd2.db

# Load the schema and data
.read hwsd2_duckdb_schema.sql

# Query example: Get soil properties for a specific location
SELECT
    l.HWSD2_SMU_ID,
    l.LAYER,
    l.TOPDEP,
    l.BOTDEP,
    l.SAND,
    l.SILT,
    l.CLAY,
    l.ORG_CARBON,
    l.PH_WATER,
    l.BULK,
    d.VALUE as DRAINAGE_CLASS
FROM HWSD2_LAYERS l
LEFT JOIN D_DRAINAGE d ON l.DRAINAGE = d.CODE
WHERE l.HWSD2_SMU_ID = 1666
ORDER BY l.TOPDEP;

# Query example: Get summary statistics by soil type
SELECT
    s.WRB2,
    COUNT(*) as count,
    AVG(s.BULK_DENSITY) as avg_bulk_density,
    AVG(s.AWC) as avg_awc,
    AVG(s.ROOT_DEPTH) as avg_root_depth
FROM HWSD2_SMU s
GROUP BY s.WRB2
ORDER BY count DESC;
```

### Using with Python

```python
import duckdb

# Connect to the database
conn = duckdb.connect('hwsd2.db')

# Query soil layers for a specific mapping unit
result = conn.execute("""
    SELECT
        LAYER, TOPDEP, BOTDEP,
        SAND, SILT, CLAY,
        ORG_CARBON, PH_WATER, BULK
    FROM HWSD2_LAYERS
    WHERE HWSD2_SMU_ID = ?
    ORDER BY TOPDEP
""", [1666]).fetchdf()

print(result)

# Get soil classification with drainage info
result = conn.execute("""
    SELECT
        s.HWSD2_SMU_ID,
        s.WRB4,
        w4.VALUE as WRB4_NAME,
        d.VALUE as DRAINAGE_CLASS,
        s.BULK_DENSITY,
        s.AWC
    FROM HWSD2_SMU s
    LEFT JOIN D_WRB4 w4 ON s.WRB4 = w4.CODE
    LEFT JOIN D_DRAINAGE d ON s.DRAINAGE = d.CODE
    LIMIT 10
""").fetchdf()

print(result)
```

### Using LinkML Schema

The LinkML schema can be used for:

1. **Validation**: Ensure data conforms to expected types and ranges
2. **Documentation**: Generate data dictionaries and documentation
3. **Code generation**: Generate Python dataclasses, SQL DDL, JSON Schema, etc.

```bash
# Install LinkML tools
uv add linkml

# Generate Python dataclasses
uv run gen-python hwsd2_schema.yaml > hwsd2_model.py

# Generate JSON Schema
uv run gen-json-schema hwsd2_schema.yaml > hwsd2_schema.json

# Generate SQL DDL (alternative to hand-written schema)
uv run gen-sqlddl hwsd2_schema.yaml > hwsd2_generated.sql

# Generate documentation
uv run gen-markdown hwsd2_schema.yaml > hwsd2_docs.md
```

## Data Source

The CSV files were extracted from the FAO HWSD v2.0 database. See issue #14 for details on the download and conversion process.

**Original source**: [FAO HWSD v2.0](https://www.fao.org/soils-portal/data-hub/soil-maps-and-databases/harmonized-world-soil-database-v20/en/)

## Units Reference

| Property | Unit | Description |
|----------|------|-------------|
| Depth | cm | Centimeters |
| Bulk Density | g/cm³ | Grams per cubic centimeter |
| Sand/Silt/Clay | % weight | Percentage by weight |
| Coarse Fragments | % volume | Percentage by volume |
| Organic Carbon | % weight | Percentage by weight |
| Total N | g/kg | Grams per kilogram |
| pH | -log(H⁺) | Negative logarithm of hydrogen ion concentration |
| CEC | cmolc/kg | Centimoles of charge per kilogram |
| AWC (SMU) | mm/m | Millimeters per meter |
| AWC (Layer) | mm | Millimeters |
| Electric Conductivity | dS/m | Decisiemens per meter |

## Classification Systems

### WRB (World Reference Base)
- **WRB2**: 2-character codes (AC=Acrisols, AL=Alisols, etc.)
- **WRB4**: 4-character codes with qualifiers (ACfr=Ferric Acrisols, etc.)
- **WRB_PHASES**: Detailed classification with multiple qualifiers

### FAO-90
FAO 1990 soil classification system (legacy)

### USDA Texture
Standard USDA texture triangle classifications (Clay, Silt, Loam, etc.)

### SOTER Texture
SOTER (Soil and Terrain) texture classification (C=Coarse, M=Medium, F=Fine, V=Very Fine, Z=Medium Fine)

## For EcoSIM Integration

To use this soil data with EcoSIM:

1. **Query by coordinates**: Join with spatial data to get soil properties for specific locations
2. **Extract layer profiles**: Use HWSD2_LAYERS to get depth-resolved soil properties
3. **Map to EcoSIM parameters**: Convert HWSD2 properties to EcoSIM NetCDF inputs:
   - Texture classes → EcoSIM soil texture codes
   - Bulk density → directly usable
   - Organic carbon → convert to soil organic matter
   - pH → directly usable
   - CEC → cation exchange capacity inputs

See `../CLAUDE.md` for more details on the EcoSIM Co-Scientist project.

## License

The HWSD v2.0 data is distributed under CC-BY-4.0 license by FAO.
