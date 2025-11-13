#!/usr/bin/env python3
"""End-to-end NetCDF file generation for experimental warming sites.

This script generates complete EcoSIM input file sets (grid, climate, PFT)
for selected Tier 1 sites.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ecosim_co_scientist.data_models import EcosystemType
from ecosim_co_scientist.netcdf_generators import create_climate_file, create_grid_file
from ecosim_co_scientist.parsers import load_experiment_metadata
from ecosim_co_scientist.pft_mapper import create_pft_file, map_ecosystem_to_pft
from ecosim_co_scientist.soil_properties import create_ecosystem_default_profile


def generate_site_files(site, output_dir: Path, start_year: int = 2010, n_years: int = 2):
    """Generate all NetCDF files for a single site.

    Args:
        site: ExperimentalSite object
        output_dir: Output directory
        start_year: Starting year for climate data
        n_years: Number of years to generate

    Returns:
        Dictionary of generated file paths
    """
    # Create site-specific subdirectory
    site_id = site.source_id.split()[0].replace(" ", "_").replace(".", "")
    site_dir = output_dir / site_id
    site_dir.mkdir(parents=True, exist_ok=True)

    print()
    print("=" * 100)
    print(f"GENERATING FILES FOR: {site.source_id[:80]}")
    print("=" * 100)
    print(f"Location: {site.location_text[:80]}")
    if site.coordinates:
        print(f"Coordinates: {site.coordinates.latitude:.4f}°, {site.coordinates.longitude:.4f}°")
    print(f"Ecosystem: {site.ecosystem_text}")
    print(f"Warming: +{site.temperature_increase_c:.2f}°C")
    print()

    files = {}

    # 1. Generate soil profile
    print("1. Creating soil profile...")
    if site.ecosystem:
        soil_profile = create_ecosystem_default_profile(site.ecosystem, site, n_layers=20)
    else:
        # Use grassland as default
        soil_profile = create_ecosystem_default_profile(
            EcosystemType.GRASSLAND_MEADOW_PRAIRIE, site, n_layers=20
        )
    print(f"   ✓ Created {len(soil_profile.layers)}-layer soil profile")
    print()

    # 2. Generate grid file
    print("2. Generating grid/soil NetCDF file...")
    grid_file = site_dir / f"{site_id}_grid.nc"
    files["grid"] = create_grid_file(site, soil_profile, grid_file)
    print()

    # 3. Generate control climate file
    print("3. Generating CONTROL climate NetCDF file...")
    control_clim_file = site_dir / f"{site_id}_clim_{start_year}-{start_year+n_years-1}_control.nc"
    files["climate_control"] = create_climate_file(
        site, control_clim_file, start_year=start_year, n_years=n_years, apply_warming=False
    )
    print()

    # 4. Generate treatment climate file
    print("4. Generating TREATMENT climate NetCDF file...")
    treatment_clim_file = site_dir / f"{site_id}_clim_{start_year}-{start_year+n_years-1}_treatment.nc"
    files["climate_treatment"] = create_climate_file(
        site, treatment_clim_file, start_year=start_year, n_years=n_years, apply_warming=True
    )
    print()

    # 5. Generate PFT file
    print("5. Generating PFT NetCDF file...")
    if site.ecosystem:
        pft_code = map_ecosystem_to_pft(site.ecosystem)
    else:
        pft_code = map_ecosystem_to_pft(EcosystemType.GRASSLAND_MEADOW_PRAIRIE)

    pft_file = site_dir / f"{site_id}_pft.{pft_code.code}.nc"
    files["pft"] = create_pft_file(site, pft_code, pft_file, start_year=start_year, n_years=n_years)
    print()

    # Summary
    print("=" * 100)
    print(f"COMPLETED: {site_id}")
    print("=" * 100)
    print("Files generated:")
    for file_type, file_path in files.items():
        size_mb = file_path.stat().st_size / (1024 * 1024)
        print(f"  • {file_type:20s}: {file_path.name:50s} ({size_mb:.2f} MB)")
    print()

    return files


def main():
    """Generate NetCDF files for Tier 1 sites."""
    # Load site metadata
    data_dir = (
        Path(__file__).parent.parent
        / "hackathon-case_study-experimental_warming_nitrogen"
        / "derived"
    )
    metadata_file = data_dir / "experiment-metadata.tsv"

    print()
    print("╔" + "=" * 98 + "╗")
    print("║" + " " * 98 + "║")
    print("║" + "  ECOSIM NETCDF FILE GENERATOR - END-TO-END PIPELINE".center(98) + "║")
    print("║" + " " * 98 + "║")
    print("╚" + "=" * 98 + "╝")
    print()

    print("Loading experimental sites...")
    inventory = load_experiment_metadata(metadata_file)
    print(f"  ✓ Loaded {inventory.n_sites} total sites")

    # Filter to sites with complete metadata
    tier1_sites = [
        s
        for s in inventory.sites
        if s.coordinates and s.temperature_increase_c and s.warming_duration_months and s.ecosystem
    ]

    print(f"  ✓ Found {len(tier1_sites)} sites with complete metadata")
    print()

    # Select pilot sites (top 3 for demo)
    pilot_sites = tier1_sites[:3]

    print(f"Generating files for {len(pilot_sites)} pilot sites...")
    print()

    # Output directory
    output_dir = Path(__file__).parent.parent / "output" / "netcdf_files"

    # Generate files for each site
    all_files = {}
    for i, site in enumerate(pilot_sites, 1):
        print(f"\n{'#' * 100}")
        print(f"SITE {i} OF {len(pilot_sites)}")
        print(f"{'#' * 100}")

        site_files = generate_site_files(site, output_dir, start_year=2010, n_years=2)
        all_files[site.source_id] = site_files

    # Final summary
    print()
    print("╔" + "=" * 98 + "╗")
    print("║" + " " * 98 + "║")
    print("║" + "  GENERATION COMPLETE".center(98) + "║")
    print("║" + " " * 98 + "║")
    print("╚" + "=" * 98 + "╝")
    print()

    print(f"Generated NetCDF files for {len(pilot_sites)} sites")
    print(f"Output directory: {output_dir}")
    print()

    total_files = sum(len(files) for files in all_files.values())
    print(f"Total files created: {total_files}")
    print()

    print("File breakdown per site:")
    print("  • 1 grid/soil file (initial conditions, soil properties)")
    print("  • 1 control climate file (unmodified)")
    print("  • 1 treatment climate file (with warming offset)")
    print("  • 1 PFT file (vegetation type)")
    print("  = 5 files per site")
    print()

    print("Next steps:")
    print("  1. Inspect NetCDF files with: ncdump -h <file>")
    print("  2. Validate file structure against Blodget templates")
    print("  3. Run EcoSIM model with generated inputs")
    print("  4. Compare model output to experimental measurements")
    print()

    print("Sites processed:")
    for i, (source_id, files) in enumerate(all_files.items(), 1):
        print(f"  {i}. {source_id[:70]}")
        print(f"     → {len(files)} files in {list(files.values())[0].parent}")
    print()


if __name__ == "__main__":
    main()
