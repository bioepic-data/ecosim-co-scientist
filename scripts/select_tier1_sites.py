#!/usr/bin/env python3
"""Select Tier 1 sites for NetCDF generation.

This script prioritizes experimental sites based on:
- Complete metadata (coordinates, temperature, duration)
- Multiple nitrogen cycle measurements
- Ecosystem diversity
- Data quality and documentation
"""

import sys
from collections import defaultdict
from pathlib import Path
from typing import NamedTuple

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ecosim_co_scientist.data_models import ExperimentalSite
from ecosim_co_scientist.parsers import (
    load_experiment_metadata,
    load_nitrogen_measurements,
)


class SiteScore(NamedTuple):
    """Score for prioritizing sites."""

    site: ExperimentalSite
    n_measurements: int
    n_variables: int
    metadata_score: int
    total_score: float

    def __str__(self) -> str:
        """Format site score for display."""
        return (
            f"{self.site.source_id[:60]:60s} | "
            f"Score: {self.total_score:5.1f} | "
            f"Meas: {self.n_measurements:2d} ({self.n_variables} vars) | "
            f"Meta: {self.metadata_score}/5"
        )


def score_site_metadata(site: ExperimentalSite) -> int:
    """Score site based on metadata completeness (0-5).

    Criteria:
    - Has coordinates: +1
    - Has temperature increase: +1
    - Has duration information: +1
    - Has ecosystem classification: +1
    - Has warming method: +1

    Args:
        site: Site to score

    Returns:
        Score from 0 to 5
    """
    score = 0
    if site.coordinates is not None:
        score += 1
    if site.temperature_increase_c is not None:
        score += 1
    if site.warming_duration_months is not None:
        score += 1
    if site.ecosystem is not None:
        score += 1
    if site.warming_method is not None:
        score += 1
    return score


def select_tier1_sites(
    inventory,
    measurements,
    target_count: int = 12,
    min_score: float = 5.0,
) -> list[SiteScore]:
    """Select top Tier 1 sites for NetCDF generation.

    Args:
        inventory: SiteInventory with all sites
        measurements: List of nitrogen measurements
        target_count: Target number of sites to select
        min_score: Minimum total score required

    Returns:
        List of SiteScore objects, sorted by score descending
    """
    # Count measurements per source
    meas_by_source = defaultdict(list)
    for meas in measurements:
        meas_by_source[meas.source_id].append(meas)

    # Score each site
    site_scores = []
    for site in inventory.sites:
        # Get measurements for this site
        site_meas = meas_by_source.get(site.source_id, [])
        n_measurements = len(site_meas)
        n_variables = len(set(m.variable for m in site_meas))

        # Score metadata
        metadata_score = score_site_metadata(site)

        # Calculate total score
        # Weight: metadata (5 points) + measurements (2 points each) + unique vars (3 points each)
        total_score = metadata_score + (n_measurements * 2) + (n_variables * 3)

        site_scores.append(
            SiteScore(
                site=site,
                n_measurements=n_measurements,
                n_variables=n_variables,
                metadata_score=metadata_score,
                total_score=total_score,
            )
        )

    # Sort by score descending
    site_scores.sort(key=lambda s: s.total_score, reverse=True)

    # Filter by minimum score
    site_scores = [s for s in site_scores if s.total_score >= min_score]

    return site_scores[:target_count]


def ensure_ecosystem_diversity(
    scored_sites: list[SiteScore], min_per_ecosystem: int = 2
) -> list[SiteScore]:
    """Ensure representation across ecosystem types.

    Args:
        scored_sites: List of scored sites
        min_per_ecosystem: Minimum sites per ecosystem type

    Returns:
        Reordered list with ecosystem diversity
    """
    selected = []
    by_ecosystem = defaultdict(list)

    # Group by ecosystem
    for ss in scored_sites:
        if ss.site.ecosystem:
            by_ecosystem[ss.site.ecosystem].append(ss)

    # First pass: ensure min representation
    for ecosystem, sites in by_ecosystem.items():
        # Take top N per ecosystem
        for site in sorted(sites, key=lambda s: s.total_score, reverse=True)[
            :min_per_ecosystem
        ]:
            if site not in selected:
                selected.append(site)

    # Second pass: add remaining high-scoring sites
    for ss in scored_sites:
        if ss not in selected:
            selected.append(ss)

    return selected


def main():
    """Select Tier 1 sites."""
    # Define data paths
    data_dir = (
        Path(__file__).parent.parent
        / "hackathon-case_study-experimental_warming_nitrogen"
        / "derived"
    )

    metadata_file = data_dir / "experiment-metadata.tsv"
    measurements_file = data_dir / "N_measurements.tsv"

    print("=" * 120)
    print("TIER 1 SITE SELECTION FOR NETCDF GENERATION")
    print("=" * 120)
    print()

    # Load data
    print("Loading data...")
    inventory = load_experiment_metadata(metadata_file)
    measurements = load_nitrogen_measurements(measurements_file)
    print(f"  ✓ {inventory.n_sites} sites")
    print(f"  ✓ {len(measurements)} measurements")
    print()

    # Select top sites
    print("Selecting Tier 1 sites...")
    tier1_sites = select_tier1_sites(
        inventory, measurements, target_count=12, min_score=5.0
    )
    print(f"  ✓ Selected {len(tier1_sites)} sites with score ≥ 5.0")
    print()

    # Ensure diversity
    tier1_sites = ensure_ecosystem_diversity(tier1_sites, min_per_ecosystem=2)
    print("Ensured ecosystem diversity (≥2 sites per major ecosystem)")
    print()

    # Display results
    print("=" * 120)
    print("TIER 1 SITES (Ranked by Priority)")
    print("=" * 120)
    print()

    for i, ss in enumerate(tier1_sites, 1):
        print(f"{i:2d}. {ss}")

    print()
    print("=" * 120)
    print("DETAILED SITE INFORMATION")
    print("=" * 120)
    print()

    for i, ss in enumerate(tier1_sites, 1):
        site = ss.site
        print(f"\n{i}. {site.source_id}")
        print(f"   {'='*100}")
        print(f"   Location   : {site.location_text[:80]}")
        if site.coordinates:
            print(
                f"   Coordinates: {site.coordinates.latitude:.4f}°, {site.coordinates.longitude:.4f}°"
            )
        print(f"   Ecosystem  : {site.ecosystem_text}")
        if site.ecosystem:
            print(f"   Type       : {site.ecosystem.value}")
        print(f"   Warming    : +{site.temperature_increase_c:.2f}°C")
        print(f"   Method     : {site.warming_method_text[:60]}")
        if site.warming_duration_months:
            print(
                f"   Duration   : {site.max_warming_duration_months} months (timepoints: {len(site.warming_duration_months)})"
            )
        print(f"   Season     : {site.warming_season.value if site.warming_season else 'N/A'}")
        print(f"   Timing     : {site.warming_timing.value if site.warming_timing else 'N/A'}")
        print(
            f"   Measurements: {ss.n_measurements} total, {ss.n_variables} unique variables"
        )

    # Summary by ecosystem
    print()
    print("=" * 120)
    print("ECOSYSTEM REPRESENTATION")
    print("=" * 120)
    print()

    by_eco = defaultdict(int)
    for ss in tier1_sites:
        if ss.site.ecosystem:
            by_eco[ss.site.ecosystem.value] += 1

    for ecosystem, count in sorted(by_eco.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {ecosystem:30s} : {count:2d} sites")

    # Geographic distribution
    print()
    print("=" * 120)
    print("GEOGRAPHIC DISTRIBUTION")
    print("=" * 120)
    print()

    lats = [ss.site.coordinates.latitude for ss in tier1_sites if ss.site.coordinates]
    lons = [ss.site.coordinates.longitude for ss in tier1_sites if ss.site.coordinates]

    if lats and lons:
        print(f"  Latitude range : {min(lats):.2f}° to {max(lats):.2f}°")
        print(f"  Longitude range: {min(lons):.2f}° to {max(lons):.2f}°")

    # Export site list
    output_file = Path(__file__).parent.parent / "output" / "tier1_sites.txt"
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, "w") as f:
        f.write("# Tier 1 Sites for NetCDF Generation\n")
        f.write(f"# Selected: {len(tier1_sites)} sites\n")
        f.write("# Format: source_id | latitude | longitude | ecosystem | warming_c\n\n")
        for ss in tier1_sites:
            site = ss.site
            if site.coordinates:
                f.write(
                    f"{site.source_id} | "
                    f"{site.coordinates.latitude:.4f} | "
                    f"{site.coordinates.longitude:.4f} | "
                    f"{site.ecosystem.value if site.ecosystem else 'unknown'} | "
                    f"{site.temperature_increase_c:.2f}\n"
                )

    print()
    print(f"✓ Exported site list to: {output_file}")
    print()


if __name__ == "__main__":
    main()
