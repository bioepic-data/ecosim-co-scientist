#!/usr/bin/env python
"""Test script to convert CDL to NetCDF and read with xarray."""

import subprocess
from pathlib import Path
import xarray as xr

# Directory containing CDL files
cdl_dir = Path("hackathon-case_study-experimental_warming_nitrogen/ecosim-inputs-netcdf")

# Find a small CDL file to test with
cdl_file = cdl_dir / "Blodget_grid_20240622.nc.cdl"
print(f"Testing with: {cdl_file}")

# Convert CDL to NetCDF using ncgen
nc_file = cdl_file.with_suffix("").with_suffix(".nc")  # Remove .cdl, keep .nc
print(f"Converting to: {nc_file}")

try:
    subprocess.run(
        ["ncgen", "-o", str(nc_file), str(cdl_file)],
        check=True,
        capture_output=True,
        text=True
    )
    print("✓ Conversion successful")
except subprocess.CalledProcessError as e:
    print(f"✗ Conversion failed: {e}")
    print(f"stderr: {e.stderr}")
    exit(1)
except FileNotFoundError:
    print("✗ ncgen not found. You may need to install netcdf tools:")
    print("  brew install netcdf  # on macOS")
    print("  apt install netcdf-bin  # on Ubuntu/Debian")
    exit(1)

# Now read with xarray
print(f"\nReading with xarray (using scipy engine for NetCDF3)...")
ds = xr.open_dataset(nc_file, engine='scipy')

print("\n" + "="*60)
print("Dataset Overview:")
print("="*60)
print(ds)

print("\n" + "="*60)
print("Dimensions:")
print("="*60)
for dim, size in ds.dims.items():
    print(f"  {dim}: {size}")

print("\n" + "="*60)
print("Variables:")
print("="*60)
for var in ds.data_vars:
    print(f"  {var}: {ds[var].dims}, {ds[var].dtype}")
    if hasattr(ds[var], 'long_name'):
        print(f"    → {ds[var].long_name}")

print("\n" + "="*60)
print("Sample Data (first few variables):")
print("="*60)
for i, var in enumerate(list(ds.data_vars)[:3]):
    print(f"\n{var}:")
    print(ds[var].values)

# Close the dataset
ds.close()

print("\n✓ Test completed successfully!")
