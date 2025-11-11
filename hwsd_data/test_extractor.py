#!/usr/bin/env python
"""
Test and demonstrate HWSD2 soil profile extraction.

This script tests the hwsd2_extractor module and provides examples of usage.
"""

from pathlib import Path
from hwsd2_extractor import HWSD2Extractor, get_soil_profile, get_smu_id


def test_coordinate_conversion():
    """Test lat/lon to row/col conversion."""
    print("=" * 70)
    print("TEST: Coordinate Conversion")
    print("=" * 70)

    extractor = HWSD2Extractor()

    # Test some known coordinates
    test_coords = [
        (40.0, -105.0, "Boulder, Colorado"),
        (51.5, -0.1, "London, UK"),
        (-23.5, -46.6, "São Paulo, Brazil"),
        (35.7, 139.7, "Tokyo, Japan"),
        (0.0, 0.0, "Null Island (Gulf of Guinea)"),
    ]

    for lat, lon, name in test_coords:
        try:
            row, col = extractor.latlon_to_rowcol(lat, lon)
            smu_id = extractor.latlon_to_smu_id(lat, lon)
            status = f"SMU_ID: {smu_id}" if smu_id else "No data (ocean/ice)"
            print(f"{name:30s} ({lat:7.2f}, {lon:7.2f}) -> Row {row:5d}, Col {col:5d} | {status}")
        except Exception as e:
            print(f"{name:30s} ERROR: {e}")

    print()


def test_smu_extraction():
    """Test SMU extraction from raster."""
    print("=" * 70)
    print("TEST: SMU ID Extraction")
    print("=" * 70)

    # Test locations
    locations = [
        (40.015, -105.270, "Boulder, CO (NEON site)"),
        (44.064, -71.288, "Hubbard Brook, NH"),
        (35.0, -84.0, "Oak Ridge, TN"),
        (64.7, -148.3, "Fairbanks, AK"),
    ]

    for lat, lon, name in locations:
        smu_id = get_smu_id(lat, lon)
        if smu_id:
            print(f"{name:35s} -> SMU_ID: {smu_id}")
        else:
            print(f"{name:35s} -> No data")

    print()


def test_soil_profile_extraction():
    """Test full soil profile extraction (requires database)."""
    print("=" * 70)
    print("TEST: Soil Profile Extraction")
    print("=" * 70)

    db_path = Path(__file__).parent / "hwsd2.db"

    if not db_path.exists():
        print(f"Database not found: {db_path}")
        print("Run 'uv run python load_hwsd2.py' first to create the database.")
        print()
        return

    # Test location: Boulder, Colorado
    lat, lon = 40.015, -105.270
    print(f"Location: {lat}°N, {lon}°W (Boulder, Colorado)\n")

    try:
        profile = get_soil_profile(lat, lon)

        if profile is None:
            print("No soil data at this location")
            return

        print(f"SMU_ID: {profile['smu_id']}")
        print(f"Soil Classification:")
        print(f"  WRB2: {profile['metadata'].get('WRB2_NAME', 'Unknown')}")
        print(f"  WRB4: {profile['metadata'].get('WRB4_NAME', 'Unknown')}")
        print(f"  FAO90: {profile['metadata']['FAO90']}")
        print(f"Drainage: {profile['metadata'].get('DRAINAGE_NAME', 'Unknown')}")
        print(f"Root Depth: {profile['metadata'].get('ROOT_DEPTH_NAME', 'Unknown')}")
        print(f"Climate (Köppen): {profile['metadata'].get('KOPPEN_NAME', 'Unknown')}")
        print(f"Available Water Capacity: {profile['metadata']['AWC']} mm/m")
        print()

        # Display soil layers
        print("Soil Profile (7 layers, 0-200 cm):")
        print("-" * 100)

        layers = profile['layers']
        for _, layer in layers.iterrows():
            print(f"Layer {layer['LAYER']}: {layer['TOPDEP']:3d}-{layer['BOTDEP']:3d} cm")
            print(f"  Texture: {layer['SAND']:5.1f}% sand, {layer['SILT']:5.1f}% silt, {layer['CLAY']:5.1f}% clay")
            print(f"  Texture class: {layer.get('TEXTURE_USDA_NAME', 'Unknown')}")
            print(f"  Bulk density: {layer['BULK']:.2f} g/cm³")
            print(f"  Organic carbon: {layer['ORG_CARBON']:.2f}%")
            print(f"  pH: {layer['PH_WATER']:.1f}")
            if layer['TOTAL_N'] is not None and layer['TOTAL_N'] > 0:
                print(f"  Total N: {layer['TOTAL_N']:.2f} g/kg, C/N ratio: {layer['CN_RATIO']:.1f}")
            if layer['CEC_SOIL'] is not None and layer['CEC_SOIL'] > 0:
                print(f"  CEC: {layer['CEC_SOIL']:.1f} cmolc/kg, Base Sat: {layer['BSAT']:.0f}%")
            print()

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()

    print()


def test_multiple_locations():
    """Extract soil profiles for multiple locations."""
    print("=" * 70)
    print("TEST: Multiple Location Extraction")
    print("=" * 70)

    db_path = Path(__file__).parent / "hwsd2.db"

    if not db_path.exists():
        print(f"Database not found. Skipping this test.")
        print()
        return

    # NEON sites and other ecological research sites
    sites = [
        (40.015, -105.270, "NEON Boulder Creek"),
        (35.689, -105.546, "NEON Jemez River Basin"),
        (32.590, -106.843, "NEON Jornada"),
        (39.103, -96.563, "NEON Konza Prairie"),
        (46.083, -89.586, "NEON Steigerwaldt"),
    ]

    print(f"{'Site':<30s} {'Lat':>8s} {'Lon':>9s} {'SMU_ID':>8s} {'Soil Type':<25s} {'Drainage':<20s}")
    print("-" * 110)

    for lat, lon, name in sites:
        try:
            profile = get_soil_profile(lat, lon)
            if profile:
                smu_id = profile['smu_id']
                soil_type = profile['metadata'].get('WRB2_NAME') or 'Unknown'
                drainage = profile['metadata'].get('DRAINAGE_NAME') or 'Unknown'
                print(f"{name:<30s} {lat:8.3f} {lon:9.3f} {smu_id:8d} {soil_type:<25s} {drainage:<20s}")
            else:
                print(f"{name:<30s} {lat:8.3f} {lon:9.3f} {'No data':>8s}")
        except Exception as e:
            print(f"{name:<30s} {lat:8.3f} {lon:9.3f} ERROR: {e}")

    print()


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("HWSD2 Extractor Test Suite")
    print("=" * 70 + "\n")

    test_coordinate_conversion()
    test_smu_extraction()
    test_soil_profile_extraction()
    test_multiple_locations()

    print("=" * 70)
    print("All tests complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
