#!/usr/bin/env python3
"""Load and analyze the warming-nitrogen meta-analysis data.

This script demonstrates Phase 1 of the NetCDF generation pipeline:
- Loads experimental site metadata
- Loads nitrogen measurements
- Links measurements to sites
- Generates summary statistics
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ecosim_co_scientist.parsers import (
    load_experiment_metadata,
    load_nitrogen_measurements,
)


def main():
    """Load and analyze warming-nitrogen data."""
    # Define data paths
    data_dir = Path(__file__).parent.parent / "hackathon-case_study-experimental_warming_nitrogen" / "derived"

    metadata_file = data_dir / "experiment-metadata.tsv"
    measurements_file = data_dir / "N_measurements.tsv"

    print("=" * 80)
    print("EXPERIMENTAL WARMING NITROGEN CYCLE DATA LOADER")
    print("=" * 80)
    print()

    # Load site metadata
    print(f"Loading experimental sites from: {metadata_file.name}")
    inventory = load_experiment_metadata(metadata_file)
    print(f"  ✓ Loaded {inventory.n_sites} experimental sites")
    print(f"  ✓ {len(inventory.sites_with_coordinates)} sites have coordinates")
    print()

    # Group by ecosystem
    by_ecosystem = inventory.by_ecosystem()
    print("Sites by ecosystem type:")
    for ecosystem, sites in sorted(by_ecosystem.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  • {ecosystem.value:30s} : {len(sites):2d} sites")
    print()

    # Warming method distribution
    warming_methods = {}
    for site in inventory.sites:
        if site.warming_method:
            method = site.warming_method.value
            warming_methods[method] = warming_methods.get(method, 0) + 1

    print("Sites by warming method:")
    for method, count in sorted(warming_methods.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {method:30s} : {count:2d} sites")
    print()

    # Temperature increase statistics
    temp_increases = [
        s.temperature_increase_c
        for s in inventory.sites
        if s.temperature_increase_c is not None
    ]
    if temp_increases:
        print("Temperature increase statistics:")
        print(f"  • Mean    : {sum(temp_increases) / len(temp_increases):.2f}°C")
        print(f"  • Minimum : {min(temp_increases):.2f}°C")
        print(f"  • Maximum : {max(temp_increases):.2f}°C")
        print(f"  • N sites : {len(temp_increases)}")
    print()

    # Load nitrogen measurements
    print(f"Loading nitrogen measurements from: {measurements_file.name}")
    measurements = load_nitrogen_measurements(measurements_file)
    print(f"  ✓ Loaded {len(measurements)} nitrogen cycle measurements")
    print()

    # Group measurements by variable type
    by_variable = {}
    for meas in measurements:
        var_name = meas.variable.value
        if var_name not in by_variable:
            by_variable[var_name] = []
        by_variable[var_name].append(meas)

    print("Measurements by nitrogen variable:")
    for var_name, meas_list in sorted(by_variable.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  • {var_name:30s} : {len(meas_list):3d} measurements")
    print()

    # Link measurements to sites
    site_source_ids = {site.source_id for site in inventory.sites}
    linked_measurements = [
        m for m in measurements if m.source_id in site_source_ids
    ]
    print(f"Linked measurements to sites:")
    print(f"  • {len(linked_measurements)} measurements linked to {len(site_source_ids)} sites")
    print(f"  • {len(measurements) - len(linked_measurements)} measurements from sites not in metadata")
    print()

    # Warming effect statistics for N2O (most common)
    n2o_measurements = [m for m in measurements if m.variable.value == "N2O"]
    if n2o_measurements:
        print("N2O flux warming effects:")
        positive_effects = [m for m in n2o_measurements if m.warming_effect > 0]
        negative_effects = [m for m in n2o_measurements if m.warming_effect < 0]
        print(f"  • Increased with warming: {len(positive_effects)} ({len(positive_effects)/len(n2o_measurements)*100:.1f}%)")
        print(f"  • Decreased with warming: {len(negative_effects)} ({len(negative_effects)/len(n2o_measurements)*100:.1f}%)")

        # Calculate mean effect
        effects = [m.warming_effect for m in n2o_measurements]
        print(f"  • Mean warming effect   : {sum(effects)/len(effects):.3f} (treatment - control)")
    print()

    # Sites ready for NetCDF generation
    ready_sites = [
        s for s in inventory.sites
        if s.coordinates is not None
        and s.temperature_increase_c is not None
        and s.warming_duration_months is not None
    ]
    print("Sites ready for NetCDF generation:")
    print(f"  • {len(ready_sites)} sites have complete metadata (coordinates, temperature, duration)")
    print(f"  • Tier 1 priority sites (well-documented): ~10-15 sites recommended")
    print()

    # Sample site details
    if ready_sites:
        print("Example site with complete metadata:")
        site = ready_sites[0]
        print(f"  • Study      : {site.source_id[:60]}")
        print(f"  • Location   : {site.location_text[:60]}")
        print(f"  • Coordinates: {site.coordinates.latitude:.2f}°, {site.coordinates.longitude:.2f}°")
        print(f"  • Ecosystem  : {site.ecosystem_text}")
        print(f"  • Warming    : +{site.temperature_increase_c:.2f}°C via {site.warming_method_text[:40]}")
        if site.warming_duration_months:
            print(f"  • Duration   : {site.max_warming_duration_months} months (max)")

    print()
    print("=" * 80)
    print("NEXT STEPS:")
    print("  1. Select Tier 1 sites (10-15 with best documentation)")
    print("  2. Download ERA5 climate data for each site")
    print("  3. Query HWSD for soil properties")
    print("  4. Generate NetCDF files")
    print("=" * 80)


if __name__ == "__main__":
    main()
