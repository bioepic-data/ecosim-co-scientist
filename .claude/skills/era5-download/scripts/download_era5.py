#!/usr/bin/env python
"""
Flexible ERA5 data downloader using the Copernicus CDS API.

This script provides a reusable interface for downloading ERA5 reanalysis data
with configurable parameters for variables, time ranges, and geographic areas.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

try:
    import cdsapi
except ImportError:
    print("Error: cdsapi not installed. Install with: pip install cdsapi")
    sys.exit(1)


def download_era5(
    variables: List[str],
    start_date: str,
    end_date: str,
    output_file: str,
    area: Optional[List[float]] = None,
    hours: Optional[List[str]] = None,
    pressure_levels: Optional[List[int]] = None,
    data_format: str = "netcdf",
    product_type: str = "reanalysis",
) -> Path:
    """
    Download ERA5 data from the Copernicus Climate Data Store.

    Parameters
    ----------
    variables : List[str]
        ERA5 variable names (e.g., ['2m_temperature', 'total_precipitation'])
    start_date : str
        Start date in format 'YYYY-MM-DD'
    end_date : str
        End date in format 'YYYY-MM-DD'
    output_file : str
        Output file path
    area : Optional[List[float]]
        Geographic bounding box [north, west, south, east] in degrees
        If None, downloads global data
    hours : Optional[List[str]]
        List of hours to download (e.g., ['00:00', '06:00', '12:00', '18:00'])
        If None, downloads all 24 hours
    pressure_levels : Optional[List[int]]
        Pressure levels in hPa for pressure-level data
        If None, uses single-level data
    data_format : str
        Output format: 'netcdf' or 'grib'
    product_type : str
        Product type: 'reanalysis' or 'ensemble_members'

    Returns
    -------
    Path
        Path to downloaded file
    """
    # Parse dates
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    # Generate year, month, day lists
    years = sorted(list(set(range(start.year, end.year + 1))))
    months = [f"{m:02d}" for m in range(1, 13)]
    days = [f"{d:02d}" for d in range(1, 32)]

    # Default to all hours if not specified
    if hours is None:
        hours = [f"{h:02d}:00" for h in range(24)]

    # Build request parameters
    request_params = {
        "product_type": product_type,
        "variable": variables,
        "year": [str(y) for y in years],
        "month": months,
        "day": days,
        "time": hours,
        "format": data_format,
    }

    # Add area constraint if specified
    if area is not None:
        request_params["area"] = area

    # Determine dataset based on pressure levels
    if pressure_levels is not None:
        dataset = "reanalysis-era5-pressure-levels"
        request_params["pressure_level"] = pressure_levels
    else:
        dataset = "reanalysis-era5-single-levels"

    # Create client and download
    print(f"Initializing CDS API client...")
    client = cdsapi.Client()

    print(f"\nRequesting ERA5 {dataset}...")
    print(f"  Variables: {', '.join(variables)}")
    print(f"  Date range: {start_date} to {end_date}")
    print(f"  Hours: {len(hours)} per day")
    if area:
        print(f"  Area: {area[0]}°N to {area[2]}°N, {area[1]}°E to {area[3]}°E")
    else:
        print(f"  Area: Global")
    if pressure_levels:
        print(f"  Pressure levels: {pressure_levels} hPa")
    print(f"  Format: {data_format}")

    result = client.retrieve(dataset, request_params)

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\nDownloading to: {output_path}")
    result.download(str(output_path))

    file_size = output_path.stat().st_size
    print(f"✓ Download complete!")
    print(f"  File size: {file_size / 1024:.1f} KB")
    print(f"  Location: {output_path}")

    return output_path


def main():
    """Command-line interface for ERA5 downloads."""
    parser = argparse.ArgumentParser(
        description="Download ERA5 reanalysis data from Copernicus CDS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download 2m temperature for Jan 2023, global
  python download_era5.py -v 2m_temperature -s 2023-01-01 -e 2023-01-31 -o temp.nc

  # Download multiple variables for a region
  python download_era5.py -v 2m_temperature total_precipitation \\
    -s 2023-01-01 -e 2023-01-02 \\
    -a 46 -123 44 -121 \\
    -o pacific_nw.nc

  # Download 6-hourly data at specific pressure levels
  python download_era5.py -v temperature geopotential \\
    -s 2023-01-01 -e 2023-01-01 \\
    --hours 00:00 06:00 12:00 18:00 \\
    --pressure-levels 1000 850 500 \\
    -o upper_air.nc
        """,
    )

    parser.add_argument(
        "-v",
        "--variables",
        nargs="+",
        required=True,
        help="ERA5 variable names (e.g., 2m_temperature total_precipitation)",
    )
    parser.add_argument(
        "-s", "--start-date", required=True, help="Start date (YYYY-MM-DD)"
    )
    parser.add_argument("-e", "--end-date", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument(
        "-o", "--output", required=True, help="Output file path (e.g., output.nc)"
    )
    parser.add_argument(
        "-a",
        "--area",
        nargs=4,
        type=float,
        metavar=("NORTH", "WEST", "SOUTH", "EAST"),
        help="Geographic bounding box in degrees (north west south east)",
    )
    parser.add_argument(
        "--hours",
        nargs="+",
        help="Hours to download (e.g., 00:00 06:00 12:00 18:00). Default: all 24 hours",
    )
    parser.add_argument(
        "--pressure-levels",
        nargs="+",
        type=int,
        help="Pressure levels in hPa for 3D data (e.g., 1000 850 500)",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["netcdf", "grib"],
        default="netcdf",
        help="Output format (default: netcdf)",
    )

    args = parser.parse_args()

    try:
        download_era5(
            variables=args.variables,
            start_date=args.start_date,
            end_date=args.end_date,
            output_file=args.output,
            area=args.area,
            hours=args.hours,
            pressure_levels=args.pressure_levels,
            data_format=args.format,
        )
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
