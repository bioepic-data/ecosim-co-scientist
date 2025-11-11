#!/usr/bin/env python
"""
Extract soil profiles from HWSD2 database by geographic coordinates.

This module provides functions to query the HWSD2 (Harmonized World Soil Database v2.0)
gridded dataset and extract detailed soil profiles for specific locations.

Usage:
    >>> from hwsd2_extractor import get_soil_profile
    >>> profile = get_soil_profile(lat=40.0, lon=-105.0, db_path="hwsd2.db")
    >>> print(profile['layers'])  # 7-layer soil profile

Functions:
    - latlon_to_smu_id: Convert lat/lon to HWSD2_SMU_ID from raster
    - get_smu_properties: Get soil properties for a given SMU_ID from database
    - get_soil_profile: Combined function to get profile from lat/lon
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
import struct
import duckdb
import pandas as pd


class HWSD2Extractor:
    """
    Extract soil data from HWSD2 gridded database.

    Attributes:
        raster_path: Path to HWSD2.bil raster file
        db_path: Path to DuckDB database with soil properties
        ncols: Number of columns in raster (43200)
        nrows: Number of rows in raster (21600)
        xdim: Pixel width in degrees (0.00833333)
        ydim: Pixel height in degrees (0.00833333)
        ulx: Upper left X coordinate (-179.995833)
        uly: Upper left Y coordinate (89.995833)
        nodata: NODATA value (65535)

    Examples:
        >>> extractor = HWSD2Extractor()
        >>> smu_id = extractor.latlon_to_smu_id(40.0, -105.0)
        >>> profile = extractor.get_smu_properties(smu_id)
    """

    def __init__(
        self,
        raster_path: Optional[str] = None,
        db_path: Optional[str] = None,
    ):
        """
        Initialize HWSD2 extractor.

        Args:
            raster_path: Path to HWSD2.bil file. If None, looks in HWSD2_RASTER/
            db_path: Path to DuckDB database. If None, looks for hwsd2.db
        """
        # Set default paths relative to this file
        base_dir = Path(__file__).parent

        if raster_path is None:
            raster_path = base_dir / "HWSD2_RASTER" / "HWSD2.bil"
        self.raster_path = Path(raster_path)

        if db_path is None:
            db_path = base_dir / "hwsd2.db"
        self.db_path = Path(db_path)

        # Raster metadata (from HWSD2.hdr)
        self.ncols = 43200
        self.nrows = 21600
        self.xdim = 0.00833333333333333
        self.ydim = 0.00833333333333333
        self.ulx = -179.995833333333
        self.uly = 89.9958333333333
        self.nodata = 65535

        # Validate files exist
        if not self.raster_path.exists():
            raise FileNotFoundError(f"Raster file not found: {self.raster_path}")

    def latlon_to_rowcol(self, lat: float, lon: float) -> Tuple[int, int]:
        """
        Convert latitude/longitude to raster row/column indices.

        Args:
            lat: Latitude in decimal degrees (-90 to 90)
            lon: Longitude in decimal degrees (-180 to 180)

        Returns:
            Tuple of (row, col) indices

        Raises:
            ValueError: If coordinates are out of bounds

        Examples:
            >>> extractor = HWSD2Extractor()
            >>> row, col = extractor.latlon_to_rowcol(40.0, -105.0)
            >>> 0 <= row < 21600 and 0 <= col < 43200
            True
        """
        if not (-90 <= lat <= 90):
            raise ValueError(f"Latitude {lat} out of range [-90, 90]")
        if not (-180 <= lon <= 180):
            raise ValueError(f"Longitude {lon} out of range [-180, 180]")

        # Calculate row and column
        # Row increases from north to south
        col = int((lon - self.ulx) / self.xdim)
        row = int((self.uly - lat) / self.ydim)

        # Clamp to valid range
        row = max(0, min(self.nrows - 1, row))
        col = max(0, min(self.ncols - 1, col))

        return row, col

    def read_raster_value(self, row: int, col: int) -> int:
        """
        Read a single pixel value from the raster file.

        Args:
            row: Row index (0 to 21599)
            col: Column index (0 to 43199)

        Returns:
            HWSD2_SMU_ID value, or nodata value (65535) if no data

        Examples:
            >>> extractor = HWSD2Extractor()
            >>> # Read a value (exact result depends on location)
            >>> value = extractor.read_raster_value(5000, 15000)
            >>> isinstance(value, int)
            True
        """
        if not (0 <= row < self.nrows):
            raise ValueError(f"Row {row} out of range [0, {self.nrows})")
        if not (0 <= col < self.ncols):
            raise ValueError(f"Column {col} out of range [0, {self.ncols})")

        # Calculate byte offset
        # BIL format: Band Interleaved by Line
        # Each pixel is 2 bytes (unsigned 16-bit integer)
        offset = (row * self.ncols + col) * 2

        with open(self.raster_path, 'rb') as f:
            f.seek(offset)
            data = f.read(2)
            if len(data) != 2:
                return self.nodata

            # Little-endian unsigned short
            value = struct.unpack('<H', data)[0]
            return value

    def latlon_to_smu_id(self, lat: float, lon: float) -> Optional[int]:
        """
        Convert latitude/longitude to HWSD2_SMU_ID.

        Args:
            lat: Latitude in decimal degrees (-90 to 90)
            lon: Longitude in decimal degrees (-180 to 180)

        Returns:
            HWSD2_SMU_ID, or None if no data at this location (ocean, etc.)

        Examples:
            >>> extractor = HWSD2Extractor()
            >>> # Test a location in Colorado (should have data)
            >>> smu_id = extractor.latlon_to_smu_id(40.0, -105.0)
            >>> smu_id is None or isinstance(smu_id, int)
            True
        """
        row, col = self.latlon_to_rowcol(lat, lon)
        value = self.read_raster_value(row, col)

        if value == self.nodata:
            return None

        return value

    def get_smu_properties(
        self,
        smu_id: int,
        include_layers: bool = True,
        include_metadata: bool = True,
    ) -> Dict:
        """
        Get soil properties for a given HWSD2_SMU_ID from the database.

        Args:
            smu_id: HWSD2 Soil Mapping Unit ID
            include_layers: Include detailed layer properties (default: True)
            include_metadata: Include SMU summary metadata (default: True)

        Returns:
            Dictionary with keys:
                - 'smu_id': The SMU ID
                - 'metadata': SMU summary properties (if include_metadata=True)
                - 'layers': DataFrame with 7 layers of soil properties (if include_layers=True)

        Raises:
            FileNotFoundError: If database doesn't exist
            ValueError: If SMU_ID not found in database

        Examples:
            >>> extractor = HWSD2Extractor()
            >>> # This will fail if DB doesn't exist, which is expected
            >>> # In practice, you'd create the DB first with load_hwsd2.py
        """
        if not self.db_path.exists():
            raise FileNotFoundError(
                f"Database not found: {self.db_path}. "
                f"Run load_hwsd2.py to create it first."
            )

        conn = duckdb.connect(str(self.db_path))

        result = {
            'smu_id': smu_id,
        }

        # Get SMU metadata
        if include_metadata:
            smu_query = """
                SELECT
                    s.*,
                    wrb4.VALUE as WRB4_NAME,
                    wrb2.VALUE as WRB2_NAME,
                    d.VALUE as DRAINAGE_NAME,
                    rd.VALUE as ROOT_DEPTH_NAME,
                    k.VALUE as KOPPEN_NAME
                FROM HWSD2_SMU s
                LEFT JOIN D_WRB4 wrb4 ON s.WRB4 = wrb4.CODE
                LEFT JOIN D_WRB2 wrb2 ON s.WRB2 = wrb2.CODE
                LEFT JOIN D_DRAINAGE d ON s.DRAINAGE = d.CODE
                LEFT JOIN D_ROOT_DEPTH rd ON s.ROOT_DEPTH = rd.CODE
                LEFT JOIN D_KOPPEN k ON s.KOPPEN = k.CODE
                WHERE s.HWSD2_SMU_ID = ?
            """
            smu_data = conn.execute(smu_query, [smu_id]).fetchdf()

            if len(smu_data) == 0:
                conn.close()
                raise ValueError(f"SMU_ID {smu_id} not found in database")

            result['metadata'] = smu_data.iloc[0].to_dict()

        # Get layer properties
        if include_layers:
            layers_query = """
                SELECT
                    l.*,
                    d.VALUE as DRAINAGE_NAME,
                    tu.VALUE as TEXTURE_USDA_NAME,
                    ts.VALUE as TEXTURE_SOTER_NAME
                FROM HWSD2_LAYERS l
                LEFT JOIN D_DRAINAGE d ON l.DRAINAGE = d.CODE
                LEFT JOIN D_TEXTURE_USDA tu ON l.TEXTURE_USDA = tu.CODE
                LEFT JOIN D_TEXTURE_SOTER ts ON l.TEXTURE_SOTER = ts.CODE
                WHERE l.HWSD2_SMU_ID = ?
                ORDER BY l.TOPDEP
            """
            layers_data = conn.execute(layers_query, [smu_id]).fetchdf()
            result['layers'] = layers_data

        conn.close()
        return result

    def get_soil_profile(
        self,
        lat: float,
        lon: float,
        include_layers: bool = True,
        include_metadata: bool = True,
    ) -> Optional[Dict]:
        """
        Get complete soil profile for a geographic location.

        This is the main function that combines raster lookup and database query.

        Args:
            lat: Latitude in decimal degrees (-90 to 90)
            lon: Longitude in decimal degrees (-180 to 180)
            include_layers: Include detailed layer properties (default: True)
            include_metadata: Include SMU summary metadata (default: True)

        Returns:
            Dictionary with soil properties, or None if no data at location

        Examples:
            >>> extractor = HWSD2Extractor()
            >>> # Get soil profile for a location
            >>> # (This would work if the database exists)
            >>> # profile = extractor.get_soil_profile(40.0, -105.0)
            >>> # print(profile['layers'][['LAYER', 'TOPDEP', 'BOTDEP', 'CLAY', 'SAND', 'ORG_CARBON']])
        """
        # Get SMU_ID from raster
        smu_id = self.latlon_to_smu_id(lat, lon)

        if smu_id is None:
            return None

        # Get properties from database
        result = self.get_smu_properties(
            smu_id,
            include_layers=include_layers,
            include_metadata=include_metadata,
        )

        # Add location info
        result['latitude'] = lat
        result['longitude'] = lon

        return result


# Convenience functions for quick access
def get_soil_profile(
    lat: float,
    lon: float,
    db_path: Optional[str] = None,
    raster_path: Optional[str] = None,
) -> Optional[Dict]:
    """
    Get soil profile for a location (convenience function).

    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees
        db_path: Path to database (optional, uses default)
        raster_path: Path to raster (optional, uses default)

    Returns:
        Dictionary with soil profile data, or None if no data

    Examples:
        >>> # Get soil profile for Boulder, Colorado
        >>> profile = get_soil_profile(40.0, -105.0)
        >>> if profile:
        ...     print(f"Found soil data: {profile['metadata']['WRB2_NAME']}")
    """
    extractor = HWSD2Extractor(raster_path=raster_path, db_path=db_path)
    return extractor.get_soil_profile(lat, lon)


def get_smu_id(
    lat: float,
    lon: float,
    raster_path: Optional[str] = None,
) -> Optional[int]:
    """
    Get HWSD2_SMU_ID for a location (convenience function).

    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees
        raster_path: Path to raster (optional, uses default)

    Returns:
        HWSD2_SMU_ID, or None if no data

    Examples:
        >>> smu_id = get_smu_id(40.0, -105.0)
        >>> smu_id is None or isinstance(smu_id, int)
        True
    """
    extractor = HWSD2Extractor(raster_path=raster_path, db_path=None)
    return extractor.latlon_to_smu_id(lat, lon)


if __name__ == "__main__":
    import sys

    # Simple CLI for testing
    if len(sys.argv) >= 3:
        lat = float(sys.argv[1])
        lon = float(sys.argv[2])

        print(f"Extracting soil profile for: {lat:.4f}°, {lon:.4f}°")

        extractor = HWSD2Extractor()
        profile = extractor.get_soil_profile(lat, lon)

        if profile is None:
            print("No soil data at this location (ocean or missing data)")
            sys.exit(1)

        print(f"\nSMU_ID: {profile['smu_id']}")
        print(f"Soil Type (WRB): {profile['metadata'].get('WRB2_NAME', 'Unknown')}")
        print(f"Drainage: {profile['metadata'].get('DRAINAGE_NAME', 'Unknown')}")
        print(f"Climate (Köppen): {profile['metadata'].get('KOPPEN_NAME', 'Unknown')}")

        print("\nSoil Profile (7 layers):")
        layers_df = profile['layers'][['LAYER', 'TOPDEP', 'BOTDEP', 'SAND', 'SILT', 'CLAY', 'ORG_CARBON', 'PH_WATER', 'BULK']]
        print(layers_df.to_string(index=False))
    else:
        print("Usage: python hwsd2_extractor.py <latitude> <longitude>")
        print("Example: python hwsd2_extractor.py 40.0 -105.0")
