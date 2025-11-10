#!/usr/bin/env python
"""
Download ERA5 surface pressure data for a small test region and time range.

This script demonstrates using cdsapi to retrieve ERA5 reanalysis data
from the Copernicus Climate Data Store (CDS).
"""

import cdsapi
from pathlib import Path

def download_surface_pressure():
    """
    Download ERA5 surface pressure for a small region and short time period.

    Downloads 2 days of hourly surface pressure data for a small area
    around 45°N, 122°W (Pacific Northwest region).

    Output saved to: era5_surface_pressure_test.nc
    """
    # Create output directory if it doesn't exist
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "era5_surface_pressure_test.nc"

    print("Initializing CDS API client...")
    client = cdsapi.Client()

    print("Requesting ERA5 surface pressure data...")
    print("  Variable: Surface pressure")
    print("  Date range: 2023-01-01 to 2023-01-02")
    print("  Time: All hours (00:00-23:00)")
    print("  Area: 46°N to 44°N, -123°W to -121°W")
    print("  Format: NetCDF")

    result = client.retrieve(
        "reanalysis-era5-single-levels",
        {
            "product_type": "reanalysis",
            "variable": "surface_pressure",
            "year": "2023",
            "month": "01",
            "day": ["01", "02"],
            "time": [
                "00:00", "01:00", "02:00", "03:00", "04:00", "05:00",
                "06:00", "07:00", "08:00", "09:00", "10:00", "11:00",
                "12:00", "13:00", "14:00", "15:00", "16:00", "17:00",
                "18:00", "19:00", "20:00", "21:00", "22:00", "23:00",
            ],
            "area": [46, -123, 44, -121],  # North, West, South, East
            "format": "netcdf",
        },
    )

    print(f"\nDownloading to: {output_file}")
    result.download(str(output_file))

    print(f"✓ Download complete!")
    print(f"  File size: {output_file.stat().st_size / 1024:.1f} KB")
    print(f"  Location: {output_file}")

    return output_file


if __name__ == "__main__":
    download_surface_pressure()
