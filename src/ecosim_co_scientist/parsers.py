"""Parsers for experimental warming meta-analysis data files.

This module provides functions to parse TSV files containing experimental
site metadata and nitrogen cycle measurements.
"""

import re
from pathlib import Path
from typing import Optional

import pandas as pd

from ecosim_co_scientist.data_models import (
    Coordinates,
    EcosystemType,
    ExperimentalSite,
    NitrogenMeasurement,
    NitrogenVariable,
    SiteInventory,
    WarmingMethod,
    WarmingSeason,
    WarmingTiming,
)


def parse_coordinates(coord_str: str) -> Optional[Coordinates]:
    """Parse coordinate string into Coordinates object.

    Handles various formats:
    - Decimal degrees: "65.5°N, 150.3°W"
    - Degrees/minutes: "68°38'N,149°34'W"
    - Mixed formats

    Args:
        coord_str: String containing latitude and longitude

    Returns:
        Coordinates object or None if parsing fails

    Examples:
        >>> coords = parse_coordinates("65.5°N, 150.3°W")
        >>> coords.latitude
        65.5
        >>> coords.longitude
        -150.3

        >>> coords = parse_coordinates("68°38'N,149°34'W")
        >>> round(coords.latitude, 2)
        68.63
        >>> round(coords.longitude, 2)
        -149.57

        >>> parse_coordinates("invalid") is None
        True
    """
    if not coord_str or pd.isna(coord_str):
        return None

    try:
        # Pattern for decimal degrees or degrees/minutes
        # Matches: 68°38'N or 68.5°N or 68.5N
        pattern = r"([\d.]+)°?(?:'?(\d+)')?([NS])[,\s]+([\d.]+)°?(?:'?(\d+)')?([EW])"
        match = re.search(pattern, coord_str)

        if not match:
            return None

        lat_deg, lat_min, lat_dir, lon_deg, lon_min, lon_dir = match.groups()

        # Convert to decimal degrees
        latitude = float(lat_deg)
        if lat_min:
            latitude += float(lat_min) / 60
        if lat_dir == "S":
            latitude = -latitude

        longitude = float(lon_deg)
        if lon_min:
            longitude += float(lon_min) / 60
        if lon_dir == "W":
            longitude = -longitude

        return Coordinates(latitude=latitude, longitude=longitude)

    except (ValueError, AttributeError):
        return None


def parse_temperature_increase(temp_str: str) -> Optional[float]:
    """Parse temperature increase string to extract numeric value.

    Args:
        temp_str: String describing temperature increase

    Returns:
        Temperature increase in degrees Celsius, or None

    Examples:
        >>> parse_temperature_increase("5")
        5.0

        >>> parse_temperature_increase("3.5")
        3.5

        >>> parse_temperature_increase("1.5-2")
        1.75

        >>> parse_temperature_increase("3-5°C in air temperature")
        4.0

        >>> parse_temperature_increase("invalid") is None
        True
    """
    if not temp_str or pd.isna(temp_str):
        return None

    try:
        # Remove non-numeric characters except numbers, decimal points, and dashes
        clean_str = re.sub(r"[^0-9.\-]", " ", str(temp_str))

        # Extract all numbers
        numbers = re.findall(r"[\d.]+", clean_str)

        if not numbers:
            return None

        # If single number, return it
        if len(numbers) == 1:
            return float(numbers[0])

        # If range (e.g., "3-5"), return midpoint
        if len(numbers) >= 2:
            return (float(numbers[0]) + float(numbers[1])) / 2

    except (ValueError, AttributeError):
        return None

    return None


def parse_duration_months(duration_str: str) -> Optional[list[int]]:
    """Parse duration string to extract list of measurement timepoints.

    Args:
        duration_str: Comma-separated list of months

    Returns:
        List of integers representing months, or None

    Examples:
        >>> parse_duration_months("1,3,6,12")
        [1, 3, 6, 12]

        >>> parse_duration_months("24")
        [24]

        >>> parse_duration_months("invalid") is None
        True
    """
    if not duration_str or pd.isna(duration_str):
        return None

    try:
        # Split by comma and convert to integers
        months = [int(m.strip()) for m in str(duration_str).split(",") if m.strip()]
        return months if months else None
    except ValueError:
        return None


def map_ecosystem_type(ecosystem_text: str) -> Optional[EcosystemType]:
    """Map ecosystem text description to enum value.

    Args:
        ecosystem_text: Original ecosystem description

    Returns:
        EcosystemType enum or None

    Examples:
        >>> map_ecosystem_type("tundra")
        <EcosystemType.TUNDRA: 'tundra'>

        >>> map_ecosystem_type("Boreal forest")
        <EcosystemType.FOREST: 'forest'>

        >>> map_ecosystem_type("grassland")
        <EcosystemType.GRASSLAND_MEADOW_PRAIRIE: 'grassland/meadow/prairie'>
    """
    if not ecosystem_text or pd.isna(ecosystem_text):
        return None

    text_lower = str(ecosystem_text).lower()

    if "tundra" in text_lower:
        return EcosystemType.TUNDRA
    elif "forest" in text_lower:
        return EcosystemType.FOREST
    elif any(word in text_lower for word in ["shrub", "heath"]):
        return EcosystemType.SHRUB_HEATHLAND
    elif any(word in text_lower for word in ["grass", "meadow", "prairie", "steppe"]):
        return EcosystemType.GRASSLAND_MEADOW_PRAIRIE
    elif any(word in text_lower for word in ["crop", "wheat", "maize", "agriculture"]):
        return EcosystemType.CROPLAND
    elif "peat" in text_lower:
        return EcosystemType.PEAT

    return None


def map_warming_method(method_text: str) -> Optional[WarmingMethod]:
    """Map warming method text to enum value.

    Args:
        method_text: Original warming method description

    Returns:
        WarmingMethod enum or None

    Examples:
        >>> map_warming_method("greenhouse")
        <WarmingMethod.GREENHOUSE: 'greenhouse'>

        >>> map_warming_method("heating cable")
        <WarmingMethod.HEATING_CABLE: 'heating cable'>

        >>> map_warming_method("infrared heater")
        <WarmingMethod.INFRARED_RADIATOR: 'infrared radiator'>
    """
    if not method_text or pd.isna(method_text):
        return None

    text_lower = str(method_text).lower()

    if "greenhouse" in text_lower:
        return WarmingMethod.GREENHOUSE
    elif any(word in text_lower for word in ["cable", "heating wire"]):
        return WarmingMethod.HEATING_CABLE
    elif "infrared" in text_lower:
        return WarmingMethod.INFRARED_RADIATOR
    elif "otc" in text_lower or "open top chamber" in text_lower:
        return WarmingMethod.OPEN_TOP_CHAMBER
    elif "curtain" in text_lower:
        return WarmingMethod.CURTAIN

    return None


def map_warming_timing(timing_text: str) -> Optional[WarmingTiming]:
    """Map warming timing text to enum value.

    Args:
        timing_text: Original timing description

    Returns:
        WarmingTiming enum or None

    Examples:
        >>> map_warming_timing("all day warming")
        <WarmingTiming.ALL_DAY: 'all day warming'>

        >>> map_warming_timing("night time warming")
        <WarmingTiming.NIGHT_TIME: 'night time warming'>
    """
    if not timing_text or pd.isna(timing_text):
        return None

    text_lower = str(timing_text).lower()

    if "night" in text_lower:
        return WarmingTiming.NIGHT_TIME
    elif "day" in text_lower and "all" not in text_lower:
        return WarmingTiming.DAY_TIME
    elif "all day" in text_lower:
        return WarmingTiming.ALL_DAY
    elif "growing season" in text_lower:
        return WarmingTiming.GROWING_SEASON

    return None


def map_warming_season(season_text: str) -> Optional[WarmingSeason]:
    """Map warming season text to enum value.

    Args:
        season_text: Original season description

    Returns:
        WarmingSeason enum or None

    Examples:
        >>> map_warming_season("all year")
        <WarmingSeason.ALL_YEAR: 'all year'>

        >>> map_warming_season("growing season")
        <WarmingSeason.GROWING_SEASON: 'growing season'>
    """
    if not season_text or pd.isna(season_text):
        return None

    text_lower = str(season_text).lower()

    if "all year" in text_lower:
        return WarmingSeason.ALL_YEAR
    elif "growing season" in text_lower:
        return WarmingSeason.GROWING_SEASON
    elif "winter" in text_lower:
        return WarmingSeason.WINTER

    return None


def load_experiment_metadata(file_path: Path) -> SiteInventory:
    """Load experimental site metadata from TSV file.

    Args:
        file_path: Path to experiment-metadata.tsv file

    Returns:
        SiteInventory containing all parsed sites

    Examples:
        >>> from pathlib import Path
        >>> # This would load real data in practice
        >>> # inv = load_experiment_metadata(Path("experiment-metadata.tsv"))
        >>> # len(inv.sites) > 0
    """
    df = pd.read_csv(file_path, sep="\t", encoding="utf-8")

    sites = []
    for _, row in df.iterrows():
        # Parse coordinates
        coords = parse_coordinates(row.get("latitude and longitude coordinate", ""))

        # Parse temperature increase
        temp_increase = parse_temperature_increase(
            row.get("temperature-increase (degree C)", "")
        )

        # Parse duration
        duration_months = parse_duration_months(
            row.get("warming-duration (months)", "")
        )

        # Map categorical fields
        ecosystem = map_ecosystem_type(row.get("ecosystem-text", ""))
        warming_method = map_warming_method(row.get("warming-method", ""))
        warming_timing = map_warming_timing(row.get("warming-timing", ""))
        warming_season = map_warming_season(row.get("warming-season", ""))

        site = ExperimentalSite(
            source_id=row.get("source-id", ""),
            coordinates=coords,
            location_text=row.get("latitude and longitude text", ""),
            ecosystem=ecosystem,
            ecosystem_text=row.get("ecosystem-text", ""),
            warming_method=warming_method,
            warming_method_text=row.get("warming-method-text", ""),
            temperature_increase_c=temp_increase,
            warming_duration_months=duration_months,
            warming_timing=warming_timing,
            warming_season=warming_season,
        )
        sites.append(site)

    return SiteInventory(sites=sites)


def load_nitrogen_measurements(file_path: Path) -> list[NitrogenMeasurement]:
    """Load nitrogen cycle measurements from TSV file.

    Args:
        file_path: Path to N_measurements.tsv file

    Returns:
        List of NitrogenMeasurement objects

    Examples:
        >>> from pathlib import Path
        >>> # This would load real data in practice
        >>> # measurements = load_nitrogen_measurements(Path("N_measurements.tsv"))
        >>> # len(measurements) > 0
    """
    df = pd.read_csv(file_path, sep="\t", encoding="utf-8")

    measurements = []
    for _, row in df.iterrows():
        # Map variable name to enum
        var_name = row.get("variable", "")
        try:
            variable = NitrogenVariable(var_name)
        except ValueError:
            # Skip rows with unrecognized variables
            continue

        # Parse numeric values
        def safe_float(val):
            try:
                return float(val) if val and not pd.isna(val) else None
            except (ValueError, TypeError):
                return None

        def safe_int(val):
            try:
                return int(float(val)) if val and not pd.isna(val) else None
            except (ValueError, TypeError):
                return None

        def safe_string(val):
            """Convert value to string or None, handling NaN values."""
            if val is None or pd.isna(val):
                return None
            return str(val) if val else None

        treatment_mean = safe_float(row.get("treatment mean"))
        control_mean = safe_float(row.get("control mean"))

        # Skip if we don't have both treatment and control means
        if treatment_mean is None or control_mean is None:
            continue

        # Get unit, default to empty string if missing
        unit = safe_string(row.get("unit"))
        if not unit:
            unit = ""

        meas = NitrogenMeasurement(
            source_id=str(row.get("source-id", "")),
            variable=variable,
            treatment_mean=treatment_mean,
            control_mean=control_mean,
            treatment_sd=safe_float(row.get("treatment SD")),
            control_sd=safe_float(row.get("control SD")),
            treatment_n=safe_int(row.get("treatment n")),
            control_n=safe_int(row.get("control n")),
            duration_months=safe_int(row.get("duration_months")),
            unit=unit,
            other_conditions=safe_string(row.get("other_conditions")),
        )
        measurements.append(meas)

    return measurements
