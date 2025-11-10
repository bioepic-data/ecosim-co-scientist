#!/usr/bin/env python
"""Test script to read and explore the climate NetCDF file."""

import subprocess
from pathlib import Path
import xarray as xr

# Directory containing CDL files
cdl_dir = Path("hackathon-case_study-experimental_warming_nitrogen/ecosim-inputs-netcdf")

# Convert and read the climate data file
cdl_file = cdl_dir / "Blodget.clim.2012-2022.nc.cdl"
nc_file = cdl_file.with_suffix("").with_suffix(".nc")

print(f"Testing with climate data: {cdl_file.name}")

# Convert if needed
if not nc_file.exists():
    print(f"Converting to: {nc_file}")
    subprocess.run(
        ["ncgen", "-o", str(nc_file), str(cdl_file)],
        check=True,
        capture_output=True
    )
    print("✓ Conversion successful")
else:
    print(f"Using existing file: {nc_file}")

# Read with xarray
print(f"\nReading with xarray...")
ds = xr.open_dataset(nc_file, engine='scipy')

print("\n" + "="*60)
print("Dataset Overview:")
print("="*60)
print(ds)

print("\n" + "="*60)
print("Time Range:")
print("="*60)
if 'time' in ds.coords or 'time' in ds.dims:
    time_var = ds['time'] if 'time' in ds.data_vars else None
    if time_var is not None:
        print(f"  Start: {time_var[0].values}")
        print(f"  End: {time_var[-1].values}")
        print(f"  N timesteps: {len(time_var)}")

print("\n" + "="*60)
print("Climate Variables:")
print("="*60)
for var in list(ds.data_vars)[:10]:  # Show first 10
    print(f"  {var}: {ds[var].dims}, shape={ds[var].shape}")
    if hasattr(ds[var], 'long_name'):
        print(f"    → {ds[var].long_name}")
    if hasattr(ds[var], 'units'):
        print(f"    → units: {ds[var].units}")

print("\n" + "="*60)
print("Sample Temperature Data (first 5 timesteps):")
print("="*60)
# Find a temperature variable
temp_vars = [v for v in ds.data_vars if 'temp' in v.lower() or 'tair' in v.lower()]
if temp_vars:
    temp_var = temp_vars[0]
    print(f"\n{temp_var}:")
    print(ds[temp_var][:5].values)

ds.close()
print("\n✓ Climate data test completed successfully!")
