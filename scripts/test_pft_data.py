#!/usr/bin/env python
"""Test script to explore plant functional type parameters."""

from pathlib import Path
import xarray as xr

nc_file = Path("hackathon-case_study-experimental_warming_nitrogen/ecosim-inputs-netcdf/ecosim_pftpar_20240723.nc")

print(f"Reading PFT parameters from: {nc_file.name}")
ds = xr.open_dataset(nc_file, engine='scipy')

print("\n" + "="*60)
print("Dataset Overview:")
print("="*60)
print(ds)

print("\n" + "="*60)
print("Plant Functional Types:")
print("="*60)
print(f"Number of PFTs: {ds.dims.get('pft', 'N/A')}")

# Show PFT names if available
if 'pft_name' in ds.data_vars:
    print("\nPFT Names:")
    for i, name in enumerate(ds['pft_name'].values[:10]):  # First 10
        print(f"  {i}: {name}")

print("\n" + "="*60)
print("Sample Parameters (first 10):")
print("="*60)
for var in list(ds.data_vars)[:10]:
    print(f"\n{var}: {ds[var].dims}, shape={ds[var].shape}")
    if hasattr(ds[var], 'long_name'):
        print(f"  → {ds[var].long_name}")
    if hasattr(ds[var], 'units'):
        print(f"  → units: {ds[var].units}")
    # Show first few values
    if len(ds[var].shape) == 1 and ds[var].shape[0] <= 5:
        print(f"  → values: {ds[var].values}")

ds.close()
print("\n✓ PFT data test completed successfully!")
