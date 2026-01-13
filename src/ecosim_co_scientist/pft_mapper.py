"""Plant Functional Type (PFT) mapping for EcoSIM.

Maps ecosystem types to EcoSIM PFT codes and generates PFT NetCDF files.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    import numpy as np
    import xarray as xr
except ImportError:
    np = None
    xr = None

from ecosim_co_scientist.data_models import EcosystemType, ExperimentalSite


@dataclass
class PFTCode:
    """EcoSIM Plant Functional Type code."""

    code: str
    name: str
    description: str


# EcoSIM PFT codes mapping
PFT_CODES = {
    EcosystemType.TUNDRA: PFTCode("DGS", "Deciduous Grass/Shrub", "Arctic/alpine tundra vegetation"),
    EcosystemType.FOREST: PFTCode("DBF", "Deciduous Broadleaf Forest", "Temperate deciduous forest"),
    EcosystemType.SHRUB_HEATHLAND: PFTCode("DSH", "Deciduous Shrub", "Heathland and shrubland"),
    EcosystemType.GRASSLAND_MEADOW_PRAIRIE: PFTCode("C3G", "C3 Grass", "Temperate grassland"),
    EcosystemType.CROPLAND: PFTCode("CRP", "Crop", "Agricultural cropland"),
    EcosystemType.PEAT: PFTCode("WET", "Wetland", "Peatland vegetation"),
}


def map_ecosystem_to_pft(ecosystem: EcosystemType) -> PFTCode:
    """Map ecosystem type to EcoSIM PFT code.

    Args:
        ecosystem: Ecosystem type

    Returns:
        PFTCode for this ecosystem

    Examples:
        >>> pft = map_ecosystem_to_pft(EcosystemType.FOREST)
        >>> pft.code
        'DBF'
        >>> pft.name
        'Deciduous Broadleaf Forest'
    """
    return PFT_CODES.get(ecosystem, PFT_CODES[EcosystemType.GRASSLAND_MEADOW_PRAIRIE])


def create_pft_file(
    site: ExperimentalSite,
    pft_code: PFTCode,
    output_path: Path,
    start_year: int = 2010,
    n_years: int = 2,
) -> Path:
    """Create EcoSIM PFT NetCDF file.

    Args:
        site: Experimental site metadata
        pft_code: PFT code to use
        output_path: Path for output NetCDF file
        start_year: Starting year
        n_years: Number of years

    Returns:
        Path to created file
    """
    if np is None or xr is None:
        raise ImportError("numpy and xarray required")

    print(f"Generating PFT file for {site.source_id[:60]}")
    print(f"  PFT: {pft_code.code} ({pft_code.name})")
    print(f"  Output: {output_path}")

    # Dimensions
    ntopou = 1
    maxpfts = 1
    maxpmgt = 1
    nchar1 = 50
    ncharmgnt = 200

    # Create dataset
    ds = xr.Dataset(
        coords={
            "year": ("year", list(range(n_years))),
            "ntopou": ("ntopou", [0]),
            "maxpfts": ("maxpfts", [0]),
            "maxpmgt": ("maxpmgt", [0]),
            "nchar1": ("nchar1", list(range(nchar1))),
            "ncharmgnt": ("ncharmgnt", list(range(ncharmgnt))),
        }
    )

    # Grid mapping
    ds["NH1"] = (("ntopou",), np.array([1], dtype=np.int32))
    ds["NH1"].attrs["long_name"] = "Starting column from the west for a topo unit"

    ds["NH2"] = (("ntopou",), np.array([1], dtype=np.int32))
    ds["NH2"].attrs["long_name"] = "Starting row from the north for a topo unit"

    ds["NV1"] = (("ntopou",), np.array([1], dtype=np.int32))
    ds["NV1"].attrs["long_name"] = "Ending column at the east for a topo unit"

    ds["NV2"] = (("ntopou",), np.array([1], dtype=np.int32))
    ds["NV2"].attrs["long_name"] = "Ending row at the south for a topo unit"

    # Number of PFTs
    ds["NZ"] = (("ntopou",), np.array([1], dtype=np.int32))
    ds["NZ"].attrs["long_name"] = "Number of pfts on a topo unit"

    # PFT data flag
    ds["pft_dflag"] = np.array(0, dtype=np.int32)
    ds["pft_dflag"].attrs["long_name"] = "Flag for plant management data"
    ds["pft_dflag"].attrs["flags"] = "-1 no pft data, 0 only plantation information, 1 transient pft data"

    # PFT type string
    pft_type_str = np.zeros((n_years, ntopou, maxpfts, nchar1), dtype='S1')
    pft_str = pft_code.code.ljust(nchar1)[:nchar1]
    for i in range(len(pft_str)):
        pft_type_str[:, :, :, i] = pft_str[i].encode('utf-8')

    ds["pft_type"] = (("year", "ntopou", "maxpfts", "nchar1"), pft_type_str)

    # Planting info
    planting_info = f"Natural {pft_code.name.lower()} vegetation".ljust(ncharmgnt)[:ncharmgnt]
    pft_pltinfo_arr = np.zeros((n_years, ntopou, maxpfts, ncharmgnt), dtype='S1')
    for i in range(len(planting_info)):
        pft_pltinfo_arr[:, :, :, i] = planting_info[i].encode('utf-8')

    ds["pft_pltinfo"] = (("year", "ntopou", "maxpfts", "ncharmgnt"), pft_pltinfo_arr)
    ds["pft_pltinfo"].attrs["long_name"] = "string containing planting information"

    # Number of management events
    ds["nmgnts"] = (("year", "ntopou", "maxpfts"), np.zeros((n_years, ntopou, maxpfts), dtype=np.int16))
    ds["nmgnts"].attrs["long_name"] = "Number of managements for a given pft in given topo unit in a year"

    # Management info (empty for natural vegetation)
    pft_mgmt_arr = np.zeros((n_years, ntopou, maxpfts, maxpmgt, ncharmgnt), dtype='S1')
    ds["pft_mgmt"] = (("year", "ntopou", "maxpfts", "maxpmgt", "ncharmgnt"), pft_mgmt_arr)
    ds["pft_mgmt"].attrs["long_name"] = "string containing plant management information"

    # Global attributes
    ds.attrs["title"] = f"EcoSIM PFT file for {site.source_id}"
    ds.attrs["source"] = "Generated by EcoSIM Co-Scientist"
    ds.attrs["pft_code"] = pft_code.code
    ds.attrs["pft_name"] = pft_code.name
    ds.attrs["ecosystem"] = site.ecosystem_text

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ds.to_netcdf(output_path)

    print(f"  ✓ Created PFT file")
    return output_path
