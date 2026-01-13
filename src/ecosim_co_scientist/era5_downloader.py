"""ERA5 climate data downloader for experimental warming sites.

This module downloads hourly ERA5 reanalysis data for experimental sites
and applies warming treatment offsets to generate control and treatment
climate forcing files.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import cdsapi
    import pandas as pd
    import xarray as xr

# Try to import optional dependencies
try:
    import cdsapi
except ImportError:
    cdsapi = None

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import xarray as xr
except ImportError:
    xr = None

from ecosim_co_scientist.data_models import ExperimentalSite


@dataclass
class ERA5Request:
    """ERA5 data request parameters."""

    latitude: float
    longitude: float
    start_date: datetime
    end_date: datetime
    output_path: Path

    # Variables needed for EcoSIM
    variables: list[str] = None

    def __post_init__(self):
        """Set default variables if not provided."""
        if self.variables is None:
            # Default EcoSIM climate variables
            self.variables = [
                "2m_temperature",  # TMPH
                "10m_u_component_of_wind",  # For wind speed
                "10m_v_component_of_wind",  # For wind speed
                "total_precipitation",  # RAINH
                "surface_solar_radiation_downwards",  # SRADH
                "2m_dewpoint_temperature",  # For vapor pressure
            ]

    @property
    def year_range(self) -> list[str]:
        """Get list of years in request.

        Examples:
            >>> from datetime import datetime
            >>> req = ERA5Request(
            ...     latitude=55.0,
            ...     longitude=12.0,
            ...     start_date=datetime(2005, 1, 1),
            ...     end_date=datetime(2007, 12, 31),
            ...     output_path=Path("output.nc")
            ... )
            >>> req.year_range
            ['2005', '2006', '2007']
        """
        years = []
        year = self.start_date.year
        while year <= self.end_date.year:
            years.append(str(year))
            year += 1
        return years

    @property
    def bounding_box(self) -> tuple[float, float, float, float]:
        """Get bounding box for request (N, W, S, E).

        Uses 0.5° buffer around point for better interpolation.

        Examples:
            >>> req = ERA5Request(
            ...     latitude=55.0,
            ...     longitude=12.0,
            ...     start_date=datetime(2005, 1, 1),
            ...     end_date=datetime(2007, 12, 31),
            ...     output_path=Path("output.nc")
            ... )
            >>> req.bounding_box
            (55.5, 11.5, 54.5, 12.5)
        """
        buffer = 0.5
        return (
            self.latitude + buffer,  # North
            self.longitude - buffer,  # West
            self.latitude - buffer,  # South
            self.longitude + buffer,  # East
        )


def create_request_from_site(
    site: ExperimentalSite,
    output_dir: Path,
    reference_year: int = 2010,
) -> Optional[ERA5Request]:
    """Create ERA5 request from experimental site metadata.

    Args:
        site: Experimental site with metadata
        output_dir: Directory for output files
        reference_year: Year to use for climate data (default: 2010)

    Returns:
        ERA5Request or None if site lacks required metadata

    Examples:
        >>> from pathlib import Path
        >>> from ecosim_co_scientist.data_models import Coordinates, ExperimentalSite
        >>> site = ExperimentalSite(
        ...     source_id="Test 2020",
        ...     location_text="Test site",
        ...     ecosystem_text="forest",
        ...     warming_method_text="greenhouse",
        ...     coordinates=Coordinates(latitude=55.0, longitude=12.0),
        ...     temperature_increase_c=2.0,
        ...     warming_duration_months=[12]
        ... )
        >>> req = create_request_from_site(site, Path("output"))
        >>> req is not None
        True
        >>> req.latitude
        55.0
    """
    if not site.coordinates:
        return None

    if not site.warming_duration_months:
        return None

    # Use maximum duration
    duration_months = max(site.warming_duration_months)

    # Create date range
    start_date = datetime(reference_year, 1, 1)
    end_date = start_date + timedelta(days=duration_months * 30)  # Approximate

    # Create output filename
    site_id = site.source_id.split()[0].replace(" ", "_")
    output_file = output_dir / f"{site_id}_era5_{reference_year}.nc"

    return ERA5Request(
        latitude=site.coordinates.latitude,
        longitude=site.coordinates.longitude,
        start_date=start_date,
        end_date=end_date,
        output_path=output_file,
    )


def download_era5_data(request: ERA5Request) -> Path:
    """Download ERA5 data for a request.

    Args:
        request: ERA5Request with parameters

    Returns:
        Path to downloaded file

    Note:
        Requires CDS API credentials configured in ~/.cdsapirc
    """
    if cdsapi is None:
        raise ImportError("cdsapi is required for downloading ERA5 data. Install with: pip install cdsapi")

    client = cdsapi.Client()

    # Format bounding box for CDS API
    bbox = request.bounding_box

    # Prepare request
    cds_request = {
        "product_type": "reanalysis",
        "format": "netcdf",
        "variable": request.variables,
        "year": request.year_range,
        "month": [f"{m:02d}" for m in range(1, 13)],
        "day": [f"{d:02d}" for d in range(1, 32)],
        "time": [f"{h:02d}:00" for h in range(24)],
        "area": bbox,  # N, W, S, E
    }

    # Download
    print(f"Downloading ERA5 data for {request.latitude:.2f}°, {request.longitude:.2f}°")
    print(f"  Period: {request.start_date.date()} to {request.end_date.date()}")
    print(f"  Output: {request.output_path}")

    request.output_path.parent.mkdir(parents=True, exist_ok=True)

    client.retrieve("reanalysis-era5-single-levels", cds_request, str(request.output_path))

    print(f"  ✓ Downloaded to {request.output_path}")
    return request.output_path


def apply_warming_treatment(
    control_file: Path,
    warming_c: float,
    output_file: Path,
) -> Path:
    """Apply warming treatment to ERA5 data.

    Creates a treatment file by adding a temperature offset to the control file.

    Args:
        control_file: Path to control (unmodified) ERA5 file
        warming_c: Temperature increase in degrees Celsius
        output_file: Path for output (warmed) file

    Returns:
        Path to treatment file

    Examples:
        >>> # This would work with real ERA5 data
        >>> # warmed = apply_warming_treatment(
        >>> #     control_file=Path("control.nc"),
        >>> #     warming_c=2.5,
        >>> #     output_file=Path("treatment.nc")
        >>> # )
    """
    if xr is None:
        raise ImportError("xarray is required. Install with: pip install xarray")

    print(f"Applying +{warming_c:.2f}°C warming treatment")
    print(f"  Control : {control_file}")
    print(f"  Treatment: {output_file}")

    # Load control data
    ds = xr.open_dataset(control_file)

    # Apply temperature offset
    if "t2m" in ds:  # 2m temperature
        ds["t2m"] = ds["t2m"] + warming_c

    if "d2m" in ds:  # dewpoint temperature (affects vapor pressure)
        # Dewpoint also increases, but typically less than air temp
        # Use conservative factor of 0.7
        ds["d2m"] = ds["d2m"] + (warming_c * 0.7)

    # Save treatment file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    ds.to_netcdf(output_file)
    ds.close()

    print(f"  ✓ Created treatment file")
    return output_file


def convert_era5_to_ecosim_format(
    era5_file: Path,
    output_file: Path,
    site_name: str,
) -> Path:
    """Convert ERA5 NetCDF to EcoSIM climate format.

    EcoSIM expects:
    - Dimensions: year, day, hour, ngrid
    - Variables: TMPH (°C), WINDH (m/s), RAINH (mm/hr), SRADH (W/m²), DWPTH (kPa)

    Args:
        era5_file: Path to ERA5 NetCDF file
        output_file: Path for EcoSIM-formatted output
        site_name: Name of site for metadata

    Returns:
        Path to converted file

    Examples:
        >>> # This would work with real ERA5 data
        >>> # ecosim_file = convert_era5_to_ecosim_format(
        >>> #     era5_file=Path("era5.nc"),
        >>> #     output_file=Path("ecosim_climate.nc"),
        >>> #     site_name="Test_Site"
        >>> # )
    """
    if xr is None or pd is None:
        raise ImportError("xarray and pandas are required. Install with: pip install xarray pandas")

    print(f"Converting ERA5 to EcoSIM format")
    print(f"  Input : {era5_file}")
    print(f"  Output: {output_file}")

    # Load ERA5 data
    ds = xr.open_dataset(era5_file)

    # Extract first grid point (since we requested small area)
    if "latitude" in ds.dims and "longitude" in ds.dims:
        ds = ds.isel(latitude=0, longitude=0)

    # Prepare time indexing
    times = pd.to_datetime(ds["time"].values)
    years = times.year.unique()

    # Initialize EcoSIM dataset structure
    n_years = len(years)
    n_days = 366  # Use 366 to accommodate leap years
    n_hours = 24
    n_grid = 1

    # Create new dataset
    ecosim_ds = xr.Dataset(
        coords={
            "year": ("year", list(range(n_years))),
            "day": ("day", list(range(1, n_days + 1))),
            "hour": ("hour", list(range(n_hours))),
            "ngrid": ("ngrid", [0]),
        }
    )

    # Temperature (K to °C)
    if "t2m" in ds:
        tmph = xr.DataArray(
            dims=("year", "day", "hour", "ngrid"),
            coords=ecosim_ds.coords,
        )
        # Fill with temperature data (convert K to °C)
        for i, year in enumerate(years):
            year_data = ds.sel(time=times[times.year == year])
            temps_c = year_data["t2m"].values - 273.15  # K to °C
            # Reshape to (day, hour)
            # This is simplified - real implementation needs proper date handling
            tmph[i, :len(temps_c)//24, :, 0] = temps_c.reshape(-1, 24)[:366, :]

        ecosim_ds["TMPH"] = tmph
        ecosim_ds["TMPH"].attrs["long_name"] = "hourly air temperature"
        ecosim_ds["TMPH"].attrs["units"] = "oC"

    # Add other variables similarly (WINDH, RAINH, SRADH, DWPTH)
    # Simplified for now - full implementation would process all variables

    # Save
    output_file.parent.mkdir(parents=True, exist_ok=True)
    ecosim_ds.to_netcdf(output_file)

    print(f"  ✓ Converted to EcoSIM format")
    return output_file
