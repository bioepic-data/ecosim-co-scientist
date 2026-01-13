"""Soil properties module with ecosystem-based defaults.

This module provides soil property data for EcoSIM grid files.
Uses ecosystem-type defaults when HWSD data is unavailable.
"""

from dataclasses import dataclass
from typing import Optional

import numpy as np

from ecosim_co_scientist.data_models import EcosystemType, ExperimentalSite


@dataclass
class SoilLayer:
    """Properties for a single soil layer."""

    depth_m: float  # Depth to bottom of layer (m)
    bulk_density_mg_m3: float  # Bulk density (Mg/m³)
    sand_fraction: float  # Sand content (kg/Mg, i.e., fraction * 1000)
    silt_fraction: float  # Silt content (kg/Mg)
    clay_fraction: float  # Clay content (kg/Mg)
    ph: float  # pH
    organic_c_kg_mg: float  # Organic C (kg C/Mg soil)
    organic_n_g_mg: float  # Organic N (g N/Mg soil)
    nh4_g_mg: float  # NH4-N (g N/Mg soil)
    no3_g_mg: float  # NO3-N (g N/Mg soil)


@dataclass
class SoilProfile:
    """Complete soil profile with multiple layers."""

    layers: list[SoilLayer]
    site_name: str
    latitude: float
    longitude: float
    altitude_m: float = 0.0
    mean_annual_temp_c: float = 10.0


def create_ecosystem_default_profile(
    ecosystem: EcosystemType,
    site: ExperimentalSite,
    n_layers: int = 20,
) -> SoilProfile:
    """Create default soil profile based on ecosystem type.

    Args:
        ecosystem: Ecosystem type
        site: Experimental site metadata
        n_layers: Number of soil layers (default: 20)

    Returns:
        SoilProfile with ecosystem-appropriate defaults

    Examples:
        >>> from ecosim_co_scientist.data_models import EcosystemType, ExperimentalSite, Coordinates
        >>> site = ExperimentalSite(
        ...     source_id="Test",
        ...     location_text="Test",
        ...     ecosystem_text="forest",
        ...     warming_method_text="test",
        ...     ecosystem=EcosystemType.FOREST,
        ...     coordinates=Coordinates(latitude=45.0, longitude=-120.0)
        ... )
        >>> profile = create_ecosystem_default_profile(EcosystemType.FOREST, site)
        >>> len(profile.layers)
        20
        >>> profile.layers[0].depth_m
        0.05
    """
    # Ecosystem-specific defaults
    defaults = {
        EcosystemType.TUNDRA: {
            "bulk_density": 0.8,  # Low due to high organic matter
            "sand": 400,  # 40%
            "silt": 400,
            "clay": 200,
            "ph": 5.0,
            "organic_c": 150,  # High organic C
            "organic_n": 8,
            "nh4": 2.0,
            "no3": 1.0,
        },
        EcosystemType.FOREST: {
            "bulk_density": 1.2,
            "sand": 450,
            "silt": 350,
            "clay": 200,
            "ph": 5.5,
            "organic_c": 80,
            "organic_n": 4.5,
            "nh4": 1.5,
            "no3": 2.0,
        },
        EcosystemType.SHRUB_HEATHLAND: {
            "bulk_density": 1.0,
            "sand": 500,
            "silt": 300,
            "clay": 200,
            "ph": 5.2,
            "organic_c": 100,
            "organic_n": 5.5,
            "nh4": 1.8,
            "no3": 1.5,
        },
        EcosystemType.GRASSLAND_MEADOW_PRAIRIE: {
            "bulk_density": 1.3,
            "sand": 400,
            "silt": 400,
            "clay": 200,
            "ph": 6.5,
            "organic_c": 60,
            "organic_n": 4.0,
            "nh4": 1.2,
            "no3": 2.5,
        },
        EcosystemType.CROPLAND: {
            "bulk_density": 1.4,
            "sand": 450,
            "silt": 350,
            "clay": 200,
            "ph": 6.8,
            "organic_c": 30,
            "organic_n": 2.5,
            "nh4": 3.0,  # Higher due to fertilization
            "no3": 5.0,
        },
        EcosystemType.PEAT: {
            "bulk_density": 0.5,  # Very low
            "sand": 200,
            "silt": 300,
            "clay": 500,
            "ph": 4.5,
            "organic_c": 400,  # Very high
            "organic_n": 20,
            "nh4": 2.5,
            "no3": 0.5,
        },
    }

    # Get defaults for this ecosystem
    eco_defaults = defaults.get(ecosystem, defaults[EcosystemType.FOREST])

    # Create layers with exponential depth distribution
    layers = []
    for i in range(n_layers):
        # Exponential depth: shallow layers near surface
        if i == 0:
            depth = 0.05  # 5 cm
        elif i < 5:
            depth = 0.05 + i * 0.05  # 5 cm increments to 30 cm
        elif i < 10:
            depth = 0.30 + (i - 5) * 0.10  # 10 cm increments to 80 cm
        else:
            depth = 0.80 + (i - 10) * 0.20  # 20 cm increments to 2.8 m

        # Decrease organic matter with depth
        depth_factor = np.exp(-depth / 0.3)  # Exponential decay

        # Increase bulk density with depth
        bd = eco_defaults["bulk_density"] * (1 + depth * 0.2)

        layer = SoilLayer(
            depth_m=depth,
            bulk_density_mg_m3=bd,
            sand_fraction=eco_defaults["sand"],
            silt_fraction=eco_defaults["silt"],
            clay_fraction=eco_defaults["clay"],
            ph=eco_defaults["ph"] + depth * 0.5,  # pH increases slightly with depth
            organic_c_kg_mg=eco_defaults["organic_c"] * depth_factor,
            organic_n_g_mg=eco_defaults["organic_n"] * depth_factor,
            nh4_g_mg=eco_defaults["nh4"] * depth_factor,
            no3_g_mg=eco_defaults["no3"] * depth_factor,
        )
        layers.append(layer)

    # Create profile
    profile = SoilProfile(
        layers=layers,
        site_name=site.source_id,
        latitude=site.coordinates.latitude if site.coordinates else 0.0,
        longitude=site.coordinates.longitude if site.coordinates else 0.0,
        altitude_m=site.coordinates.altitude if site.coordinates and site.coordinates.altitude else 0.0,
        mean_annual_temp_c=10.0,  # Default, could be calculated from climate
    )

    return profile
