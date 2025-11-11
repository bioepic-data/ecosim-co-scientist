#!/usr/bin/env python
"""
Fetch the FAO Harmonized World Soil Database (HWSD) v2.0.

This script downloads and processes the FAO HWSD database, which provides
global soil property information at 1km resolution with 7 depth layers.

The HWSD includes:
- Database file (.mdb format) with soil mapping units and properties
- Raster file with spatial soil mapping units
- Technical documentation

Downloads from: https://www.fao.org/soils-portal/data-hub/soil-maps-and-databases/harmonized-world-soil-database-v20/en/
"""

import hashlib
import logging
import sqlite3
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Optional
from urllib.request import urlopen, urlretrieve
from urllib.parse import urlparse

import pandas as pd
import rasterio
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# FAO HWSD v2.0 download URLs
HWSD_DATABASE_URL = "https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/HWSD/HWSD2_DB.zip"
HWSD_RASTER_URL = "https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/HWSD/HWSD2_RASTER.zip"
HWSD_TECHNICAL_DOC_URL = "https://www.fao.org/3/cc3823en/cc3823en.pdf"

# Expected file checksums (SHA256) - these should be verified from FAO sources
# Note: These would need to be updated with actual checksums from FAO
EXPECTED_CHECKSUMS = {
    "HWSD2_DB.zip": None,  # Placeholder - would need actual checksum
    "HWSD2_RASTER.zip": None,  # Placeholder - would need actual checksum
    "cc3823en.pdf": None  # Placeholder - would need actual checksum
}


class HWSDFetcher:
    """
    Fetcher for the FAO Harmonized World Soil Database v2.0.
    
    Handles downloading, extracting, and converting the Microsoft Access
    database to more accessible formats like SQLite and CSV. Also processes
    raster data (.bil files) to CSV format for spatial analysis.
    
    Examples:
        >>> fetcher = HWSDFetcher(data_dir="./hwsd_data")
        >>> # Download all components
        >>> fetcher.download_all()
        >>> 
        >>> # Convert database to SQLite for easier access
        >>> fetcher.convert_mdb_to_sqlite()
        >>> 
        >>> # Process raster data to CSV
        >>> fetcher.process_raster_directory_to_csv(raster_dir, sample_rate=0.1)
        >>> 
        >>> # Extract specific soil properties
        >>> soil_data = fetcher.get_soil_properties(['organic_carbon', 'bulk_density'])
    """
    
    def __init__(self, data_dir: str = "./hwsd_data"):
        """
        Initialize the HWSD fetcher.
        
        Args:
            data_dir: Directory to store downloaded HWSD data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True, parents=True)
        logger.info(f"HWSD data directory: {self.data_dir.absolute()}")
    
    def download_file(self, url: str, filename: Optional[str] = None) -> Path:
        """
        Download a file with progress tracking and verification.
        
        Args:
            url: URL to download from
            filename: Optional filename to save as (default: extract from URL)
            
        Returns:
            Path to downloaded file
        """
        if filename is None:
            filename = Path(urlparse(url).path).name
        
        file_path = self.data_dir / filename
        
        # Skip if file already exists
        if file_path.exists():
            logger.info(f"File already exists: {file_path}")
            return file_path
        
        logger.info(f"Downloading {url} to {file_path}")
        
        try:
            # Download with progress indication
            urlretrieve(url, file_path)
            file_size = file_path.stat().st_size / (1024 * 1024)  # MB
            logger.info(f"✓ Download complete: {filename} ({file_size:.1f} MB)")
            
        except Exception as e:
            if file_path.exists():
                file_path.unlink()  # Clean up partial download
            raise RuntimeError(f"Failed to download {url}: {e}")
        
        return file_path
    
    def verify_checksum(self, file_path: Path, expected_checksum: Optional[str] = None) -> bool:
        """
        Verify file integrity using SHA256 checksum.
        
        Args:
            file_path: Path to file to verify
            expected_checksum: Expected SHA256 hash (if None, just compute hash)
            
        Returns:
            True if checksum matches (or if no expected checksum provided)
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        computed_hash = sha256_hash.hexdigest()
        logger.info(f"File {file_path.name} SHA256: {computed_hash}")
        
        if expected_checksum is None:
            return True
        
        if computed_hash.lower() == expected_checksum.lower():
            logger.info("✓ Checksum verification passed")
            return True
        else:
            logger.error("✗ Checksum verification failed!")
            return False
    
    def download_database(self) -> Path:
        """
        Download the HWSD database file (.mdb format).
        
        Returns:
            Path to downloaded database zip file
        """
        logger.info("Downloading HWSD database...")
        return self.download_file(HWSD_DATABASE_URL, "HWSD2_DB.zip")
    
    def download_raster(self) -> Path:
        """
        Download the HWSD raster files.
        
        Returns:
            Path to downloaded raster zip file
        """
        logger.info("Downloading HWSD raster data...")
        return self.download_file(HWSD_RASTER_URL, "HWSD2_RASTER.zip")
    
    def download_documentation(self) -> Path:
        """
        Download the technical documentation PDF.
        
        Returns:
            Path to downloaded documentation file
        """
        logger.info("Downloading HWSD technical documentation...")
        return self.download_file(HWSD_TECHNICAL_DOC_URL, "hwsd_technical_report.pdf")
    
    def download_all(self) -> dict[str, Path]:
        """
        Download all HWSD components.
        
        Returns:
            Dictionary mapping component names to file paths
        """
        logger.info("Starting HWSD v2.0 download...")
        
        components = {
            "database": self.download_database(),
            "raster": self.download_raster(),
            "documentation": self.download_documentation()
        }
        
        logger.info("✓ All HWSD components downloaded successfully!")
        return components
    
    def extract_zip(self, zip_path: Path, extract_to: Optional[Path] = None) -> Path:
        """
        Extract a ZIP file to the specified directory.
        
        Args:
            zip_path: Path to ZIP file to extract
            extract_to: Directory to extract to (default: same name as zip without extension)
            
        Returns:
            Path to extraction directory
        """
        if extract_to is None:
            extract_to = self.data_dir / zip_path.stem
        
        extract_to.mkdir(exist_ok=True, parents=True)
        
        logger.info(f"Extracting {zip_path.name} to {extract_to}")
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        
        # List extracted files
        extracted_files = list(extract_to.rglob("*"))
        logger.info(f"✓ Extracted {len(extracted_files)} files to {extract_to}")
        
        return extract_to
    
    def find_mdb_files(self) -> list[Path]:
        """
        Find all Microsoft Access database files in the data directory.
        
        Returns:
            List of .mdb file paths
        """
        mdb_files = list(self.data_dir.rglob("*.mdb"))
        logger.info(f"Found {len(mdb_files)} .mdb files: {[f.name for f in mdb_files]}")
        return mdb_files
    
    def check_mdb_tools(self) -> bool:
        """
        Check if mdb-tools are available for converting Access databases.
        
        Returns:
            True if mdb-tools are available
        """
        try:
            result = subprocess.run(['mdb-ver', '--help'], 
                                 capture_output=True, text=True, timeout=10)
            logger.info("✓ mdb-tools are available")
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("✗ mdb-tools not found. Install with: sudo apt-get install mdbtools")
            return False
    
    def convert_mdb_to_sqlite(self, mdb_path: Path, sqlite_path: Optional[Path] = None) -> Path:
        """
        Convert Microsoft Access database to SQLite.
        
        Args:
            mdb_path: Path to .mdb file
            sqlite_path: Path to output SQLite file (default: same name with .db extension)
            
        Returns:
            Path to created SQLite database
        """
        if sqlite_path is None:
            sqlite_path = mdb_path.with_suffix(".db")
        
        if not self.check_mdb_tools():
            raise RuntimeError("mdb-tools required for .mdb conversion")
        
        logger.info(f"Converting {mdb_path.name} to SQLite: {sqlite_path.name}")
        
        # Get list of tables in the Access database
        result = subprocess.run(['mdb-tables', '-1', str(mdb_path)], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to list tables: {result.stderr}")
        
        table_names = [name.strip() for name in result.stdout.split('\n') if name.strip()]
        logger.info(f"Found {len(table_names)} tables: {table_names}")
        
        # Create SQLite database and import tables
        conn = sqlite3.connect(sqlite_path)
        
        for table_name in table_names:
            logger.info(f"Converting table: {table_name}")
            
            # Export table to CSV using mdb-export
            csv_result = subprocess.run(['mdb-export', str(mdb_path), table_name],
                                      capture_output=True, text=True)
            if csv_result.returncode != 0:
                logger.warning(f"Failed to export table {table_name}: {csv_result.stderr}")
                continue
            
            # Read CSV data into pandas and save to SQLite
            try:
                # Use StringIO to read CSV from memory
                from io import StringIO
                csv_data = StringIO(csv_result.stdout)
                df = pd.read_csv(csv_data)
                df.to_sql(table_name, conn, if_exists='replace', index=False)
                logger.info(f"✓ Imported {len(df)} rows to table {table_name}")
                
            except Exception as e:
                logger.warning(f"Failed to import table {table_name}: {e}")
        
        conn.close()
        logger.info(f"✓ SQLite conversion complete: {sqlite_path}")
        return sqlite_path
    
    def find_bil_files(self) -> list[Path]:
        """
        Find all BIL (Band Interleaved by Line) raster files in the data directory.
        
        Returns:
            List of .bil file paths
        """
        bil_files = list(self.data_dir.rglob("*.bil"))
        logger.info(f"Found {len(bil_files)} .bil files: {[f.name for f in bil_files]}")
        return bil_files
    
    def process_bil_to_csv(self, bil_path: Path, output_path: Optional[Path] = None, sample_rate: float = 1.0, 
                          sqlite_db_path: Optional[Path] = None) -> Path:
        """
        Convert BIL raster file to CSV format with soil mapping unit codes.
        
        HWSD2 BIL files contain soil mapping unit codes (integers) that link to the 
        attribute database containing actual soil properties. This method extracts 
        the mapping unit codes and can optionally join with database tables to 
        include actual soil variable values.
        
        Args:
            bil_path: Path to .bil raster file
            output_path: Path to output CSV file (default: bil filename + .csv)
            sample_rate: Fraction of pixels to sample (1.0 = all pixels, 0.1 = 10% sample)
            sqlite_db_path: Optional path to SQLite database for joining soil variables
            
        Returns:
            Path to created CSV file
        """
        if output_path is None:
            output_path = bil_path.with_suffix('.csv')
        
        logger.info(f"Converting {bil_path.name} to CSV: {output_path.name}")
        
        try:
            with rasterio.open(bil_path) as src:
                # Get raster metadata
                width = src.width
                height = src.height
                transform = src.transform
                crs = src.crs
                nodata = src.nodata
                
                logger.info(f"Raster dimensions: {width} x {height} pixels")
                logger.info(f"Coordinate system: {crs}")
                logger.info(f"NoData value: {nodata}")
                
                # Read the first band (soil mapping unit codes)
                data = src.read(1)
                
                # Create coordinate grids
                x_coords = []
                y_coords = []
                mapping_units = []
                
                # Calculate sampling step
                step = int(1.0 / sample_rate) if sample_rate < 1.0 else 1
                
                for row in range(0, height, step):
                    for col in range(0, width, step):
                        # Convert pixel coordinates to geographic coordinates
                        x, y = rasterio.transform.xy(transform, row, col)
                        mapping_unit_code = int(data[row, col])
                        
                        # Skip nodata values
                        if nodata is not None and mapping_unit_code == nodata:
                            continue
                        
                        x_coords.append(x)
                        y_coords.append(y)
                        mapping_units.append(mapping_unit_code)
                
                # Create DataFrame with mapping unit codes
                df = pd.DataFrame({
                    'longitude': x_coords,
                    'latitude': y_coords,
                    'soil_mapping_unit': mapping_units
                })
                
                # Join with soil properties if database provided
                if sqlite_db_path and sqlite_db_path.exists():
                    df = self._join_soil_properties(df, sqlite_db_path)
                
                # Save to CSV
                df.to_csv(output_path, index=False)
                
                logger.info(f"✓ Exported {len(df)} valid pixels to {output_path.name}")
                logger.info(f"Unique mapping units: {df['soil_mapping_unit'].nunique()}")
                logger.info(f"Mapping unit range: {df['soil_mapping_unit'].min()} to {df['soil_mapping_unit'].max()}")
                if 'soc_topsoil' in df.columns:
                    logger.info(f"Soil variables joined from database")
                
        except Exception as e:
            logger.error(f"Failed to process {bil_path.name}: {e}")
            raise
        
        return output_path
    
    def _join_soil_properties(self, df: pd.DataFrame, sqlite_db_path: Path) -> pd.DataFrame:
        """
        Join raster mapping unit codes with soil properties from ALL database tables.
        
        Args:
            df: DataFrame with longitude, latitude, and soil_mapping_unit columns
            sqlite_db_path: Path to SQLite database with soil property tables
            
        Returns:
            Enhanced DataFrame with soil property columns from all available tables
        """
        try:
            conn = sqlite3.connect(sqlite_db_path)
            cursor = conn.cursor()
            
            # Get all available tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            available_tables = [row[0] for row in cursor.fetchall()]
            logger.info(f"Available database tables: {available_tables}")
            
            # Start with the base dataframe
            result_df = df.copy()
            total_joined_columns = 0
            
            # Process each table to extract variables
            for table_name in available_tables:
                try:
                    # Get table schema
                    cursor.execute(f"PRAGMA table_info({table_name});")
                    table_info = cursor.fetchall()
                    columns = [row[1] for row in table_info]
                    
                    logger.info(f"Processing table {table_name} with {len(columns)} columns")
                    
                    # Find potential mapping unit columns
                    mapping_unit_cols = ['MU_GLOBAL', 'MAPPING_UNIT', 'MU_CODE', 'SMU_ID', 'CODE', 'ID']
                    mapping_col = None
                    for col in mapping_unit_cols:
                        if col in columns:
                            mapping_col = col
                            break
                    
                    if not mapping_col:
                        logger.info(f"  Skipping {table_name}: No mapping unit column found")
                        continue
                    
                    # Build column list for extraction (excluding the mapping column)
                    data_columns = [col for col in columns if col != mapping_col]
                    
                    if not data_columns:
                        logger.info(f"  Skipping {table_name}: No data columns found")
                        continue
                    
                    # Create table-prefixed column names to avoid conflicts
                    prefixed_columns = []
                    for col in data_columns:
                        # Create descriptive column name with table context and units hint
                        col_name = f"{table_name.lower()}_{col.lower()}"
                        
                        # Add unit hints based on common HWSD variable patterns
                        if 'ph' in col.lower():
                            col_name += "_ph_units"
                        elif 'awc' in col.lower() or 'water' in col.lower():
                            col_name += "_percent"
                        elif 'bulk' in col.lower() or 'density' in col.lower():
                            col_name += "_g_cm3"
                        elif any(texture in col.lower() for texture in ['sand', 'silt', 'clay']):
                            col_name += "_percent"
                        elif 'soc' in col.lower() or 'carbon' in col.lower():
                            col_name += "_percent"
                        elif 'cec' in col.lower():
                            col_name += "_cmol_kg"
                        elif 'drainage' in col.lower():
                            col_name += "_class"
                        elif 'coverage' in col.lower():
                            col_name += "_percent"
                        elif 'depth' in col.lower():
                            col_name += "_cm"
                        elif 'value' in col.lower():
                            col_name += "_value"
                        else:
                            col_name += "_units_unknown"
                            
                        prefixed_columns.append(f"{col} as {col_name}")
                    
                    # Query the table
                    query = f"""
                    SELECT {mapping_col}, {', '.join(prefixed_columns)}
                    FROM {table_name}
                    WHERE {mapping_col} IS NOT NULL
                    """
                    
                    table_df = pd.read_sql_query(query, conn)
                    
                    if table_df.empty:
                        logger.info(f"  Skipping {table_name}: No data rows")
                        continue
                    
                    # Ensure compatible data types for merging
                    # Convert both mapping unit columns to consistent type (int64)
                    try:
                        # Convert table mapping column to int64, handling any non-numeric values
                        table_df[mapping_col] = pd.to_numeric(table_df[mapping_col], errors='coerce')
                        # Remove rows where conversion failed (NaN values)
                        table_df = table_df.dropna(subset=[mapping_col])
                        # Convert to int64
                        table_df[mapping_col] = table_df[mapping_col].astype('int64')
                        
                        # Ensure main dataframe mapping column is also int64
                        result_df['soil_mapping_unit'] = result_df['soil_mapping_unit'].astype('int64')
                        
                        # Check if table still has data after conversion
                        if table_df.empty:
                            logger.warning(f"  Skipping {table_name}: No valid mapping units after type conversion")
                            continue
                            
                    except (ValueError, TypeError) as e:
                        logger.warning(f"  Failed to convert data types for {table_name}: {e}")
                        continue
                    
                    # Join with result dataframe
                    before_cols = len(result_df.columns)
                    result_df = result_df.merge(
                        table_df,
                        left_on='soil_mapping_unit',
                        right_on=mapping_col,
                        how='left',
                        suffixes=('', f'_{table_name}')
                    )
                    
                    # Drop duplicate mapping column
                    if mapping_col in result_df.columns:
                        result_df = result_df.drop(columns=[mapping_col])
                    
                    after_cols = len(result_df.columns)
                    joined_cols = after_cols - before_cols
                    total_joined_columns += joined_cols
                    
                    logger.info(f"  ✓ Joined {joined_cols} variables from {table_name}")
                    
                except Exception as e:
                    logger.warning(f"  Failed to process table {table_name}: {e}")
                    continue
            
            conn.close()
            
            # Log final statistics
            logger.info(f"✓ Multi-table join complete: {total_joined_columns} total variables from {len(available_tables)} tables")
            logger.info(f"Final DataFrame shape: {result_df.shape}")
            
            # Log a sample of joined columns (excluding coordinate columns)
            data_cols = [col for col in result_df.columns if col not in ['longitude', 'latitude', 'soil_mapping_unit']]
            if data_cols:
                sample_cols = data_cols[:5]  # Show first 5 data columns
                logger.info(f"Sample variables: {sample_cols}")
                if len(data_cols) > 5:
                    logger.info(f"... and {len(data_cols) - 5} more variables")
            
            return result_df
            
        except Exception as e:
            logger.warning(f"Failed to join soil properties: {e}")
            return df
    
    def process_raster_directory_to_csv(self, raster_dir: Path, output_dir: Optional[Path] = None, 
                                       sample_rate: float = 0.1, sqlite_db_path: Optional[Path] = None) -> Path:
        """
        Process all BIL files in a directory to CSV format with optional soil variable joining.
        
        Args:
            raster_dir: Directory containing .bil files
            output_dir: Directory to save CSV files (default: raster_dir + "_csv") 
            sample_rate: Fraction of pixels to sample (default: 0.1 for 10% sample)
            sqlite_db_path: Optional path to SQLite database for joining soil variables
            
        Returns:
            Path to directory containing CSV files
        """
        if output_dir is None:
            output_dir = self.data_dir / f"{raster_dir.name}_csv"
        
        output_dir.mkdir(exist_ok=True, parents=True)
        
        logger.info(f"Processing raster files from {raster_dir} to CSV in {output_dir}")
        logger.info(f"Using {sample_rate*100:.1f}% pixel sampling rate")
        
        if sqlite_db_path and sqlite_db_path.exists():
            logger.info(f"Will join with soil properties from: {sqlite_db_path.name}")
        else:
            logger.info("Processing mapping unit codes only (no database join)")
        
        # Find all .bil files in the directory
        bil_files = list(raster_dir.rglob("*.bil"))
        
        if not bil_files:
            logger.warning(f"No .bil files found in {raster_dir}")
            return output_dir
        
        for bil_file in bil_files:
            csv_path = output_dir / f"{bil_file.stem}.csv"
            try:
                self.process_bil_to_csv(bil_file, csv_path, sample_rate, sqlite_db_path)
            except Exception as e:
                logger.warning(f"Failed to process {bil_file.name}: {e}")
                continue
        
        logger.info(f"✓ Raster processing complete: {output_dir}")
        return output_dir
    
    def export_tables_to_csv(self, mdb_path: Path, output_dir: Optional[Path] = None) -> Path:
        """
        Export all tables from Access database to CSV files.
        
        Args:
            mdb_path: Path to .mdb file
            output_dir: Directory to save CSV files (default: mdb filename + "_csv")
            
        Returns:
            Path to directory containing CSV files
        """
        if output_dir is None:
            output_dir = self.data_dir / f"{mdb_path.stem}_csv"
        
        output_dir.mkdir(exist_ok=True, parents=True)
        
        if not self.check_mdb_tools():
            raise RuntimeError("mdb-tools required for .mdb conversion")
        
        logger.info(f"Exporting tables from {mdb_path.name} to CSV files in {output_dir}")
        
        # Get table names
        result = subprocess.run(['mdb-tables', '-1', str(mdb_path)], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to list tables: {result.stderr}")
        
        table_names = [name.strip() for name in result.stdout.split('\n') if name.strip()]
        
        # Export each table to CSV
        for table_name in table_names:
            csv_path = output_dir / f"{table_name}.csv"
            logger.info(f"Exporting {table_name} to {csv_path.name}")
            
            with open(csv_path, 'w') as f:
                result = subprocess.run(['mdb-export', str(mdb_path), table_name], 
                                      stdout=f, text=True)
                if result.returncode != 0:
                    logger.warning(f"Failed to export table {table_name}")
                    continue
            
            # Report row count
            try:
                df = pd.read_csv(csv_path)
                logger.info(f"✓ Exported {len(df)} rows to {csv_path.name}")
            except Exception:
                logger.warning(f"Could not verify row count for {csv_path.name}")
        
        logger.info(f"✓ CSV export complete: {output_dir}")
        return output_dir
    
    def get_database_info(self) -> dict:
        """
        Get information about downloaded and processed HWSD databases.
        
        Returns:
            Dictionary with database information
        """
        info = {
            "data_directory": str(self.data_dir.absolute()),
            "downloaded_files": [],
            "mdb_files": [],
            "bil_files": [],
            "sqlite_files": [],
            "csv_directories": []
        }
        
        # Find downloaded files
        for pattern in ["*.zip", "*.pdf"]:
            info["downloaded_files"].extend([str(f) for f in self.data_dir.glob(pattern)])
        
        # Find processed files
        info["mdb_files"] = [str(f) for f in self.find_mdb_files()]
        info["bil_files"] = [str(f) for f in self.find_bil_files()]
        info["sqlite_files"] = [str(f) for f in self.data_dir.rglob("*.db")]
        info["csv_directories"] = [str(d) for d in self.data_dir.glob("*_csv") if d.is_dir()]
        
        return info


def main():
    """
    Main function demonstrating HWSD fetcher usage.
    
    Downloads the complete HWSD v2.0 database and converts it to
    accessible formats (SQLite and CSV).
    """
    # Initialize fetcher
    fetcher = HWSDFetcher(data_dir="./hwsd_data")
    
    try:
        # Download all components
        logger.info("=== Starting HWSD v2.0 Download ===")
        components = fetcher.download_all()
        
        # Extract database zip
        db_zip = components["database"]
        logger.info("\n=== Extracting Database ===")
        fetcher.extract_zip(db_zip)
        
        # Find and convert .mdb files
        mdb_files = fetcher.find_mdb_files()
        sqlite_files = []
        if mdb_files:
            logger.info("\n=== Converting Databases ===")
            for mdb_file in mdb_files:
                try:
                    # Convert to SQLite
                    sqlite_file = fetcher.convert_mdb_to_sqlite(mdb_file)
                    sqlite_files.append(sqlite_file)
                    logger.info(f"✓ SQLite database: {sqlite_file}")
                    
                    # Export to CSV
                    csv_dir = fetcher.export_tables_to_csv(mdb_file)
                    logger.info(f"✓ CSV export: {csv_dir}")
                    
                except Exception as e:
                    logger.error(f"Failed to convert {mdb_file.name}: {e}")
        
        # Extract raster data
        raster_zip = components["raster"] 
        logger.info("\n=== Extracting Raster Data ===")
        raster_extract_dir = fetcher.extract_zip(raster_zip)
        
        # Process .bil files to CSV with soil variable joining
        bil_files = fetcher.find_bil_files()
        if bil_files:
            logger.info("\n=== Converting Raster Files to CSV ===")
            try:
                # Use the first SQLite database if available for joining soil variables
                sqlite_db = sqlite_files[0] if sqlite_files else None
                csv_dir = fetcher.process_raster_directory_to_csv(
                    raster_extract_dir, 
                    sample_rate=0.1, 
                    sqlite_db_path=sqlite_db
                )
                logger.info(f"✓ Raster CSV export: {csv_dir}")
            except Exception as e:
                logger.error(f"Failed to process raster files: {e}")
        
        # Show final summary
        logger.info("\n=== HWSD Setup Complete ===")
        info = fetcher.get_database_info()
        for key, value in info.items():
            if isinstance(value, list) and value:
                logger.info(f"{key}: {len(value)} items")
                for item in value[:3]:  # Show first 3 items
                    logger.info(f"  - {Path(item).name}")
                if len(value) > 3:
                    logger.info(f"  - ... and {len(value) - 3} more")
            elif not isinstance(value, list):
                logger.info(f"{key}: {value}")
        
    except Exception as e:
        logger.error(f"HWSD setup failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())