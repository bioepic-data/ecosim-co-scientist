#!/usr/bin/env python
"""Extract variable metadata from NetCDF files to CSV."""

import csv
import sys
from pathlib import Path
import xarray as xr


def extract_metadata(nc_file: Path) -> list[dict]:
    """
    Extract metadata for all variables in a NetCDF file.

    Args:
        nc_file: Path to NetCDF file

    Returns:
        List of dictionaries containing variable metadata
    """
    ds = xr.open_dataset(nc_file, engine='scipy')

    metadata = []

    # Extract metadata for data variables
    for var_name in ds.data_vars:
        var = ds[var_name]

        # Build metadata dictionary
        var_meta = {
            'variable_name': var_name,
            'dimensions': ', '.join(str(d) for d in var.dims),
            'shape': str(var.shape),
            'dtype': str(var.dtype),
            'ndim': var.ndim,
            'size': var.size,
        }

        # Add all attributes
        for attr_name, attr_value in var.attrs.items():
            var_meta[attr_name] = str(attr_value)

        metadata.append(var_meta)

    ds.close()
    return metadata


def write_metadata_csv(metadata: list[dict], output_file: Path):
    """
    Write metadata to CSV file.

    Args:
        metadata: List of metadata dictionaries
        output_file: Path to output CSV file
    """
    if not metadata:
        print(f"No metadata to write for {output_file}")
        return

    # Get all unique fieldnames across all variables
    fieldnames = set()
    for var_meta in metadata:
        fieldnames.update(var_meta.keys())

    # Sort fieldnames, with standard fields first
    standard_fields = ['variable_name', 'dimensions', 'shape', 'dtype', 'ndim', 'size', 'long_name', 'units']
    sorted_fields = []
    for field in standard_fields:
        if field in fieldnames:
            sorted_fields.append(field)
            fieldnames.remove(field)
    sorted_fields.extend(sorted(fieldnames))

    # Write CSV
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=sorted_fields)
        writer.writeheader()
        writer.writerows(metadata)

    print(f"✓ Wrote metadata to: {output_file}")


def process_netcdf_file(nc_file: Path):
    """
    Process a single NetCDF file and create metadata CSV.

    Args:
        nc_file: Path to NetCDF file
    """
    print(f"\nProcessing: {nc_file.name}")

    # Extract metadata
    metadata = extract_metadata(nc_file)
    print(f"  Found {len(metadata)} variables")

    # Create output CSV filename (same name with .csv extension)
    csv_file = nc_file.with_suffix('.metadata.csv')

    # Write to CSV
    write_metadata_csv(metadata, csv_file)


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # Process files specified on command line
        nc_files = [Path(arg) for arg in sys.argv[1:]]
    else:
        # Process all .nc files in the ecosim-inputs-netcdf directory
        nc_dir = Path("hackathon-case_study-experimental_warming_nitrogen/ecosim-inputs-netcdf")
        nc_files = list(nc_dir.glob("*.nc"))

    if not nc_files:
        print("No NetCDF files found to process")
        sys.exit(1)

    print(f"Processing {len(nc_files)} NetCDF file(s)...")

    for nc_file in nc_files:
        if not nc_file.exists():
            print(f"⨯ File not found: {nc_file}")
            continue

        process_netcdf_file(nc_file)

    print("\n✓ All files processed!")


if __name__ == "__main__":
    main()
