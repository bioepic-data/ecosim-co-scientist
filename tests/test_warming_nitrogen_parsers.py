"""Unit tests for warming-nitrogen data parsers."""

import sys
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ecosim_co_scientist.data_models import (
    Coordinates,
    EcosystemType,
    NitrogenVariable,
    WarmingMethod,
)
from ecosim_co_scientist.parsers import (
    load_experiment_metadata,
    load_nitrogen_measurements,
    map_ecosystem_type,
    map_warming_method,
    parse_coordinates,
    parse_duration_months,
    parse_temperature_increase,
)


class TestCoordinateParsing:
    """Test coordinate string parsing."""

    def test_decimal_degrees(self):
        """Test parsing decimal degree format."""
        coords = parse_coordinates("65.5°N, 150.3°W")
        assert coords is not None
        assert coords.latitude == 65.5
        assert coords.longitude == -150.3

    def test_degrees_minutes(self):
        """Test parsing degrees/minutes format."""
        coords = parse_coordinates("68°38'N,149°34'W")
        assert coords is not None
        assert round(coords.latitude, 2) == 68.63
        assert round(coords.longitude, 2) == -149.57

    def test_southern_hemisphere(self):
        """Test parsing southern hemisphere coordinates."""
        coords = parse_coordinates("42°42'S 147°16'E")
        assert coords is not None
        assert coords.latitude < 0
        assert coords.longitude > 0

    def test_invalid_coordinates(self):
        """Test that invalid coordinates return None."""
        assert parse_coordinates("invalid") is None
        assert parse_coordinates("") is None
        assert parse_coordinates(None) is None


class TestTemperatureParsing:
    """Test temperature increase parsing."""

    @pytest.mark.parametrize(
        "input_str,expected",
        [
            ("5", 5.0),
            ("3.5", 3.5),
            ("1.5-2", 1.75),
            ("3-5°C in air temperature", 4.0),
            ("2.2", 2.2),
        ],
    )
    def test_valid_temperatures(self, input_str, expected):
        """Test parsing various temperature formats."""
        result = parse_temperature_increase(input_str)
        assert result == expected

    def test_invalid_temperature(self):
        """Test that invalid temperatures return None."""
        assert parse_temperature_increase("invalid") is None
        assert parse_temperature_increase("") is None


class TestDurationParsing:
    """Test duration string parsing."""

    def test_single_month(self):
        """Test parsing single month."""
        result = parse_duration_months("24")
        assert result == [24]

    def test_multiple_months(self):
        """Test parsing comma-separated months."""
        result = parse_duration_months("1,3,6,12")
        assert result == [1, 3, 6, 12]

    def test_months_with_spaces(self):
        """Test parsing months with spaces."""
        result = parse_duration_months("1, 3, 6, 12")
        assert result == [1, 3, 6, 12]

    def test_invalid_duration(self):
        """Test that invalid durations return None."""
        assert parse_duration_months("invalid") is None
        assert parse_duration_months("") is None


class TestCategoricalMapping:
    """Test mapping text descriptions to enum values."""

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("tundra", EcosystemType.TUNDRA),
            ("Boreal forest", EcosystemType.FOREST),
            ("grassland", EcosystemType.GRASSLAND_MEADOW_PRAIRIE),
            ("shrubland", EcosystemType.SHRUB_HEATHLAND),
            ("cropland", EcosystemType.CROPLAND),
        ],
    )
    def test_ecosystem_mapping(self, text, expected):
        """Test ecosystem type mapping."""
        assert map_ecosystem_type(text) == expected

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("greenhouse", WarmingMethod.GREENHOUSE),
            ("heating cable", WarmingMethod.HEATING_CABLE),
            ("infrared heater", WarmingMethod.INFRARED_RADIATOR),
            ("OTC", WarmingMethod.OPEN_TOP_CHAMBER),
            ("curtain", WarmingMethod.CURTAIN),
        ],
    )
    def test_warming_method_mapping(self, text, expected):
        """Test warming method mapping."""
        assert map_warming_method(text) == expected


class TestDataLoading:
    """Test loading real data files."""

    @pytest.fixture
    def data_dir(self):
        """Get path to test data directory."""
        return (
            Path(__file__).parent.parent
            / "hackathon-case_study-experimental_warming_nitrogen"
            / "derived"
        )

    def test_load_experiment_metadata(self, data_dir):
        """Test loading experiment metadata file."""
        metadata_file = data_dir / "experiment-metadata.tsv"
        if not metadata_file.exists():
            pytest.skip(f"Data file not found: {metadata_file}")

        inventory = load_experiment_metadata(metadata_file)

        # Check basic properties
        assert inventory.n_sites > 0
        assert len(inventory.sites_with_coordinates) > 0

        # Check that we can group by ecosystem
        by_ecosystem = inventory.by_ecosystem()
        assert len(by_ecosystem) > 0

        # Check that at least one site has complete metadata
        complete_sites = [
            s
            for s in inventory.sites
            if s.coordinates is not None
            and s.temperature_increase_c is not None
            and s.warming_duration_months is not None
        ]
        assert len(complete_sites) > 0

    def test_load_nitrogen_measurements(self, data_dir):
        """Test loading nitrogen measurements file."""
        measurements_file = data_dir / "N_measurements.tsv"
        if not measurements_file.exists():
            pytest.skip(f"Data file not found: {measurements_file}")

        measurements = load_nitrogen_measurements(measurements_file)

        # Check basic properties
        assert len(measurements) > 0

        # Check that measurements have required fields
        for meas in measurements[:5]:  # Check first 5
            assert meas.source_id
            assert isinstance(meas.variable, NitrogenVariable)
            assert isinstance(meas.treatment_mean, float)
            assert isinstance(meas.control_mean, float)
            assert isinstance(meas.unit, str)

        # Check that warming effects can be calculated
        n2o_measurements = [m for m in measurements if m.variable == NitrogenVariable.N2O]
        if n2o_measurements:
            for meas in n2o_measurements[:3]:
                effect = meas.warming_effect
                assert isinstance(effect, float)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
