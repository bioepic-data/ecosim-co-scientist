#!/usr/bin/env python3
"""Complete pipeline for generating EcoSIM NetCDF files from experimental sites.

This script demonstrates the full workflow:
1. Load Tier 1 site metadata
2. Create ERA5 download requests
3. Apply warming treatments
4. Generate EcoSIM-formatted climate files
5. (Future) Add soil and PFT data

Note: Actual ERA5 downloads require CDS API credentials in ~/.cdsapirc
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ecosim_co_scientist.parsers import load_experiment_metadata


def main():
    """Demonstrate NetCDF generation pipeline."""
    print("=" * 100)
    print("ECOSIM NETCDF GENERATION PIPELINE - Phase 2 Demonstration")
    print("=" * 100)
    print()

    # Load Tier 1 sites
    data_dir = (
        Path(__file__).parent.parent
        / "hackathon-case_study-experimental_warming_nitrogen"
        / "derived"
    )
    metadata_file = data_dir / "experiment-metadata.tsv"

    print("Step 1: Loading Tier 1 site metadata...")
    inventory = load_experiment_metadata(metadata_file)

    # Filter to sites with complete metadata
    tier1_sites = [
        s
        for s in inventory.sites
        if s.coordinates
        and s.temperature_increase_c
        and s.warming_duration_months
    ][:5]  # Take top 5 for demo

    print(f"  ✓ Loaded {len(tier1_sites)} Tier 1 sites with complete metadata")
    print()

    # Show ERA5 download requirements
    print("Step 2: ERA5 Climate Data Requirements")
    print("-" * 100)
    print()

    from ecosim_co_scientist.era5_downloader import create_request_from_site

    output_dir = Path(__file__).parent.parent / "output" / "era5_data"

    for i, site in enumerate(tier1_sites, 1):
        print(f"{i}. {site.source_id[:70]}")

        # Create ERA5 request
        request = create_request_from_site(site, output_dir, reference_year=2010)

        if request:
            print(f"   Location: {request.latitude:.4f}°, {request.longitude:.4f}°")
            print(f"   Period  : {request.start_date.date()} to {request.end_date.date()}")
            print(f"   Years   : {', '.join(request.year_range)}")
            print(f"   BBox    : N={request.bounding_box[0]:.2f}, S={request.bounding_box[2]:.2f}, " +
                  f"E={request.bounding_box[3]:.2f}, W={request.bounding_box[1]:.2f}")
            print(f"   Variables: {len(request.variables)} (T, wind, precip, solar, dewpoint)")
            print(f"   Warming : +{site.temperature_increase_c:.2f}°C treatment")
            print(f"   Output  : {request.output_path.name}")
        else:
            print(f"   ⚠ Insufficient metadata for ERA5 request")
        print()

    # Show NetCDF file structure
    print()
    print("Step 3: NetCDF File Structure for Each Site")
    print("-" * 100)
    print()

    print("Three files will be generated per site:")
    print()
    print("A. Grid/Soil File ({site}_grid.nc):")
    print("   Dimensions: ngrid=1, ntopou=1, nlevs=20")
    print("   Variables:")
    print("     • Coordinates: ALATG (latitude), ALTIG (altitude)")
    print("     • Soil layers: CDPTH (depth), BKDSI (bulk density), CSAND/CSILT (texture)")
    print("     • Chemistry  : PH, CEC, AEC, CNH4, CNO3, CORGC, CORGN")
    print("     • Physics    : FC (field capacity), WP (wilting point), SCNV (Ksat)")
    print("     • Atmosphere : CO2EIG, Z2OEG, CH4EG, ZNH3EG")
    print()

    print("B. Climate File ({site}_clim_{years}.nc):")
    print("   Dimensions: year, day=366, hour=24, ngrid=1")
    print("   Variables:")
    print("     • TMPH  : Hourly air temperature (°C) - WITH WARMING OFFSET FOR TREATMENT")
    print("     • WINDH : Horizontal wind speed (m/s)")
    print("     • RAINH : Total precipitation (mm/hr)")
    print("     • SRADH : Solar radiation (W/m²)")
    print("     • DWPTH : Vapor pressure (kPa)")
    print("     • Annual precip chemistry (NH4, NO3, PO4, pH)")
    print()
    print("   Two versions:")
    print("     - Control   : ERA5 data unmodified")
    print("     - Treatment : ERA5 data + temperature offset")
    print()

    print("C. Plant Functional Type File ({site}_pft.{PFT}.nc):")
    print("   Dimensions: year, ntopou=1, maxpfts")
    print("   Variables:")
    print("     • pft_type   : Vegetation type (mapped from ecosystem)")
    print("     • pft_pltinfo: Planting information")
    print("     • nmgnts     : Management events")
    print()

    # Data sources
    print()
    print("Step 4: Data Source Mapping")
    print("-" * 100)
    print()

    print("Climate Data:")
    print("  • Source: ERA5 reanalysis (Copernicus Climate Data Store)")
    print("  • Download: cdsapi Python client (requires free CDS account)")
    print("  • Temporal: Hourly, all years needed for experiment duration")
    print("  • Spatial : 0.25° resolution, small bbox around site coordinates")
    print()

    print("Soil Data:")
    print("  • Source: HWSD v2 (Harmonized World Soil Database)")
    print("  • Query : By latitude/longitude of experimental site")
    print("  • Layers: Texture, pH, organic C, bulk density by depth")
    print("  • Augment: Site-specific measurements from papers where available")
    print()

    print("Plant Traits:")
    print("  • Source: plant_traits.json database in this repo")
    print("  • Mapping: Ecosystem type → EcoSIM PFT code")
    print("  • Params : SLA, Vcmax, Jmax, root hydraulics, etc.")
    print()

    print("Nitrogen Pools (Initial Conditions):")
    print("  • Source: N_measurements.tsv (control plot values)")
    print("  • Variables: Soil NH4, NO3, organic N pools")
    print("  • Gap-fill: Ecosystem-type averages from literature")
    print()

    # Example workflow
    print()
    print("Step 5: Example Workflow (Pseudocode)")
    print("-" * 100)
    print()

    print("""
# For each Tier 1 site:

1. Download ERA5 climate data
   → era5_downloader.download_era5_data(request)
   → Outputs: site_era5_2010.nc

2. Create control climate file
   → era5_downloader.convert_era5_to_ecosim_format(era5_file, control_file)
   → Outputs: site_clim_2010_control.nc

3. Create treatment climate file
   → era5_downloader.apply_warming_treatment(control_file, warming_c, treatment_file)
   → Outputs: site_clim_2010_treatment.nc

4. Query HWSD for soil properties
   → hwsd_query.get_soil_profile(latitude, longitude)
   → Returns: texture, pH, organic C, bulk density by layer

5. Generate grid/soil NetCDF
   → netcdf_generator.create_grid_file(site, soil_profile, grid_file)
   → Outputs: site_grid.nc

6. Map ecosystem to PFT
   → pft_mapper.ecosystem_to_pft(ecosystem_text)
   → Returns: EcoSIM PFT code(s)

7. Generate PFT NetCDF
   → netcdf_generator.create_pft_file(site, pft_codes, pft_file)
   → Outputs: site_pft.ENF.nc (or appropriate PFT)

8. Validate NetCDF files
   → validator.check_dimensions(grid_file, clim_file, pft_file)
   → validator.check_variable_ranges(grid_file, clim_file)
   → validator.compare_with_template(grid_file, "Blodget_grid.nc")
    """)

    # Summary
    print()
    print("=" * 100)
    print("SUMMARY - Files to Generate")
    print("=" * 100)
    print()

    print(f"For {len(tier1_sites)} Tier 1 sites:")
    print(f"  • {len(tier1_sites)} grid/soil files (site_grid.nc)")
    print(f"  • {len(tier1_sites) * 2} climate files (control + treatment)")
    print(f"  • {len(tier1_sites)} PFT files (site_pft.nc)")
    print(f"  • Total: {len(tier1_sites) * 4} NetCDF files")
    print()

    print("Next Implementation Steps:")
    print("  1. ✓ Phase 1: Data extraction & harmonization (COMPLETE)")
    print("  2. ✓ Tier 1 site selection (COMPLETE)")
    print("  3. ✓ ERA5 downloader module (COMPLETE)")
    print("  4. ⧗ HWSD soil query module (IN PROGRESS)")
    print("  5. ⧗ NetCDF file generators (IN PROGRESS)")
    print("  6. ⧗ PFT mapping logic (PENDING)")
    print("  7. ⧗ Validation framework (PENDING)")
    print("  8. ⧗ EcoSIM model testing (PENDING)")
    print()


if __name__ == "__main__":
    main()
