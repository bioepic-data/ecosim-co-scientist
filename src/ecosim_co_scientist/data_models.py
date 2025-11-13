"""Data models for experimental warming nitrogen cycle studies.

These models represent experimental sites, nitrogen measurements, and related
metadata from the warming-nitrogen meta-analysis database.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class EcosystemType(str, Enum):
    """Major ecosystem types in the meta-analysis."""

    TUNDRA = "tundra"
    FOREST = "forest"
    SHRUB_HEATHLAND = "shrub/heathland"
    GRASSLAND_MEADOW_PRAIRIE = "grassland/meadow/prairie"
    CROPLAND = "cropland"
    PEAT = "peat"


class WarmingMethod(str, Enum):
    """Methods used for experimental warming."""

    GREENHOUSE = "greenhouse"
    HEATING_CABLE = "heating cable"
    INFRARED_RADIATOR = "infrared radiator"
    OPEN_TOP_CHAMBER = "open top chamber"
    CURTAIN = "curtain"


class WarmingTiming(str, Enum):
    """Timing of warming application."""

    ALL_DAY = "all day warming"
    NIGHT_TIME = "night time warming"
    DAY_TIME = "day time warming"
    GROWING_SEASON = "growing season"


class WarmingSeason(str, Enum):
    """Season during which warming was applied."""

    ALL_YEAR = "all year"
    GROWING_SEASON = "growing season"
    WINTER = "winter"


class NitrogenVariable(str, Enum):
    """Types of nitrogen cycle measurements."""

    N2O = "N2O"
    GROSS_N_MINERALIZATION = "gross N mineralization"
    NET_N_MINERALIZATION = "net N mineralization"
    NET_NITRIFICATION = "net nitrification"
    GROSS_NITRIFICATION = "gross nitrification"
    DENITRIFICATION = "denitrification"
    N_IMMOBILIZATION = "N_immobilization"
    N_FIXATION = "N_fixation"
    N_LEACHING = "N leaching"
    PLANT_N = "plant N"
    SOIL_INORGANIC_N = "soil inorganic N"
    MICROBIAL_N = "microbial N"
    SOIL_N = "soil N"
    SOIL_MOISTURE = "soil moisture"


class Coordinates(BaseModel):
    """Geographic coordinates of an experimental site."""

    latitude: float = Field(
        ..., ge=-90, le=90, description="Latitude in decimal degrees"
    )
    longitude: float = Field(
        ..., ge=-180, le=180, description="Longitude in decimal degrees"
    )
    altitude: Optional[float] = Field(
        None, description="Altitude above sea level in meters"
    )

    @field_validator("latitude", "longitude")
    @classmethod
    def validate_coordinates(cls, v: float) -> float:
        """Ensure coordinates are valid numbers.

        Examples:
            >>> coords = Coordinates(latitude=45.5, longitude=-122.6)
            >>> coords.latitude
            45.5
            >>> coords.longitude
            -122.6
        """
        return float(v)


class ExperimentalSite(BaseModel):
    """An experimental warming study site.

    Represents a single location where warming experiments were conducted,
    including metadata about the treatment, ecosystem type, and geographic location.
    """

    source_id: str = Field(..., description="Citation identifier for the study")
    coordinates: Optional[Coordinates] = Field(
        None, description="Geographic location of the site"
    )
    location_text: str = Field(..., description="Human-readable location description")
    ecosystem: Optional[EcosystemType] = Field(None, description="Ecosystem type")
    ecosystem_text: str = Field(..., description="Original ecosystem description")
    warming_method: Optional[WarmingMethod] = Field(
        None, description="Method used for warming"
    )
    warming_method_text: str = Field(
        ..., description="Detailed description of warming method"
    )
    temperature_increase_c: Optional[float] = Field(
        None, description="Temperature increase in degrees Celsius", ge=0
    )
    warming_duration_months: Optional[list[int]] = Field(
        None, description="List of measurement timepoints in months"
    )
    warming_timing: Optional[WarmingTiming] = Field(
        None, description="Time of day when warming was applied"
    )
    warming_season: Optional[WarmingSeason] = Field(
        None, description="Season when warming was applied"
    )

    @property
    def site_id(self) -> str:
        """Generate a unique site identifier.

        Examples:
            >>> site = ExperimentalSite(
            ...     source_id="Smith 2020",
            ...     location_text="Alaska",
            ...     ecosystem_text="tundra",
            ...     warming_method_text="greenhouse"
            ... )
            >>> site.site_id.startswith("Smith")
            True
        """
        # Use first author and year from source_id
        return self.source_id.split("_")[0].replace(" ", "_")

    @property
    def max_warming_duration_months(self) -> Optional[int]:
        """Get the maximum warming duration.

        Examples:
            >>> site = ExperimentalSite(
            ...     source_id="Test",
            ...     location_text="Test",
            ...     ecosystem_text="forest",
            ...     warming_method_text="cables",
            ...     warming_duration_months=[1, 3, 6, 12]
            ... )
            >>> site.max_warming_duration_months
            12
        """
        if self.warming_duration_months:
            return max(self.warming_duration_months)
        return None


class NitrogenMeasurement(BaseModel):
    """A nitrogen cycle measurement from a warming experiment.

    Represents a single observation of a nitrogen variable (e.g., N2O flux,
    mineralization rate) with treatment and control values.
    """

    source_id: str = Field(..., description="Citation identifier linking to site")
    variable: NitrogenVariable = Field(..., description="Type of N measurement")
    treatment_mean: float = Field(..., description="Mean value in warmed treatment")
    control_mean: float = Field(..., description="Mean value in control plots")
    treatment_sd: Optional[float] = Field(None, description="Standard deviation of treatment", ge=0)
    control_sd: Optional[float] = Field(None, description="Standard deviation of control", ge=0)
    treatment_n: Optional[int] = Field(None, description="Sample size for treatment", ge=1)
    control_n: Optional[int] = Field(None, description="Sample size for control", ge=1)
    duration_months: Optional[int] = Field(
        None, description="Duration of experiment in months", ge=0
    )
    unit: str = Field(..., description="Unit of measurement")
    other_conditions: Optional[str] = Field(
        None, description="Additional experimental conditions"
    )

    @property
    def warming_effect(self) -> float:
        """Calculate the warming effect as difference between treatment and control.

        Examples:
            >>> meas = NitrogenMeasurement(
            ...     source_id="Test",
            ...     variable=NitrogenVariable.N2O,
            ...     treatment_mean=5.0,
            ...     control_mean=3.0,
            ...     unit="mg N/m2/day"
            ... )
            >>> meas.warming_effect
            2.0
        """
        return self.treatment_mean - self.control_mean

    @property
    def warming_effect_pct(self) -> Optional[float]:
        """Calculate the warming effect as percent change from control.

        Examples:
            >>> meas = NitrogenMeasurement(
            ...     source_id="Test",
            ...     variable=NitrogenVariable.N2O,
            ...     treatment_mean=6.0,
            ...     control_mean=3.0,
            ...     unit="mg N/m2/day"
            ... )
            >>> meas.warming_effect_pct
            100.0
        """
        if self.control_mean == 0:
            return None
        return (self.warming_effect / abs(self.control_mean)) * 100


class SiteInventory(BaseModel):
    """Collection of experimental sites with summary statistics."""

    sites: list[ExperimentalSite] = Field(
        default_factory=list, description="List of experimental sites"
    )

    @property
    def n_sites(self) -> int:
        """Total number of sites.

        Examples:
            >>> inv = SiteInventory(sites=[])
            >>> inv.n_sites
            0
        """
        return len(self.sites)

    @property
    def sites_with_coordinates(self) -> list[ExperimentalSite]:
        """Get sites that have valid coordinates.

        Examples:
            >>> site1 = ExperimentalSite(
            ...     source_id="Test1",
            ...     location_text="Alaska",
            ...     ecosystem_text="tundra",
            ...     warming_method_text="greenhouse",
            ...     coordinates=Coordinates(latitude=65.0, longitude=-150.0)
            ... )
            >>> site2 = ExperimentalSite(
            ...     source_id="Test2",
            ...     location_text="Unknown",
            ...     ecosystem_text="forest",
            ...     warming_method_text="cables"
            ... )
            >>> inv = SiteInventory(sites=[site1, site2])
            >>> len(inv.sites_with_coordinates)
            1
        """
        return [s for s in self.sites if s.coordinates is not None]

    def by_ecosystem(self) -> dict[EcosystemType, list[ExperimentalSite]]:
        """Group sites by ecosystem type.

        Returns:
            Dictionary mapping ecosystem types to lists of sites
        """
        result: dict[EcosystemType, list[ExperimentalSite]] = {}
        for site in self.sites:
            if site.ecosystem:
                if site.ecosystem not in result:
                    result[site.ecosystem] = []
                result[site.ecosystem].append(site)
        return result
