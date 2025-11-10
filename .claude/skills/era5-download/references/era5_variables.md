# ERA5 Variable Reference

This reference provides common ERA5 variables organized by category. For the complete list, visit: https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels

## Search Strategy

When searching this file with grep:
- Search by physical quantity: `grep -i "temperature"`, `grep -i "precipitation"`
- Search by variable name: `grep "2m_temperature"`, `grep "tp"`
- Search by category: `grep "## Atmospheric"`, `grep "## Land Surface"`

## Atmospheric Variables (Single Level)

### Temperature
- `2m_temperature` - 2 meter temperature (K)
- `skin_temperature` - Skin temperature (K)
- `2m_dewpoint_temperature` - 2 meter dewpoint temperature (K)

### Precipitation
- `total_precipitation` - Total precipitation (m)
- `convective_precipitation` - Convective precipitation (m)
- `large_scale_precipitation` - Large scale precipitation (m)
- `snowfall` - Snowfall (m of water equivalent)

### Pressure
- `surface_pressure` - Surface pressure (Pa)
- `mean_sea_level_pressure` - Mean sea level pressure (Pa)

### Wind
- `10m_u_component_of_wind` - 10 meter U wind component (m/s)
- `10m_v_component_of_wind` - 10 meter V wind component (m/s)
- `10m_wind_gust_since_previous_post_processing` - Wind gusts (m/s)

### Radiation
- `surface_solar_radiation_downwards` - Surface solar radiation downwards (J/m²)
- `surface_thermal_radiation_downwards` - Surface thermal radiation downwards (J/m²)
- `surface_net_solar_radiation` - Net solar radiation at surface (J/m²)
- `surface_net_thermal_radiation` - Net thermal radiation at surface (J/m²)
- `toa_incident_solar_radiation` - TOA incident solar radiation (J/m²)

### Humidity
- `2m_relative_humidity` - 2 meter relative humidity (%)
- `total_column_water_vapour` - Total column water vapour (kg/m²)

### Cloud Cover
- `total_cloud_cover` - Total cloud cover (0-1)
- `low_cloud_cover` - Low cloud cover (0-1)
- `medium_cloud_cover` - Medium cloud cover (0-1)
- `high_cloud_cover` - High cloud cover (0-1)

## Land Surface Variables

### Soil Temperature
- `soil_temperature_level_1` - Soil temperature level 1 (0-7 cm) (K)
- `soil_temperature_level_2` - Soil temperature level 2 (7-28 cm) (K)
- `soil_temperature_level_3` - Soil temperature level 3 (28-100 cm) (K)
- `soil_temperature_level_4` - Soil temperature level 4 (100-289 cm) (K)

### Soil Moisture
- `volumetric_soil_water_layer_1` - Soil water layer 1 (0-7 cm) (m³/m³)
- `volumetric_soil_water_layer_2` - Soil water layer 2 (7-28 cm) (m³/m³)
- `volumetric_soil_water_layer_3` - Soil water layer 3 (28-100 cm) (m³/m³)
- `volumetric_soil_water_layer_4` - Soil water layer 4 (100-289 cm) (m³/m³)

### Evapotranspiration
- `evaporation` - Evaporation (m of water equivalent)
- `potential_evaporation` - Potential evaporation (m)

### Vegetation
- `leaf_area_index_low_vegetation` - Leaf area index for low vegetation (m²/m²)
- `leaf_area_index_high_vegetation` - Leaf area index for high vegetation (m²/m²)

### Snow
- `snow_depth` - Snow depth (m of water equivalent)
- `snow_cover` - Snow cover (%)
- `snow_density` - Snow density (kg/m³)

### Runoff
- `runoff` - Runoff (m)
- `surface_runoff` - Surface runoff (m)
- `sub_surface_runoff` - Sub-surface runoff (m)

## Pressure Level Variables (3D Atmosphere)

These require specifying pressure levels (e.g., 1000, 850, 500 hPa).

### Basic Meteorology
- `temperature` - Temperature (K)
- `geopotential` - Geopotential (m²/s²)
- `u_component_of_wind` - U component of wind (m/s)
- `v_component_of_wind` - V component of wind (m/s)
- `vertical_velocity` - Vertical velocity (Pa/s)
- `relative_humidity` - Relative humidity (%)
- `specific_humidity` - Specific humidity (kg/kg)

### Standard Pressure Levels
Common choices: `[1000, 925, 850, 700, 500, 300, 200]` hPa

## Common Use Cases for Ecosystem Modeling

### Climate Forcing Data for EcoSIM
Typical variables needed:
- `2m_temperature` - Air temperature forcing
- `total_precipitation` - Precipitation forcing
- `surface_pressure` - Atmospheric pressure
- `surface_solar_radiation_downwards` - Solar radiation
- `10m_u_component_of_wind` - Wind speed (U component)
- `10m_v_component_of_wind` - Wind speed (V component)
- `2m_relative_humidity` or `2m_dewpoint_temperature` - Humidity

### Soil Conditions
- `soil_temperature_level_1` through `level_4` - Initial soil temperature profiles
- `volumetric_soil_water_layer_1` through `layer_4` - Initial soil moisture profiles

### Validation Data
- `evaporation` - Compare against modeled evapotranspiration
- `runoff` - Compare against modeled water balance
- `snow_depth` - Validate snow accumulation/melt

## Download Tips

1. **Start small**: Test with 1-2 days before downloading years of data
2. **Geographic subsetting**: Use `--area` to download only the region needed
3. **Temporal subsetting**: Use `--hours` for sub-daily data (e.g., 6-hourly: `00:00 06:00 12:00 18:00`)
4. **Format choice**: NetCDF is generally easier to work with than GRIB
5. **Batch requests**: For large downloads, break into monthly or yearly chunks

## Variable Name Conventions

ERA5 uses underscores in variable names:
- Correct: `2m_temperature`
- Wrong: `2m-temperature`, `2mTemperature`, `t2m`

Note: Some documentation may use short names like `t2m`, `tp`, `sp` - these correspond to the long names used in CDS API:
- `t2m` → `2m_temperature`
- `tp` → `total_precipitation`
- `sp` → `surface_pressure`
- `u10` → `10m_u_component_of_wind`
- `v10` → `10m_v_component_of_wind`
