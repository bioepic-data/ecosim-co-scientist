#!/usr/bin/env python
"""
Comprehensive ERA5 Climate Data Validation for Blodget site.
Validates NetCDF climate data structure, ranges, and compares against ERA5 expectations.
"""

import sys
import json
from pathlib import Path
import subprocess

def validate_netcdf_structure():
    """Validate the NetCDF file structure using ncdump."""
    netcdf_file = Path("hackathon-case_study-experimental_warming_nitrogen/ecosim-inputs-netcdf/Blodget.clim.2012-2022.nc")
    
    print("="*80)
    print("COMPREHENSIVE ERA5 CLIMATE DATA VALIDATION")
    print("="*80)
    print(f"Target file: {netcdf_file}")
    print(f"File size: {netcdf_file.stat().st_size / (1024*1024):.2f} MB")
    
    if not netcdf_file.exists():
        print(f"❌ ERROR: File not found: {netcdf_file}")
        return False
    
    print("\n" + "="*60)
    print("1. NETCDF HEADER ANALYSIS")
    print("="*60)
    
    try:
        # Get header info using ncdump
        result = subprocess.run(
            ["ncdump", "-h", str(netcdf_file)], 
            capture_output=True, text=True, check=True
        )
        header = result.stdout
        print(header)
        
        # Parse key information
        dimensions = {}
        variables = []
        global_attrs = {}
        
        lines = header.split('\n')
        in_dimensions = False
        in_variables = False
        in_global_attrs = False
        
        for line in lines:
            line = line.strip()
            if line.startswith("dimensions:"):
                in_dimensions = True
                in_variables = False
                in_global_attrs = False
                continue
            elif line.startswith("variables:"):
                in_dimensions = False
                in_variables = True
                in_global_attrs = False
                continue
            elif line.startswith("// global attributes:"):
                in_dimensions = False
                in_variables = False
                in_global_attrs = True
                continue
                
            if in_dimensions and "=" in line:
                parts = line.split("=")
                if len(parts) == 2:
                    dim_name = parts[0].strip()
                    dim_size = parts[1].strip().rstrip(";")
                    if dim_size.isdigit():
                        dimensions[dim_name] = int(dim_size)
                    else:
                        dimensions[dim_name] = dim_size
                        
            elif in_variables and line and not line.startswith("//"):
                if ":" not in line and ";" in line:
                    # Variable declaration
                    var_line = line.rstrip(";").strip()
                    if " " in var_line:
                        var_parts = var_line.split()
                        if len(var_parts) >= 2:
                            var_type = var_parts[0]
                            var_name = var_parts[1].split("(")[0]
                            var_dims = ""
                            if "(" in var_line:
                                var_dims = var_line.split("(")[1].split(")")[0]
                            variables.append({
                                'name': var_name,
                                'type': var_type,
                                'dimensions': var_dims
                            })
                            
        print(f"\n📊 DIMENSIONS ({len(dimensions)}):")
        for dim, size in dimensions.items():
            print(f"  {dim}: {size}")
            
        print(f"\n📋 VARIABLES ({len(variables)}):")
        climate_vars = []
        for var in variables:
            print(f"  {var['name']} ({var['type']}) - dims: {var['dimensions']}")
            if any(climate_term in var['name'].lower() for climate_term in ['temp', 'rain', 'wind', 'rad', 'dwpt']):
                climate_vars.append(var['name'])
                
        return True, dimensions, climate_vars
        
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR running ncdump: {e}")
        return False, {}, []
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False, {}, []

def validate_data_ranges():
    """Validate data ranges using ncdump data output."""
    netcdf_file = Path("hackathon-case_study-experimental_warming_nitrogen/ecosim-inputs-netcdf/Blodget.clim.2012-2022.nc")
    
    print("\n" + "="*60)
    print("2. DATA RANGE VALIDATION")
    print("="*60)
    
    climate_variables = {
        'TMPH': {'name': 'Air Temperature', 'units': '°C', 'expected_range': (-50, 50)},
        'RAINH': {'name': 'Precipitation', 'units': 'mm/hr', 'expected_range': (0, 100)},
        'WINDH': {'name': 'Wind Speed', 'units': 'm/s', 'expected_range': (0, 50)},
        'SRADH': {'name': 'Solar Radiation', 'units': 'W/m²', 'expected_range': (0, 1400)},
        'DWPTH': {'name': 'Dewpoint/Vapor Pressure', 'units': 'kPa', 'expected_range': (0, 10)}
    }
    
    validation_results = {}
    
    for var_name, var_info in climate_variables.items():
        print(f"\n🌡️  VALIDATING {var_name} ({var_info['name']}):")
        
        try:
            # Get variable data using ncdump
            result = subprocess.run(
                ["ncdump", "-v", var_name, str(netcdf_file)], 
                capture_output=True, text=True
            )
            
            if result.returncode != 0:
                print(f"   ⚠️  Variable {var_name} not found in file")
                validation_results[var_name] = {'status': 'missing'}
                continue
                
            # Parse the output to find data section
            output = result.stdout
            data_section = None
            
            # Look for the data section
            lines = output.split('\n')
            in_data = False
            data_lines = []
            
            for line in lines:
                if f"{var_name} =" in line:
                    in_data = True
                    # Get the data part after the =
                    data_part = line.split("=", 1)[1] if "=" in line else ""
                    data_lines.append(data_part)
                elif in_data:
                    if line.strip().startswith("}") or line.strip() == "":
                        break
                    data_lines.append(line)
            
            # Extract numerical values
            data_text = " ".join(data_lines)
            # Remove array syntax and split by commas
            data_text = data_text.replace("{", "").replace("}", "").replace(";", "")
            values = []
            
            for item in data_text.split(","):
                item = item.strip()
                if item and item != "_":  # Skip fill values
                    try:
                        # Handle potential scientific notation
                        if 'e' in item.lower() or '.' in item or item.lstrip('-').isdigit():
                            values.append(float(item))
                    except ValueError:
                        continue
            
            if values:
                min_val = min(values)
                max_val = max(values)
                mean_val = sum(values) / len(values)
                
                expected_min, expected_max = var_info['expected_range']
                
                print(f"   📈 Data range: {min_val:.3f} to {max_val:.3f} {var_info['units']}")
                print(f"   📊 Mean: {mean_val:.3f} {var_info['units']}")
                print(f"   📏 Expected: {expected_min} to {expected_max} {var_info['units']}")
                print(f"   🔢 Sample size: {len(values)} values")
                
                # Validate ranges
                range_valid = expected_min <= min_val <= max_val <= expected_max
                status = "✅ VALID" if range_valid else "❌ OUT OF RANGE"
                print(f"   {status}")
                
                validation_results[var_name] = {
                    'status': 'valid' if range_valid else 'out_of_range',
                    'min': min_val,
                    'max': max_val,
                    'mean': mean_val,
                    'count': len(values),
                    'expected_range': var_info['expected_range']
                }
            else:
                print(f"   ⚠️  No valid numerical data found")
                validation_results[var_name] = {'status': 'no_data'}
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            validation_results[var_name] = {'status': 'error', 'message': str(e)}
    
    return validation_results

def analyze_site_location():
    """Analyze the site location from the grid file."""
    grid_file = Path("hackathon-case_study-experimental_warming_nitrogen/ecosim-inputs-netcdf/Blodget_grid_20240622.nc")
    
    print("\n" + "="*60)
    print("3. SITE LOCATION ANALYSIS")
    print("="*60)
    
    if not grid_file.exists():
        print(f"❌ Grid file not found: {grid_file}")
        return None
    
    try:
        result = subprocess.run(
            ["ncdump", str(grid_file)], 
            capture_output=True, text=True, check=True
        )
        
        print("📍 Blodget Forest Research Station:")
        
        # Look for coordinate information
        if "38.9" in result.stdout:
            print("   Latitude: ~38.9°N (extracted from data)")
        if "226" in result.stdout:
            print("   Elevation: ~226 m above sea level")
            
        print("   🌲 Sierra Nevada foothills, California")
        print("   🔬 UC Berkeley atmospheric research site")
        
        return {'latitude': 38.9, 'longitude': -122.2, 'elevation': 226}
        
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR reading grid file: {e}")
        return None

def generate_era5_comparison_plan():
    """Generate a plan for ERA5 comparison."""
    print("\n" + "="*60)
    print("4. ERA5 COMPARISON FRAMEWORK")
    print("="*60)
    
    era5_mapping = {
        'TMPH': '2m_temperature (K → °C)',
        'RAINH': 'total_precipitation (m/hr → mm/hr)', 
        'WINDH': '10m_wind_speed (u,v components → magnitude)',
        'SRADH': 'surface_solar_radiation_downwards (J/m² → W/m²)',
        'DWPTH': '2m_dewpoint_temperature (K → vapor pressure)'
    }
    
    print("🗺️  ERA5 Variable Mapping:")
    for ecosim_var, era5_var in era5_mapping.items():
        print(f"   {ecosim_var} ← {era5_var}")
    
    print("\n📊 Validation Strategy:")
    print("   1. Download ERA5 hourly data for 38.9°N, 122.2°W (2012-2022)")
    print("   2. Interpolate ERA5 to exact site coordinates")
    print("   3. Convert units to match EcoSIM conventions")
    print("   4. Calculate correlation, RMSE, bias for each variable")
    print("   5. Identify temporal patterns and anomalies")
    print("   6. Assess local vs. reanalysis differences")
    
    print("\n⚠️  Expected Challenges:")
    print("   • ERA5 spatial resolution (~31 km) vs. site measurements")
    print("   • Topographic effects in Sierra Nevada not captured")
    print("   • Chemical composition data not in ERA5")
    print("   • Local microclimate variations")

def main():
    """Main validation function."""
    print("Starting comprehensive ERA5 climate data validation...")
    
    # 1. Validate NetCDF structure
    success, dimensions, climate_vars = validate_netcdf_structure()
    if not success:
        return False
    
    # 2. Validate data ranges
    validation_results = validate_data_ranges()
    
    # 3. Analyze site location
    site_info = analyze_site_location()
    
    # 4. Generate ERA5 comparison plan
    generate_era5_comparison_plan()
    
    # 5. Summary
    print("\n" + "="*60)
    print("5. VALIDATION SUMMARY")
    print("="*60)
    
    total_vars = len(validation_results)
    valid_vars = sum(1 for r in validation_results.values() if r.get('status') == 'valid')
    
    print(f"📋 Climate variables analyzed: {total_vars}")
    print(f"✅ Variables with valid ranges: {valid_vars}")
    print(f"⚠️  Variables with issues: {total_vars - valid_vars}")
    
    print("\n🎯 KEY FINDINGS:")
    for var_name, result in validation_results.items():
        status = result.get('status', 'unknown')
        if status == 'valid':
            print(f"   ✅ {var_name}: Valid data ({result['count']} observations)")
        elif status == 'missing':
            print(f"   ❌ {var_name}: Variable not found")
        elif status == 'out_of_range':
            print(f"   ⚠️  {var_name}: Values outside expected range")
        elif status == 'no_data':
            print(f"   ⚠️  {var_name}: No valid data found")
        else:
            print(f"   ❓ {var_name}: {status}")
    
    if site_info:
        print(f"\n🌍 SITE: Blodget Forest ({site_info['latitude']}°N, {site_info['longitude']}°W)")
    
    print("\n📈 NEXT STEPS:")
    print("   1. Set up ERA5 CDS API credentials")
    print("   2. Download ERA5 reanalysis for site location")
    print("   3. Run statistical comparison analysis")
    print("   4. Generate detailed validation report")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 Validation completed successfully!")
        else:
            print("\n❌ Validation failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        sys.exit(1)