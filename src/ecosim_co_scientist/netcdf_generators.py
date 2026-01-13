"""NetCDF file generators for EcoSIM input files.

This module creates grid, climate, and PFT NetCDF files in EcoSIM format.
"""

from pathlib import Path
from typing import Optional

try:
    import numpy as np
    import xarray as xr
except ImportError:
    np = None
    xr = None

from ecosim_co_scientist.data_models import ExperimentalSite
from ecosim_co_scientist.soil_properties import SoilProfile


def create_grid_file(
    site: ExperimentalSite,
    soil_profile: SoilProfile,
    output_path: Path,
) -> Path:
    """Create EcoSIM grid/soil NetCDF file.

    Args:
        site: Experimental site metadata
        soil_profile: Soil profile with layer properties
        output_path: Path for output NetCDF file

    Returns:
        Path to created file
    """
    if np is None or xr is None:
        raise ImportError("numpy and xarray required. Install with: pip install numpy xarray")

    print(f"Generating grid file for {site.source_id[:60]}")
    print(f"  Output: {output_path}")

    # Dimensions
    ngrid = 1
    ntopou = 1
    nlevs = len(soil_profile.layers)
    ncol = 1
    nrow = 1

    # Create dataset
    ds = xr.Dataset(
        coords={
            "ngrid": ("ngrid", [0]),
            "ntopou": ("ntopou", [0]),
            "nlevs": ("nlevs", list(range(nlevs))),
            "ncol": ("ncol", [0]),
            "nrow": ("nrow", [0]),
        }
    )

    # Grid-level variables
    ds["ALATG"] = (("ngrid",), [soil_profile.latitude])
    ds["ALATG"].attrs["long_name"] = "Latitude"
    ds["ALATG"].attrs["units"] = "degrees north"

    ds["ALTIG"] = (("ngrid",), [soil_profile.altitude_m])
    ds["ALTIG"].attrs["long_name"] = "Altitude above sea-level"
    ds["ALTIG"].attrs["units"] = "m"

    ds["ATCAG"] = (("ngrid",), [soil_profile.mean_annual_temp_c])
    ds["ATCAG"].attrs["long_name"] = "Mean annual temperature"
    ds["ATCAG"].attrs["units"] = "oC"

    # Atmospheric composition (modern values)
    ds["CO2EIG"] = (("ngrid",), [420.0])  # ppm, current atmospheric
    ds["CO2EIG"].attrs["long_name"] = "Atmospheric CO2"
    ds["CO2EIG"].attrs["units"] = "ppm"

    ds["Z2GEG"] = (("ngrid",), [780840.0])  # ppm (78.084%)
    ds["Z2GEG"].attrs["long_name"] = "Atmospheric N2"
    ds["Z2GEG"].attrs["units"] = "ppm"

    ds["Z2OEG"] = (("ngrid",), [0.33])  # ppm
    ds["Z2OEG"].attrs["long_name"] = "Atmospheric N2O"
    ds["Z2OEG"].attrs["units"] = "ppm"

    ds["OXYEG"] = (("ngrid",), [209460.0])  # ppm (20.946%)
    ds["OXYEG"].attrs["long_name"] = "Atmospheric O2"
    ds["OXYEG"].attrs["units"] = "ppm"

    ds["CH4EG"] = (("ngrid",), [1.9])  # ppm
    ds["CH4EG"].attrs["long_name"] = "Atmospheric CH4"
    ds["CH4EG"].attrs["units"] = "ppm"

    ds["ZNH3EG"] = (("ngrid",), [0.01])  # ppm
    ds["ZNH3EG"].attrs["long_name"] = "Atmospheric NH3"
    ds["ZNH3EG"].attrs["units"] = "ppm"

    # Topographic unit variables
    ds["topo_grid"] = (("ntopou",), [0])
    ds["topo_grid"].attrs["long_name"] = "grid ID of the topo unit"
    ds["topo_grid"].attrs["units"] = "none"

    ds["NUI"] = (("ntopou",), np.array([1], dtype=np.int8))
    ds["NUI"].attrs["long_name"] = "Initial layer number of soil surface layer"
    ds["NUI"].attrs["units"] = "none"

    ds["NJ"] = (("ntopou",), np.array([min(10, nlevs)], dtype=np.int8))
    ds["NJ"].attrs["long_name"] = "Layer number of maximum rooting layer"
    ds["NJ"].attrs["units"] = "none"

    # Soil layer properties
    depths = np.array([layer.depth_m for layer in soil_profile.layers])
    ds["CDPTH"] = (("ntopou", "nlevs"), depths.reshape(1, -1))
    ds["CDPTH"].attrs["long_name"] = "Depth to bottom of soil layer"
    ds["CDPTH"].attrs["units"] = "m"
    ds["CDPTH"].attrs["_FillValue"] = -999.9

    bulk_density = np.array([layer.bulk_density_mg_m3 for layer in soil_profile.layers])
    ds["BKDSI"] = (("ntopou", "nlevs"), bulk_density.reshape(1, -1))
    ds["BKDSI"].attrs["long_name"] = "Initial bulk density"
    ds["BKDSI"].attrs["units"] = "Mg m-3"
    ds["BKDSI"].attrs["_FillValue"] = -999.9

    sand = np.array([layer.sand_fraction for layer in soil_profile.layers])
    ds["CSAND"] = (("ntopou", "nlevs"), sand.reshape(1, -1))
    ds["CSAND"].attrs["long_name"] = "Sand content"
    ds["CSAND"].attrs["units"] = "kg Mg-1"
    ds["CSAND"].attrs["_FillValue"] = -999.9

    silt = np.array([layer.silt_fraction for layer in soil_profile.layers])
    ds["CSILT"] = (("ntopou", "nlevs"), silt.reshape(1, -1))
    ds["CSILT"].attrs["long_name"] = "Silt content"
    ds["CSILT"].attrs["units"] = "kg Mg-1"
    ds["CSILT"].attrs["_FillValue"] = -999.9

    ph = np.array([layer.ph for layer in soil_profile.layers])
    ds["PH"] = (("ntopou", "nlevs"), ph.reshape(1, -1))
    ds["PH"].attrs["long_name"] = "depth-resolved pH"
    ds["PH"].attrs["units"] = "none"
    ds["PH"].attrs["_FillValue"] = -999.9

    organic_c = np.array([layer.organic_c_kg_mg for layer in soil_profile.layers])
    ds["CORGC"] = (("ntopou", "nlevs"), organic_c.reshape(1, -1))
    ds["CORGC"].attrs["long_name"] = "Total soil organic carbon"
    ds["CORGC"].attrs["units"] = "kg C/Mg soil"
    ds["CORGC"].attrs["_FillValue"] = -999.9

    organic_n = np.array([layer.organic_n_g_mg for layer in soil_profile.layers])
    ds["CORGN"] = (("ntopou", "nlevs"), organic_n.reshape(1, -1))
    ds["CORGN"].attrs["long_name"] = "Total soil organic nitrogen"
    ds["CORGN"].attrs["units"] = "g N/Mg soil"
    ds["CORGN"].attrs["_FillValue"] = -999.9

    nh4 = np.array([layer.nh4_g_mg for layer in soil_profile.layers])
    ds["CNH4"] = (("ntopou", "nlevs"), nh4.reshape(1, -1))
    ds["CNH4"].attrs["long_name"] = "Total soil NH4 concentration"
    ds["CNH4"].attrs["units"] = "gN/Mg soil"
    ds["CNH4"].attrs["_FillValue"] = -999.9

    no3 = np.array([layer.no3_g_mg for layer in soil_profile.layers])
    ds["CNO3"] = (("ntopou", "nlevs"), no3.reshape(1, -1))
    ds["CNO3"].attrs["long_name"] = "Total soil NO3 concentration"
    ds["CNO3"].attrs["units"] = "gN/Mg soil"
    ds["CNO3"].attrs["_FillValue"] = -999.9

    # Hydraulic properties (simplified)
    ds["FC"] = (("ntopou", "nlevs"), np.full((1, nlevs), 0.35))
    ds["FC"].attrs["long_name"] = "Field capacity"
    ds["FC"].attrs["units"] = "m3 m-3"
    ds["FC"].attrs["_FillValue"] = -999.9

    ds["WP"] = (("ntopou", "nlevs"), np.full((1, nlevs), 0.15))
    ds["WP"].attrs["long_name"] = "Wilting point"
    ds["WP"].attrs["units"] = "m3 m-3"
    ds["WP"].attrs["_FillValue"] = -999.9

    ds["SCNV"] = (("ntopou", "nlevs"), np.full((1, nlevs), 50.0))
    ds["SCNV"].attrs["long_name"] = "Vertical hydraulic conductivity Ksat"
    ds["SCNV"].attrs["units"] = "mm h-1"
    ds["SCNV"].attrs["_FillValue"] = -999.9

    # Global attributes
    ds.attrs["title"] = f"EcoSIM grid file for {site.source_id}"
    ds.attrs["source"] = "Generated by EcoSIM Co-Scientist"
    ds.attrs["ecosystem"] = site.ecosystem_text
    ds.attrs["warming_treatment_c"] = site.temperature_increase_c or 0.0

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ds.to_netcdf(output_path)

    print(f"  ✓ Created grid file with {nlevs} soil layers")
    return output_path


def create_climate_file(
    site: ExperimentalSite,
    output_path: Path,
    start_year: int = 2010,
    n_years: int = 2,
    apply_warming: bool = False,
) -> Path:
    """Create EcoSIM climate NetCDF file.

    Creates synthetic climate data for demonstration.
    In production, would use actual ERA5 data.

    Args:
        site: Experimental site metadata
        output_path: Path for output NetCDF file
        start_year: Starting year
        n_years: Number of years
        apply_warming: Whether to apply warming treatment

    Returns:
        Path to created file
    """
    if np is None or xr is None:
        raise ImportError("numpy and xarray required")

    treatment_type = "treatment" if apply_warming else "control"
    print(f"Generating {treatment_type} climate file for {site.source_id[:60]}")
    print(f"  Years: {start_year}-{start_year + n_years - 1}")
    print(f"  Output: {output_path}")

    # Dimensions
    n_days = 366
    n_hours = 24
    ngrid = 1

    # Create dataset
    ds = xr.Dataset(
        coords={
            "year": ("year", list(range(n_years))),
            "day": ("day", list(range(1, n_days + 1))),
            "hour": ("hour", list(range(n_hours))),
            "ngrid": ("ngrid", [0]),
        }
    )

    # Create synthetic climate data
    # Temperature: sinusoidal annual cycle + diurnal cycle
    # Need to create arrays with explicit broadcasting for all 4 dimensions

    # Base temperature (from site latitude)
    if site.coordinates:
        lat = abs(site.coordinates.latitude)
        base_temp = 25 - 0.5 * lat  # Rough latitude-temperature relationship
    else:
        base_temp = 10.0

    # Initialize full temperature array
    temp = np.zeros((n_years, n_days, n_hours, ngrid))

    for year in range(n_years):
        for day in range(n_days):
            # Annual cycle (cosine, coldest on day 15, warmest on day 195)
            annual_temp = -15 * np.cos(2 * np.pi * (day - 15) / 365)

            for hour in range(n_hours):
                # Diurnal cycle (cosine, coldest at 6am, warmest at 3pm)
                diurnal_temp = -8 * np.cos(2 * np.pi * (hour - 15) / 24)

                # Combined temperature
                temp[year, day, hour, 0] = base_temp + annual_temp + diurnal_temp

    # Apply warming treatment if requested
    if apply_warming and site.temperature_increase_c:
        temp = temp + site.temperature_increase_c
        print(f"  Applied +{site.temperature_increase_c:.2f}°C warming offset")

    ds["TMPH"] = (("year", "day", "hour", "ngrid"), temp)
    ds["TMPH"].attrs["long_name"] = "hourly air temperature"
    ds["TMPH"].attrs["units"] = "oC"
    ds["TMPH"].attrs["_FillValue"] = 1.e+30
    ds["TMPH"].attrs["missing_value"] = 1.e+30

    # Wind speed (simplified constant)
    wind = np.full((n_years, n_days, n_hours, ngrid), 3.0)
    ds["WINDH"] = (("year", "day", "hour", "ngrid"), wind)
    ds["WINDH"].attrs["long_name"] = "horizontal wind speed"
    ds["WINDH"].attrs["units"] = "m s^-1"
    ds["WINDH"].attrs["_FillValue"] = 1.e+30

    # Precipitation (random, heavier in summer)
    precip = np.zeros((n_years, n_days, n_hours, ngrid))
    for day in range(n_days):
        seasonal_factor = 0.1 * (1 + 0.5 * np.sin(2 * np.pi * day / 365))
        precip[:, day, :, :] = seasonal_factor * np.random.rand(n_years, n_hours, ngrid)

    ds["RAINH"] = (("year", "day", "hour", "ngrid"), precip)
    ds["RAINH"].attrs["long_name"] = "Total precipitation"
    ds["RAINH"].attrs["units"] = "mm m^-2 hr^-1"
    ds["RAINH"].attrs["_FillValue"] = 1.e+30

    # Solar radiation (diurnal + annual cycle, zero at night)
    solar = np.zeros((n_years, n_days, n_hours, ngrid))
    solar_max = 800  # W/m²
    for day in range(n_days):
        # Annual variation
        solar_annual = 0.3 + 0.7 * (1 - 0.5 * np.cos(2 * np.pi * day / 365))
        for hour in range(n_hours):
            # Diurnal cycle (zero at night)
            solar_diurnal = max(0, np.sin(np.pi * (hour - 6) / 12))
            solar[:, day, hour, 0] = solar_max * solar_annual * solar_diurnal

    ds["SRADH"] = (("year", "day", "hour", "ngrid"), solar)
    ds["SRADH"].attrs["long_name"] = "Incident solar radiation"
    ds["SRADH"].attrs["units"] = "W m^-2"
    ds["SRADH"].attrs["_FillValue"] = 1.e+30

    # Vapor pressure (function of temperature)
    dewpoint = temp - 5.0  # Rough approximation
    vapor_pressure = 0.611 * np.exp(17.27 * dewpoint / (dewpoint + 237.3))
    ds["DWPTH"] = (("year", "day", "hour", "ngrid"), vapor_pressure)
    ds["DWPTH"].attrs["long_name"] = "atmospheric vapor pressure"
    ds["DWPTH"].attrs["units"] = "kPa"
    ds["DWPTH"].attrs["_FillValue"] = 1.e+30

    # Year dimension
    ds["year"] = (("year",), [start_year + i for i in range(n_years)])
    ds["year"].attrs["long_name"] = "year AD"

    # Precipitation chemistry (annual averages)
    ds["CN4RIG"] = (("year", "ngrid"), np.full((n_years, ngrid), 0.5))
    ds["CN4RIG"].attrs["long_name"] = "NH4 conc in precip"
    ds["CN4RIG"].attrs["units"] = "gN m^-3"

    ds["CNORIG"] = (("year", "ngrid"), np.full((n_years, ngrid), 0.8))
    ds["CNORIG"].attrs["long_name"] = "NO3 conc in precip"
    ds["CNORIG"].attrs["units"] = "gN m^-3"

    ds["PHRG"] = (("year", "ngrid"), np.full((n_years, ngrid), 5.6))
    ds["PHRG"].attrs["long_name"] = "pH in precipitation"

    # Global attributes
    ds.attrs["title"] = f"EcoSIM climate file for {site.source_id} ({treatment_type})"
    ds.attrs["source"] = "Synthetic climate data for demonstration"
    ds.attrs["warming_treatment"] = "yes" if apply_warming else "no"
    if apply_warming and site.temperature_increase_c:
        ds.attrs["temperature_offset_c"] = site.temperature_increase_c

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ds.to_netcdf(output_path)

    print(f"  ✓ Created climate file")
    return output_path
