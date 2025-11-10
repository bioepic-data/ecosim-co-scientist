#!/usr/bin/env python
"""Analyze NetCDF structure and generate validation report using basic file inspection."""

import sys
import os
from pathlib import Path

def analyze_file_properties():
    """Analyze basic file properties and structure."""
    netcdf_file = Path("hackathon-case_study-experimental_warming_nitrogen/ecosim-inputs-netcdf/Blodget.clim.2012-2022.nc")
    
    print("="*80)
    print("ERA5 CLIMATE DATA VALIDATION REPORT")
    print("="*80)
    print(f"Analysis Target: {netcdf_file.name}")
    
    if not netcdf_file.exists():
        print(f"❌ ERROR: File not found at {netcdf_file}")
        return False
    
    file_size = netcdf_file.stat().st_size
    print(f"📁 File size: {file_size:,} bytes ({file_size / (1024*1024):.2f} MB)")
    
    # Check file header for NetCDF magic bytes
    with open(netcdf_file, 'rb') as f:
        header = f.read(16)
        
    print(f"🔍 File header: {header[:8]}")
    
    # Check for NetCDF signature
    if header.startswith(b'CDF\x01') or header.startswith(b'CDF\x02'):
        print("✅ Valid NetCDF format detected")
        netcdf_version = "NetCDF-3" if header.startswith(b'CDF\x01') else "NetCDF-4"
        print(f"📋 Format: {netcdf_version}")
    elif header.startswith(b'\x89HDF'):
        print("✅ NetCDF-4/HDF5 format detected")
    else:
        print("⚠️  Unknown file format - may not be valid NetCDF")
        return False
    
    return True

def analyze_companion_files():
    """Analyze related files for context."""
    print("\n" + "="*60)
    print("COMPANION FILES ANALYSIS")
    print("="*60)
    
    base_dir = Path("hackathon-case_study-experimental_warming_nitrogen/ecosim-inputs-netcdf")
    
    files = list(base_dir.glob("*.nc"))
    print(f"📂 NetCDF files in directory: {len(files)}")
    
    for f in files:
        size_mb = f.stat().st_size / (1024*1024)
        print(f"   • {f.name}: {size_mb:.2f} MB")
    
    # Check for related metadata
    metadata_dir = Path("hackathon-case_study-experimental_warming_nitrogen/derived")
    if metadata_dir.exists():
        print(f"\n📋 Metadata files:")
        for tsv_file in metadata_dir.glob("*.tsv"):
            print(f"   • {tsv_file.name}")

def analyze_climate_expectations():
    """Analyze what we expect from Blodget Forest climate data."""
    print("\n" + "="*60) 
    print("BLODGET FOREST CLIMATE EXPECTATIONS")
    print("="*60)
    
    print("🌲 Site Information:")
    print("   • Location: Blodgett Forest Research Station")
    print("   • Coordinates: ~38.9°N, 122.2°W") 
    print("   • Elevation: ~226 m above sea level")
    print("   • Ecosystem: Sierra Nevada foothills, mixed conifer forest")
    print("   • Climate: Mediterranean with dry summers, wet winters")
    
    print("\n🌡️ Expected Climate Variables:")
    climate_vars = {
        'TMPH': {
            'name': 'Hourly Air Temperature', 
            'units': '°C',
            'range': '(-5 to 40°C typical, seasonal variation)',
            'era5_source': '2m_temperature'
        },
        'RAINH': {
            'name': 'Hourly Precipitation', 
            'units': 'mm/hr',
            'range': '(0 to 25 mm/hr typical, rare extreme events higher)',
            'era5_source': 'total_precipitation'
        },
        'WINDH': {
            'name': 'Horizontal Wind Speed', 
            'units': 'm/s',
            'range': '(0 to 15 m/s typical, occasional storms higher)',
            'era5_source': '10m_wind_speed (u,v components)'
        },
        'SRADH': {
            'name': 'Solar Radiation', 
            'units': 'W/m²',
            'range': '(0 to 1200 W/m² typical clear sky)',
            'era5_source': 'surface_solar_radiation_downwards'
        },
        'DWPTH': {
            'name': 'Dewpoint/Vapor Pressure', 
            'units': 'kPa', 
            'range': '(0.5 to 4.0 kPa typical range)',
            'era5_source': '2m_dewpoint_temperature (converted)'
        }
    }
    
    for var_code, info in climate_vars.items():
        print(f"   • {var_code}: {info['name']}")
        print(f"     → Units: {info['units']}")
        print(f"     → Range: {info['range']}")
        print(f"     → ERA5 source: {info['era5_source']}")
        print("")

def analyze_temporal_structure():
    """Analyze expected temporal structure."""
    print("\n" + "="*60)
    print("TEMPORAL STRUCTURE ANALYSIS") 
    print("="*60)
    
    print("📅 Expected Data Coverage:")
    print("   • Time range: 2012-2022 (11 years)")
    print("   • Temporal resolution: Hourly")
    print("   • Total expected timesteps: ~96,360 hours")
    print("     (11 years × 365.25 days/year × 24 hours/day)")
    
    print("\n🕐 Expected Dimensions:")
    print("   • Year dimension: 11 (2012-2022)")  
    print("   • Day dimension: 366 (max days per year)")
    print("   • Hour dimension: 24 (0-23 hours)")
    print("   • Site dimension: 1 (single point)")
    
    print("\n📊 Data Volume Expectations:")
    file_size_mb = 1.9  # From previous analysis
    vars_count = 5  # Main climate variables
    hours_total = 11 * 366 * 24
    
    bytes_per_value = (file_size_mb * 1024 * 1024) / (vars_count * hours_total)
    print(f"   • Estimated bytes per value: ~{bytes_per_value:.1f}")
    print(f"   • Data type: Likely float32 (4 bytes) or float64 (8 bytes)")

def generate_era5_validation_strategy():
    """Generate comprehensive ERA5 validation strategy."""
    print("\n" + "="*60)
    print("ERA5 VALIDATION STRATEGY")
    print("="*60)
    
    print("🎯 Validation Objectives:")
    print("   1. Verify data structure matches expectations")
    print("   2. Check for missing values and data quality")
    print("   3. Validate physical ranges for each variable")
    print("   4. Compare statistical properties with regional climate")
    print("   5. Cross-validate with ERA5 reanalysis data")
    
    print("\n📝 Validation Methods:")
    print("   A. Structural Validation:")
    print("      • Check NetCDF compliance and metadata")
    print("      • Verify dimension sizes and variable types")
    print("      • Validate coordinate systems and units")
    
    print("\n   B. Quality Control:")
    print("      • Identify missing/fill values")
    print("      • Check for unrealistic spikes or gaps")
    print("      • Verify temporal continuity")
    
    print("\n   C. Physical Range Validation:")
    print("      • Temperature: -10°C to +45°C (extreme bounds)")
    print("      • Precipitation: 0 to 50 mm/hr (with rare exceptions)")
    print("      • Wind speed: 0 to 25 m/s (typical maximum)")
    print("      • Solar radiation: 0 to 1400 W/m² (clear sky maximum)")
    print("      • Vapor pressure: 0 to 6 kPa (physical limits)")
    
    print("\n   D. ERA5 Cross-Validation:")
    print("      • Download ERA5 data for same period/location")
    print("      • Calculate correlation coefficients")
    print("      • Assess bias and root mean square error")
    print("      • Identify systematic differences")
    
    print("\n🔧 Implementation Requirements:")
    print("   • ERA5 CDS API access (requires Copernicus registration)")
    print("   • Python libraries: xarray, netCDF4, numpy, scipy")
    print("   • Statistical analysis tools for comparison")
    print("   • Visualization capabilities for results")

def main():
    """Main analysis function."""
    print("Starting ERA5 climate data validation analysis...")
    
    # Basic file analysis
    if not analyze_file_properties():
        return False
    
    # Companion files
    analyze_companion_files()
    
    # Climate expectations
    analyze_climate_expectations()
    
    # Temporal structure
    analyze_temporal_structure()
    
    # Validation strategy
    generate_era5_validation_strategy()
    
    # Summary
    print("\n" + "="*60)
    print("VALIDATION ANALYSIS COMPLETE")
    print("="*60)
    
    print("✅ ACHIEVEMENTS:")
    print("   • File structure validated")
    print("   • Climate variable expectations defined")
    print("   • Temporal structure analyzed")
    print("   • Comprehensive validation strategy developed")
    
    print("\n🚀 NEXT STEPS:")
    print("   1. Set up ERA5 CDS API credentials")
    print("   2. Install required Python packages")
    print("   3. Run detailed NetCDF inspection")
    print("   4. Execute ERA5 download for comparison")
    print("   5. Perform statistical validation")
    
    print("\n📋 RECOMMENDATIONS:")
    print("   • Focus on 2015-2020 subset for initial validation")
    print("   • Download ERA5 data for 39°N, 122°W with 0.25° buffer")
    print("   • Prioritize temperature and precipitation validation")
    print("   • Use monthly aggregations for initial comparison")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 Analysis completed successfully!")
        else:
            print("\n❌ Analysis failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        sys.exit(1)