# FAO Harmonized World Soil Database (HWSD) v2.0

## Overview

The FAO Harmonized World Soil Database (HWSD) v2.0 provides comprehensive global soil information at 1km resolution. This document describes how to use the HWSD fetcher pipeline in the ecosim-co-scientist project.

### What is HWSD?

The HWSD v2.0 includes:
- **Global Coverage**: 1km resolution soil mapping units
- **7 Depth Layers**: 0-20cm, 20-40cm, 40-60cm, 60-80cm, 80-100cm, 100-150cm, 150-200cm  
- **29,538 Soil Mapping Units**: Increased from 16,327 in v1.2
- **Soil Properties**: Morphology, chemistry, physics, and biogeochemical parameters

**Source**: [FAO Soils Portal](https://www.fao.org/soils-portal/data-hub/soil-maps-and-databases/harmonized-world-soil-database-v20/en/)

## Installation

### Prerequisites

1. **Python Dependencies**
   ```bash
   # Install project dependencies (includes pandas)
   uv sync
   ```

2. **Microsoft Access Database Tools**
   
   The HWSD database is provided in Microsoft Access format (.mdb). To convert it to more accessible formats:
   
   ```bash
   # Run the installation script
   ./scripts/install_mdb_tools.sh
   
   # Or install manually:
   # Ubuntu/Debian:
   sudo apt-get install mdb-tools
   
   # macOS:
   brew install mdb-tools
   
   # RHEL/CentOS:
   sudo yum install mdb-tools
   ```

## Quick Start

### Basic Usage

```python
#!/usr/bin/env python
from scripts.fetch_fao_soil_database import HWSDFetcher

# Initialize the fetcher
fetcher = HWSDFetcher(data_dir="./hwsd_data")

# Download all HWSD components
components = fetcher.download_all()

# Extract the database
fetcher.extract_zip(components["database"])

# Convert to accessible formats
mdb_files = fetcher.find_mdb_files()
for mdb_file in mdb_files:
    # Convert to SQLite
    sqlite_db = fetcher.convert_mdb_to_sqlite(mdb_file)
    print(f"SQLite database: {sqlite_db}")
    
    # Export to CSV files
    csv_dir = fetcher.export_tables_to_csv(mdb_file)
    print(f"CSV files: {csv_dir}")
```

### Command Line Usage

```bash
# Download and process the complete HWSD database
python scripts/fetch_fao_soil_database.py

# Run tests
python tests/test_fao_soil_fetcher.py

# Run with integration tests (requires internet)
python tests/test_fao_soil_fetcher.py --integration
```

## Data Components

### 1. Database Component (HWSD2_DB.zip)

Contains the Microsoft Access database with:
- **Soil Mapping Units**: Geographic polygons with soil classification
- **Soil Properties**: Physical and chemical characteristics by depth layer
- **Metadata**: Data sources, measurement methods, quality indicators

**Size**: ~50-100 MB (compressed)

### 2. Raster Component (HWSD2_RASTER.zip)

Contains GIS raster files:
- **Raster Image**: Grid cells linked to soil mapping units  
- **Coordinate System**: WGS84 geographic coordinates
- **Resolution**: 30 arc-seconds (~1km at equator)

**Size**: ~500-1000 MB (compressed)

### 3. Documentation

- **Technical Report**: Complete methodology and data sources
- **User Guide**: Instructions for data interpretation
- **Metadata**: Variable definitions and units

## API Reference

### HWSDFetcher Class

```python
class HWSDFetcher:
    \"\"\"Fetcher for FAO Harmonized World Soil Database v2.0.\"\"\"
    
    def __init__(self, data_dir: str = \"./hwsd_data\"):
        \"\"\"Initialize with data directory.\"\"\"
    
    def download_all(self) -> dict[str, Path]:
        \"\"\"Download database, raster, and documentation.\"\"\"
    
    def download_database(self) -> Path:
        \"\"\"Download database component only.\"\"\"
    
    def download_raster(self) -> Path:
        \"\"\"Download raster component only.\"\"\"
    
    def extract_zip(self, zip_path: Path) -> Path:
        \"\"\"Extract ZIP file.\"\"\"
    
    def convert_mdb_to_sqlite(self, mdb_path: Path) -> Path:
        \"\"\"Convert Access database to SQLite.\"\"\"
    
    def export_tables_to_csv(self, mdb_path: Path) -> Path:
        \"\"\"Export all tables to CSV files.\"\"\"
    
    def find_mdb_files(self) -> list[Path]:
        \"\"\"Find .mdb files in data directory.\"\"\"
    
    def get_database_info(self) -> dict:
        \"\"\"Get summary of downloaded/processed data.\"\"\"
```

### Key Methods

#### Download Methods

```python
# Download individual components
db_file = fetcher.download_database()
raster_file = fetcher.download_raster()
doc_file = fetcher.download_documentation()

# Download everything at once
components = fetcher.download_all()
```

#### Conversion Methods

```python
# Convert Microsoft Access to SQLite
sqlite_file = fetcher.convert_mdb_to_sqlite(mdb_path)

# Export to CSV files for easy analysis
csv_directory = fetcher.export_tables_to_csv(mdb_path)

# Extract ZIP archives
extract_dir = fetcher.extract_zip(zip_path)
```

#### Utility Methods

```python
# Check if mdb-tools are available
has_tools = fetcher.check_mdb_tools()

# Verify file integrity
is_valid = fetcher.verify_checksum(file_path, expected_hash)

# Get overview of processed data
info = fetcher.get_database_info()
```

## Data Structure

### Directory Layout

After processing, the data directory structure looks like:

```
hwsd_data/
├── HWSD2_DB.zip              # Downloaded database archive
├── HWSD2_RASTER.zip          # Downloaded raster archive  
├── hwsd_technical_report.pdf # Documentation
├── HWSD2_DB/                 # Extracted database
│   ├── HWSD2.mdb            # Microsoft Access database
│   └── ...                  
├── HWSD2_RASTER/            # Extracted raster files
│   ├── hwsd2.bil            # Raster data
│   ├── hwsd2.hdr            # Header file
│   └── ...
├── HWSD2.db                 # SQLite conversion
└── HWSD2_csv/               # CSV exports
    ├── D_SOIL.csv           # Soil properties table
    ├── SOIL.csv             # Soil mapping units
    └── ...
```

### Database Tables

The HWSD database typically contains these key tables:

| Table | Description | Records |
|-------|-------------|---------|
| `SOIL` | Soil mapping units with geographic codes | ~29,000 |
| `D_SOIL` | Detailed soil properties by depth layer | ~200,000 |
| `ROOTS` | Root zone characteristics | ~29,000 |
| `D_ROOTS` | Detailed root properties | ~200,000 |

### Key Variables

Major soil variables available in HWSD v2.0:

| Variable | Unit | Description |
|----------|------|-------------|
| `SOC` | % | Soil organic carbon content |
| `BULK_DENSITY` | g/cm³ | Soil bulk density |
| `AWC` | % | Available water capacity |
| `SAND`, `SILT`, `CLAY` | % | Soil texture fractions |
| `PH_H2O` | - | Soil pH in water |
| `CEC` | cmol/kg | Cation exchange capacity |

## Examples

### Example 1: Basic Download and Conversion

```python
from scripts.fetch_fao_soil_database import HWSDFetcher

# Setup
fetcher = HWSDFetcher(\"./my_soil_data\")

# Download and extract database
db_zip = fetcher.download_database() 
fetcher.extract_zip(db_zip)

# Convert to SQLite for easier access
mdb_files = fetcher.find_mdb_files()
if mdb_files:
    sqlite_file = fetcher.convert_mdb_to_sqlite(mdb_files[0])
    print(f\"SQLite database ready: {sqlite_file}\")
```

### Example 2: Working with Converted Data

```python
import sqlite3
import pandas as pd

# Connect to converted SQLite database
conn = sqlite3.connect(\"hwsd_data/HWSD2.db\")

# Query soil organic carbon for specific regions
query = \"\"\"
SELECT mu_global, soc, depth 
FROM D_SOIL 
WHERE soc > 2.0 AND depth = '0-30cm'
LIMIT 100
\"\"\"

soil_data = pd.read_sql_query(query, conn)
print(soil_data.head())

conn.close()
```

### Example 3: Geographic Analysis

```python
import pandas as pd

# Load soil mapping units
soil_units = pd.read_csv(\"hwsd_data/HWSD2_csv/SOIL.csv\")

# Load detailed soil properties  
soil_props = pd.read_csv(\"hwsd_data/HWSD2_csv/D_SOIL.csv\")

# Merge for analysis
merged = soil_units.merge(soil_props, on='mu_global')

# Analyze soil organic carbon by climate zone
soc_by_zone = merged.groupby('climate_zone')['soc'].agg(['mean', 'std'])
print(soc_by_zone)
```

## Troubleshooting

### Common Issues

1. **mdb-tools not found**
   ```
   ✗ mdb-tools not found. Install with: sudo apt-get install mdb-tools
   ```
   **Solution**: Install mdb-tools using the provided installation script.

2. **Download fails**
   ```
   Failed to download [...]: HTTP Error 404
   ```
   **Solution**: Check internet connection. FAO may have updated URLs.

3. **Access database conversion fails**
   ```
   Failed to list tables: [access denied]
   ```
   **Solution**: The .mdb file may be corrupted. Re-download the database component.

4. **Large file sizes**
   ```
   OSError: [Errno 28] No space left on device
   ```
   **Solution**: Ensure sufficient disk space (~2-3 GB for complete HWSD).

### Getting Help

- **Check logs**: The fetcher provides detailed logging output
- **Verify installation**: Run `python tests/test_fao_soil_fetcher.py`
- **Check file integrity**: Use the built-in checksum verification
- **Report issues**: Document errors with log output

## Integration with EcoSIM

### Soil Data Pipeline

The HWSD data integrates with EcoSIM modeling workflows:

1. **Parameter Extraction**: Extract soil properties for model sites
2. **Spatial Interpolation**: Interpolate between HWSD grid cells  
3. **Unit Conversion**: Convert HWSD units to EcoSIM requirements
4. **NetCDF Generation**: Create EcoSIM-compatible input files

### Example Integration

```python
# Extract soil data for EcoSIM site coordinates
site_coords = [(45.0, -122.0), (46.0, -121.0)]  # lat, lon pairs

for lat, lon in site_coords:
    # Get nearest HWSD mapping unit
    soil_unit = get_nearest_hwsd_unit(lat, lon)
    
    # Extract soil properties by depth layer
    soil_profile = extract_soil_profile(soil_unit)
    
    # Convert to EcoSIM NetCDF format
    ecosim_file = create_ecosim_soil_input(soil_profile, lat, lon)
    print(f\"Created: {ecosim_file}\")
```

## Citations

When using HWSD data, please cite:

> FAO. 2023. Harmonized World Soil Database version 2.0. Rome. https://doi.org/10.4060/cc3823en

## License

The HWSD database is provided by FAO for non-commercial research use. See the technical documentation for full license terms.

**Usage Rights**:
- ✓ Educational and research use
- ✓ Non-commercial applications  
- ✗ Redistribution without permission
- ✗ Commercial use without license

---

**Last Updated**: November 2024  
**HWSD Version**: 2.0  
**Fetcher Version**: 1.0