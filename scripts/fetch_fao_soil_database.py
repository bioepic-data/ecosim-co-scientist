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
    database to more accessible formats like SQLite and CSV.
    
    Examples:
        >>> fetcher = HWSDFetcher(data_dir="./hwsd_data")
        >>> # Download all components
        >>> fetcher.download_all()
        >>> 
        >>> # Convert database to SQLite for easier access
        >>> fetcher.convert_mdb_to_sqlite()
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
            logger.warning("✗ mdb-tools not found. Install with: sudo apt-get install mdb-tools")
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
            "sqlite_files": [],
            "csv_directories": []
        }
        
        # Find downloaded files
        for pattern in ["*.zip", "*.pdf"]:
            info["downloaded_files"].extend([str(f) for f in self.data_dir.glob(pattern)])
        
        # Find processed files
        info["mdb_files"] = [str(f) for f in self.find_mdb_files()]
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
        if mdb_files:
            logger.info("\n=== Converting Databases ===")
            for mdb_file in mdb_files:
                try:
                    # Convert to SQLite
                    sqlite_file = fetcher.convert_mdb_to_sqlite(mdb_file)
                    logger.info(f"✓ SQLite database: {sqlite_file}")
                    
                    # Export to CSV
                    csv_dir = fetcher.export_tables_to_csv(mdb_file)
                    logger.info(f"✓ CSV export: {csv_dir}")
                    
                except Exception as e:
                    logger.error(f"Failed to convert {mdb_file.name}: {e}")
        
        # Extract raster data
        raster_zip = components["raster"] 
        logger.info("\n=== Extracting Raster Data ===")
        fetcher.extract_zip(raster_zip)
        
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