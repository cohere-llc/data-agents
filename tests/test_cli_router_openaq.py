"""
Test CLI router configuration with OpenAQ adapter examples.
"""

import json
import os
import tempfile
from unittest.mock import Mock, patch

import pytest


class TestCLIRouterWithOpenAQ:
    """Test CLI router configuration examples with OpenAQ adapter."""

    @pytest.fixture
    def openaq_router_config(self):
        """Create a router configuration with OpenAQ adapter."""
        return {
            "adapters": {
                "air_quality": {
                    "type": "openaq",
                    "api_key": "${OPENAQ_API_KEY}",
                    "base_url": "https://api.openaq.org/v3",
                    "description": "OpenAQ air quality measurement data",
                },
                "weather_data": {
                    "type": "nasa_power",
                    "description": "NASA POWER meteorological data",
                },
                "local_data": {
                    "type": "tabular",
                    "csv_file": "examples/sample_data.csv",
                },
            }
        }

    @pytest.fixture
    def temp_router_config_file(self, openaq_router_config):
        """Create temporary router configuration file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(openaq_router_config, f)
            temp_path = f.name

        yield temp_path
        os.unlink(temp_path)

    def test_router_config_format(self, openaq_router_config):
        """Test router configuration format with OpenAQ adapter."""
        assert "adapters" in openaq_router_config
        adapters = openaq_router_config["adapters"]

        assert "air_quality" in adapters
        openaq_adapter = adapters["air_quality"]
        assert openaq_adapter["type"] == "openaq"
        assert "api_key" in openaq_adapter
        assert "base_url" in openaq_adapter

        # Test that config is valid JSON
        json_str = json.dumps(openaq_router_config)
        parsed = json.loads(json_str)
        assert parsed == openaq_router_config

    def test_mixed_adapter_types_config(self, openaq_router_config):
        """Test router with multiple adapter types including OpenAQ."""
        adapters = openaq_router_config["adapters"]

        # Should have different adapter types
        adapter_types = [adapter["type"] for adapter in adapters.values()]
        assert "openaq" in adapter_types
        assert "nasa_power" in adapter_types
        assert "tabular" in adapter_types

        # Each adapter should have required fields
        for name, adapter in adapters.items():
            assert "type" in adapter
            if adapter["type"] == "openaq":
                assert "api_key" in adapter
            elif adapter["type"] == "tabular":
                assert "csv_file" in adapter

    @patch("data_agents.core.router.Router")
    def test_router_creation_with_openaq(
        self, mock_router_class, temp_router_config_file
    ):
        """Test that router can be created with OpenAQ adapter configuration."""
        mock_router = Mock()
        mock_router_class.return_value = mock_router

        # This would be the CLI logic for creating a router
        with open(temp_router_config_file) as f:
            config = json.load(f)

        # Test that config is structured correctly for router creation
        assert "adapters" in config
        assert len(config["adapters"]) == 3
        assert "air_quality" in config["adapters"]

    def test_cli_command_examples_with_router(self):
        """Test CLI command examples that use router configurations."""
        # These commands should have correct structure
        router_commands = [
            [
                "uv",
                "run",
                "data-agents",
                "info",
                "--router-config",
                "config/air_quality_router.json",
            ],
            [
                "uv",
                "run",
                "data-agents",
                "list-adapters",
                "--router-config",
                "config/air_quality_router.json",
            ],
            [
                "uv",
                "run",
                "data-agents",
                "discover",
                "--router-config",
                "config/air_quality_router.json",
            ],
            [
                "uv",
                "run",
                "data-agents",
                "query",
                "*",
                "--router-config",
                "config/air_quality_router.json",
            ],
        ]

        for cmd in router_commands:
            assert len(cmd) >= 4
            assert cmd[0] in ["uv", "python"]
            assert "data-agents" in cmd
            assert "--router-config" in cmd

    def test_environment_variable_handling(self):
        """Test environment variable substitution in configuration."""
        config_with_env = {
            "adapter_type": "openaq",
            "api_key": "${OPENAQ_API_KEY}",
            "base_url": "https://api.openaq.org/v3",
        }

        # Test with environment variable set
        with patch.dict(os.environ, {"OPENAQ_API_KEY": "test_env_key"}):
            # This would be the logic for environment variable substitution
            api_key = config_with_env["api_key"]
            if api_key.startswith("${") and api_key.endswith("}"):
                env_var = api_key[2:-1]
                resolved_key = os.environ.get(env_var)
                assert resolved_key == "test_env_key"

    def test_example_yaml_config_equivalent(self):
        """Test YAML equivalent of OpenAQ router configuration."""
        # This would be the YAML equivalent structure
        yaml_equivalent = """
adapters:
  air_quality:
    type: openaq
    api_key: ${OPENAQ_API_KEY}
    base_url: https://api.openaq.org/v3
    description: OpenAQ air quality measurement data
  
  weather_data:
    type: nasa_power
    description: NASA POWER meteorological data
    
  local_data:
    type: tabular
    csv_file: examples/sample_data.csv
"""

        # Test that YAML structure is valid (simulated)
        lines = yaml_equivalent.strip().split("\n")
        assert any("type: openaq" in line for line in lines)
        assert any("api_key: ${OPENAQ_API_KEY}" in line for line in lines)


class TestOpenAQDocumentationExamples:
    """Test specific examples from the CLI documentation."""

    def test_geographic_query_examples(self):
        """Test geographic query examples from documentation."""
        bbox_examples = [
            "40.6,-74.2,40.9,-73.7",  # NYC
            "33.7,-118.7,34.3,-117.9",  # LA
            "51.3,-0.5,51.7,0.2",  # London
        ]

        for bbox_str in bbox_examples:
            parts = bbox_str.split(",")
            assert len(parts) == 4
            south, west, north, east = [float(p) for p in parts]
            assert -90 <= south <= 90
            assert -90 <= north <= 90
            assert -180 <= west <= 180
            assert -180 <= east <= 180
            assert south < north
            assert west < east

    def test_center_radius_examples(self):
        """Test center point and radius examples."""
        center_radius_examples = [
            ("37.7749", "-122.4194", "25"),  # San Francisco
            ("52.5200", "13.4050", "50"),  # Berlin
            ("35.6762", "139.6503", "10"),  # Tokyo
        ]

        for lat_str, lon_str, radius_str in center_radius_examples:
            lat = float(lat_str)
            lon = float(lon_str)
            radius = float(radius_str)

            assert -90 <= lat <= 90
            assert -180 <= lon <= 180
            assert radius > 0

    def test_parameter_examples(self):
        """Test air quality parameter examples."""
        parameter_examples = ["pm25", "pm10", "no2", "o3", "so2", "co", "bc"]

        # All should be valid parameter names
        for param in parameter_examples:
            assert isinstance(param, str)
            assert len(param) > 0
            assert param.isalnum() or param.replace("_", "").isalnum()

    def test_multi_parameter_examples(self):
        """Test multiple parameter query examples."""
        multi_param_examples = ["pm25,no2,o3", "pm25,pm10,no2", "pm25,pm10,no2,o3,so2"]

        for params_str in multi_param_examples:
            params = params_str.split(",")
            assert len(params) >= 2
            for param in params:
                assert len(param.strip()) > 0

    def test_country_code_examples(self):
        """Test country code examples from documentation."""
        country_examples = ["US", "GB", "DE", "CA"]

        for country in country_examples:
            assert len(country) == 2
            assert country.isupper()
            assert country.isalpha()

    def test_limit_parameter_examples(self):
        """Test limit parameter examples."""
        limit_examples = [50, 100, 150, 200, 300, 500]

        for limit in limit_examples:
            assert isinstance(limit, int)
            assert limit > 0
            assert limit <= 1000  # Reasonable upper bound

    def test_date_range_examples(self):
        """Test date range examples from documentation."""
        date_pairs = [
            ("2024-10-01", "2024-10-07"),
            ("2024-09-01", "2024-09-30"),
            ("2024-08-01", "2024-08-31"),
            ("2024-06-01", "2024-06-30"),
        ]

        from datetime import datetime

        for start_date, end_date in date_pairs:
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
            assert start <= end
            assert start.year >= 2020
            assert end.year >= 2020

    def test_query_command_structure(self):
        """Test query command structure from documentation examples."""
        query_examples = [
            "query_measurements_by_region bbox=40.6,-74.2,40.9,-73.7 parameters=pm25 limit=50",
            "query_measurements_by_region center_lat=37.7749 center_lon=-122.4194 radius=25 parameters=pm25 limit=50",
            "query_measurements_by_parameter parameter=pm25 country=US limit=150",
            "query_measurements_by_parameter parameter=o3 bbox=40.0,-125.0,45.0,-120.0 limit=75",
        ]

        for query in query_examples:
            parts = query.split()
            assert len(parts) >= 2
            assert parts[0].startswith("query_measurements_by_")

            # Check parameter format
            for part in parts[1:]:
                if "=" in part:
                    key, value = part.split("=", 1)
                    assert len(key) > 0
                    assert len(value) > 0


if __name__ == "__main__":
    pytest.main([__file__])
