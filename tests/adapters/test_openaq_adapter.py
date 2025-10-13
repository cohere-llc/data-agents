"""
Tests for OpenAQ Air Quality Data Adapter

This module contains comprehensive tests for the OpenAQAdapter class,
including unit tests, integration tests, and example validation.
"""

import os
from unittest.mock import Mock, patch

import pandas as pd
import pytest
from requests.exceptions import HTTPError, RequestException

from data_agents.adapters.openaq_adapter import OpenAQAdapter


class TestOpenAQAdapter:
    """Test cases for OpenAQAdapter core functionality."""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration for testing."""
        return {"api_key": "test_api_key_123", "base_url": "https://api.openaq.org/v3"}

    @pytest.fixture
    def adapter(self, mock_config):
        """Create adapter instance for testing."""
        return OpenAQAdapter(mock_config)

    @pytest.fixture
    def mock_locations_response(self):
        """Mock response for locations API."""
        return {
            "results": [
                {
                    "id": 1001,
                    "name": "Test Location 1",
                    "coordinates": {"latitude": 40.7128, "longitude": -74.0060},
                    "country": {"code": "US", "name": "United States"},
                    "timezone": "America/New_York",
                    "locality": "New York",
                    "sensors": [
                        {"id": 1675, "parameter": {"id": 2, "name": "pm25"}},
                        {"id": 1676, "parameter": {"id": 3, "name": "no2"}},
                    ],
                },
                {
                    "id": 1002,
                    "name": "Test Location 2",
                    "coordinates": {"latitude": 40.7589, "longitude": -73.9851},
                    "country": {"code": "US", "name": "United States"},
                    "timezone": "America/New_York",
                    "locality": "New York",
                    "sensors": [{"id": 1677, "parameter": {"id": 2, "name": "pm25"}}],
                },
            ]
        }

    @pytest.fixture
    def mock_measurements_response(self):
        """Mock response for measurements API."""
        return {
            "results": [
                {
                    "datetime": "2024-10-10T12:00:00Z",
                    "value": 15.2,
                    "parameter": {"id": 2, "name": "pm25", "units": "µg/m³"},
                },
                {
                    "datetime": "2024-10-10T13:00:00Z",
                    "value": 16.8,
                    "parameter": {"id": 2, "name": "pm25", "units": "µg/m³"},
                },
            ]
        }

    @pytest.fixture
    def mock_parameters_response(self):
        """Mock response for parameters API."""
        return {
            "results": [
                {
                    "id": 2,
                    "name": "pm25",
                    "displayName": "PM2.5",
                    "description": "Particulate matter <2.5μm",
                },
                {
                    "id": 3,
                    "name": "no2",
                    "displayName": "NO₂",
                    "description": "Nitrogen dioxide",
                },
                {"id": 4, "name": "o3", "displayName": "O₃", "description": "Ozone"},
            ]
        }

    def test_adapter_initialization(self, mock_config):
        """Test adapter initialization with valid configuration."""
        adapter = OpenAQAdapter(mock_config)
        assert adapter.api_key == "test_api_key_123"
        assert adapter.base_url == "https://api.openaq.org/v3"
        assert adapter.headers["X-API-Key"] == "test_api_key_123"

    def test_adapter_initialization_without_api_key(self):
        """Test adapter initialization without API key."""
        config = {"base_url": "https://api.openaq.org/v3"}

        with patch.dict(os.environ, {}, clear=True):
            adapter = OpenAQAdapter(config)
            assert adapter.api_key is None
            assert "X-API-Key" not in adapter.headers

    def test_adapter_initialization_with_env_var(self):
        """Test adapter initialization with environment variable."""
        config = {"base_url": "https://api.openaq.org/v3"}

        with patch.dict(os.environ, {"OPENAQ_API_KEY": "env_test_key"}):
            adapter = OpenAQAdapter(config)
            assert adapter.api_key == "env_test_key"

    def test_adapter_initialization_defaults(self):
        """Test adapter initialization with defaults."""
        with patch.dict(os.environ, {}, clear=True):
            adapter = OpenAQAdapter({})
            assert adapter.base_url == "https://api.openaq.org/v3"
            assert adapter.api_key is None

    @patch("requests.Session.get")
    def test_discover_method(self, mock_get, adapter, mock_parameters_response):
        """Test the discover method returns correct information."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_parameters_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        discovery = adapter.discover()

        assert "adapter_type" in discovery
        assert discovery["adapter_type"] == "openaq"
        assert "query_methods" in discovery
        assert "capabilities" in discovery
        assert discovery["capabilities"]["geographic_filtering"] == [
            "bounding_box",
            "center_point_radius",
            "coordinates",
        ]

    @patch("requests.Session.get")
    def test_get_available_parameters(
        self, mock_get, adapter, mock_parameters_response
    ):
        """Test getting available parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_parameters_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        params_df = adapter.get_available_parameters()

        assert isinstance(params_df, pd.DataFrame)
        assert len(params_df) == 3
        assert "pm25" in params_df["name"].values
        assert "no2" in params_df["name"].values

    @patch("requests.Session.get")
    def test_find_locations_by_region_bbox(
        self, mock_get, adapter, mock_locations_response
    ):
        """Test finding locations by bounding box."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_locations_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Mock parameters to avoid parameter lookup
        adapter._parameters_cache = [{"id": 2, "name": "pm25"}]

        bbox = [40.6, -74.2, 40.9, -73.7]
        locations = adapter._find_locations_by_region(bbox=bbox, parameters=["pm25"])

        assert isinstance(locations, pd.DataFrame)
        assert len(locations) == 2
        assert "location_id" in locations.columns
        assert "latitude" in locations.columns
        assert "longitude" in locations.columns

    @patch("requests.Session.get")
    def test_find_locations_by_region_center_radius(
        self, mock_get, adapter, mock_locations_response
    ):
        """Test finding locations by center point and radius."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_locations_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        center = {"lat": 40.7128, "lon": -74.0060}
        radius = 5000
        locations = adapter._find_locations_by_region(center=center, radius=radius)

        assert isinstance(locations, pd.DataFrame)
        assert len(locations) == 2

    @patch("requests.Session.get")
    def test_get_sensor_measurements(
        self, mock_get, adapter, mock_measurements_response
    ):
        """Test getting measurements for a specific sensor."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_measurements_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        measurements = adapter._get_sensor_measurements(
            1675, date_from="2024-10-01", date_to="2024-10-10"
        )

        assert isinstance(measurements, pd.DataFrame)
        assert len(measurements) == 2
        assert "sensor_id" in measurements.columns
        assert "value" in measurements.columns
        assert "parameter" in measurements.columns

    @patch("requests.Session.get")
    def test_get_sensor_measurements_network_error(self, mock_get, adapter):
        """Test handling network errors in sensor measurements."""
        mock_get.side_effect = RequestException("Network error")

        with patch("builtins.print") as mock_print:
            measurements = adapter._get_sensor_measurements(1675)

        assert isinstance(measurements, pd.DataFrame)
        assert measurements.empty
        mock_print.assert_called_once()

    def test_extract_sensor_ids(self, adapter):
        """Test extracting sensor IDs from locations DataFrame."""
        locations_data = {
            "location_id": [1001, 1002],
            "sensors": [[{"id": 1675}, {"id": 1676}], [{"id": 1677}]],
        }
        locations_df = pd.DataFrame(locations_data)

        sensor_ids = adapter._extract_sensor_ids(locations_df)

        assert set(sensor_ids) == {1675, 1676, 1677}

    def test_extract_sensor_ids_empty(self, adapter):
        """Test extracting sensor IDs from empty DataFrame."""
        locations_df = pd.DataFrame()
        sensor_ids = adapter._extract_sensor_ids(locations_df)
        assert sensor_ids == []

    def test_get_parameter_id(self, adapter):
        """Test getting parameter ID from name."""
        adapter._parameters_cache = [
            {"id": 2, "name": "pm25"},
            {"id": 3, "name": "no2"},
        ]

        assert adapter._get_parameter_id("pm25") == 2
        assert adapter._get_parameter_id("PM25") == 2  # Case insensitive
        assert adapter._get_parameter_id("nonexistent") is None

    def test_enrich_measurements_with_location_data(self, adapter):
        """Test enriching measurements with location data."""
        measurements_data = {
            "sensor_id": [1675, 1676],
            "value": [15.2, 25.8],
            "parameter": ["pm25", "no2"],
        }
        measurements_df = pd.DataFrame(measurements_data)

        locations_data = {
            "location_id": [1001],
            "location_name": ["Test Location"],
            "latitude": [40.7128],
            "longitude": [-74.0060],
            "country_code": ["US"],
            "country_name": ["United States"],  # Add country_name
            "timezone": ["America/New_York"],  # Add timezone
            "locality": ["New York"],  # Add locality
            "sensors": [[{"id": 1675}, {"id": 1676}]],
        }
        locations_df = pd.DataFrame(locations_data)

        enriched = adapter._enrich_measurements_with_location_data(
            measurements_df, locations_df
        )

        assert "location_name" in enriched.columns
        assert "latitude" in enriched.columns
        assert enriched.loc[0, "location_name"] == "Test Location"

    @patch("requests.Session.get")
    def test_query_measurements_by_parameter(
        self,
        mock_get,
        adapter,
        mock_locations_response,
        mock_measurements_response,
        mock_parameters_response,
    ):
        """Test querying measurements by parameter."""
        # Mock parameter response first, then locations, then measurements for
        # each sensor
        mock_param_response = Mock()
        mock_param_response.status_code = 200
        mock_param_response.json.return_value = mock_parameters_response
        mock_param_response.raise_for_status.return_value = None

        mock_loc_response = Mock()
        mock_loc_response.status_code = 200
        mock_loc_response.json.return_value = mock_locations_response
        mock_loc_response.raise_for_status.return_value = None

        mock_meas_response = Mock()
        mock_meas_response.status_code = 200
        mock_meas_response.json.return_value = mock_measurements_response
        mock_meas_response.raise_for_status.return_value = None

        # Need 4 calls: parameters, locations, measurements for sensor 1675,
        # measurements for sensor 1676, measurements for sensor 1677
        mock_get.side_effect = [
            mock_param_response,  # Parameter lookup
            mock_loc_response,  # Location search
            mock_meas_response,  # Measurements for sensor 1675
            mock_meas_response,  # Measurements for sensor 1676
            mock_meas_response,  # Measurements for sensor 1677
        ]

        result = adapter.query_measurements_by_parameter("pm25", limit=10)

        assert isinstance(result, pd.DataFrame)

    @patch("requests.Session.get")
    def test_query_measurements_by_region_error_handling(self, mock_get, adapter):
        """Test error handling in region query."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = HTTPError("401 Unauthorized")
        mock_get.return_value = mock_response

        with pytest.raises(HTTPError):
            adapter.query_measurements_by_region(bbox=[40.6, -74.2, 40.9, -73.7])

    def test_to_dict(self, adapter):
        """Test converting adapter to dictionary."""
        result = adapter.to_dict()

        assert result["adapter_type"] == "openaq"
        assert result["base_url"] == "https://api.openaq.org/v3"
        assert result["has_api_key"] is True
        assert "capabilities" in result

    @patch("requests.Session.get")
    def test_query_general_interface(self, mock_get, adapter, mock_locations_response):
        """Test general query interface."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_locations_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Test measurements query format
        result = adapter.query("measurements?bbox=40.6,-74.2,40.9,-73.7&parameter=pm25")
        assert isinstance(result, pd.DataFrame)

        # For parameter query, we need to mock the parameter cache first
        adapter._parameters_cache = [{"id": 2, "name": "pm25"}]

        # Test parameter query format
        result = adapter.query("parameter:pm25&country=US")
        assert isinstance(result, pd.DataFrame)

    def test_handle_measurements_query_parsing(self, adapter):
        """Test parsing of measurements query strings."""
        # Mock the actual query method to avoid network calls
        with patch.object(
            adapter, "query_measurements_by_region", return_value=pd.DataFrame()
        ) as mock_query:
            adapter._handle_measurements_query(
                "measurements?bbox=40.6,-74.2,40.9,-73.7&parameter=pm25"
            )

            mock_query.assert_called_once()
            args, kwargs = mock_query.call_args
            assert "bbox" in kwargs
            assert kwargs["bbox"] == [40.6, -74.2, 40.9, -73.7]
            assert kwargs["parameters"] == ["pm25"]

    def test_handle_parameter_query_parsing(self, adapter):
        """Test parsing of parameter query strings."""
        with patch.object(
            adapter, "query_measurements_by_parameter", return_value=pd.DataFrame()
        ) as mock_query:
            adapter._handle_parameter_query("parameter:pm25&country=US")

            mock_query.assert_called_once()
            args, kwargs = mock_query.call_args
            assert args[0] == "pm25"

    # Additional tests for coverage improvements

    def test_empty_measurements_list_returns_empty_dataframe(self, adapter):
        """Test line 120: empty measurements list returns empty DataFrame."""
        empty_df = pd.DataFrame()
        result = adapter._extract_sensor_ids(empty_df)
        assert result == []

    def test_parameter_not_found_raises_error(self, adapter):
        """Test line 164: parameter not found raises ValueError."""
        with patch.object(adapter, "_get_parameter_id", return_value=None):
            with pytest.raises(ValueError, match="Parameter.*not found"):
                adapter.query_measurements_by_parameter("nonexistent_param")

    @patch("requests.Session.get")
    def test_invalid_radius_raises_error(self, mock_get, adapter):
        """Test line 195: raise error for invalid radius."""
        # Mock successful response for cases where API might be reached
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"results": []}
        mock_get.return_value = mock_response

        # Test radius validation for values > 25000 (this works correctly)
        with pytest.raises(
            ValueError, match="Invalid radius.*Must be between 1 and 25000"
        ):
            adapter._find_locations_by_region(
                center={"lat": 40.7, "lon": -74.0},
                radius=30000,  # > 25000 limit
            )

        # Test radius validation for negative values (this works correctly)
        with pytest.raises(
            ValueError, match="Invalid radius.*Must be between 1 and 25000"
        ):
            adapter._find_locations_by_region(
                center={"lat": 40.7, "lon": -74.0},
                radius=-1,  # < 0
            )

        # Test radius validation for zero values (now fixed)
        with pytest.raises(
            ValueError, match="Invalid radius.*Must be between 1 and 25000"
        ):
            adapter._find_locations_by_region(
                center={"lat": 40.7, "lon": -74.0},
                radius=0,  # <= 0
            )

    @patch("requests.Session.get")
    def test_kwargs_filtering_in_params(self, mock_get, adapter):
        """Test line 219: kwargs filtering in _find_locations_by_region."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Test that other kwargs are included
        adapter._find_locations_by_region(
            bbox=[40.6, -74.2, 40.9, -73.7],
            country="US",  # Should be included
            sort="desc",  # Should be included
        )

        # Verify the request was made with filtered params
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        params = call_args[1]["params"]
        assert "country" in params
        assert "sort" in params

    def test_sensor_measurements_with_invalid_limit(self, adapter):
        """Test lines 282-284: exception handling for invalid limit."""
        # Test invalid string limit
        with pytest.raises(
            ValueError, match="Limit must be an integer between 1 and 10000"
        ):
            adapter._get_sensor_measurements(1675, limit="invalid")

        # Test out of range limit
        with pytest.raises(
            ValueError, match="Limit must be an integer between 1 and 10000"
        ):
            adapter._get_sensor_measurements(1675, limit=15000)

    @patch("requests.Session.get")
    def test_sensor_measurements_request_exception(self, mock_get, adapter):
        """Test line 296: request exception handling in _get_sensor_measurements."""
        mock_get.side_effect = RequestException("Network error")

        result = adapter._get_sensor_measurements(1675)

        # Should return empty DataFrame on exception
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_enrich_measurements_empty_inputs(self, adapter):
        """Test lines 322, 360: empty inputs handling in "
        "_enrich_measurements_with_location_data."""
        empty_df = pd.DataFrame()
        empty_locations_df = pd.DataFrame()
        non_empty_measurements = pd.DataFrame({"value": [1, 2, 3]})

        # Test with empty measurements
        result = adapter._enrich_measurements_with_location_data(
            empty_df, pd.DataFrame({"name": ["Test"]})
        )
        assert result.equals(empty_df)

        # Test with empty locations
        result = adapter._enrich_measurements_with_location_data(
            non_empty_measurements, empty_locations_df
        )
        assert result.equals(non_empty_measurements)

    @patch("requests.Session.get")
    def test_load_parameters_with_exception(self, mock_get, adapter):
        """Test lines 383-385: exception handling in _load_parameters."""
        mock_get.side_effect = RequestException("API error")

        with patch.object(adapter, "_parameters_cache", None):
            adapter._load_parameters()
            assert adapter._parameters_cache == []

    def test_get_available_parameters_with_none_cache(self, adapter):
        """Test line 393: get_available_parameters when cache is None."""
        with patch.object(adapter, "_parameters_cache", None):
            with patch.object(adapter, "_load_parameters") as mock_load:
                adapter.get_available_parameters()
                mock_load.assert_called_once()

    def test_get_available_parameters_empty_cache(self, adapter):
        """Test line 393: get_available_parameters when cache is empty list."""
        adapter._parameters_cache = []
        result = adapter.get_available_parameters()
        assert result.empty

    def test_query_unsupported_format(self, adapter):
        """Test line 423: unsupported query format."""
        # This should raise ValueError when parameter is not found
        with pytest.raises(ValueError, match="Parameter.*not found"):
            adapter.query("unsupported:format")

    @patch("requests.Session.get")
    def test_handle_measurements_query_malformed(self, mock_get, adapter):
        """Test line 432: malformed measurements query."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = adapter._handle_measurements_query("malformed query")

        # Should return empty DataFrame since query can't be parsed properly
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_handle_parameter_query_parsing_error(self, adapter):
        """Test lines 471, 475: parsing errors in parameter query."""
        result = adapter._handle_parameter_query("malformed")

        # Should return empty DataFrame for unparseable query
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_handle_parameter_query_missing_parameter(self, adapter):
        """Test line 475: missing parameter in query."""
        result = adapter._handle_parameter_query("country=US")

        # Should return empty DataFrame when no parameter specified
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_parameter_cache_none_in_get_parameter_id(self, adapter):
        """Test that _get_parameter_id loads parameters when cache is None."""
        # Set cache to None initially
        adapter._parameters_cache = None

        with patch.object(adapter, "_load_parameters") as mock_load:
            # Mock _load_parameters to set cache after being called
            def mock_load_side_effect():
                adapter._parameters_cache = [{"id": 1, "name": "pm25"}]

            mock_load.side_effect = mock_load_side_effect

            result = adapter._get_parameter_id("pm25")

            # Verify _load_parameters was called and result is correct
            mock_load.assert_called_once()
            assert result == 1

    @patch("requests.Session.get")
    def test_find_locations_no_results(self, mock_get, adapter):
        """Test _find_locations_by_region with no results."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = adapter._find_locations_by_region(bbox=[40.6, -74.2, 40.9, -73.7])
        assert result.empty

    @patch("requests.Session.get")
    def test_get_sensor_measurements_no_results(self, mock_get, adapter):
        """Test _get_sensor_measurements with no results."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = adapter._get_sensor_measurements(1675)
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_extract_sensor_ids_with_invalid_sensors(self, adapter):
        """Test _extract_sensor_ids with sensors missing required fields."""
        # Create a DataFrame with sensors that have missing fields
        locations_df = pd.DataFrame(
            [
                {
                    "sensors": [
                        {"parameter": {"id": 2, "name": "pm25"}},  # Missing 'id'
                        {"id": 1676},  # Missing 'parameter'
                        {
                            "id": 1677,
                            "parameter": {"name": "no2"},
                        },  # Missing parameter id
                    ]
                }
            ]
        )

        result = adapter._extract_sensor_ids(locations_df)
        # Should only extract sensor IDs that have the 'id' field
        # The method only requires 'id' field, not parameter validation
        assert sorted(result) == [1676, 1677]


class TestOpenAQAdapterIntegration:
    """Integration tests for OpenAQAdapter with mocked API responses."""

    @pytest.fixture
    def full_adapter_config(self):
        """Configuration for integration testing."""
        return {
            "api_key": "test_integration_key",
            "base_url": "https://api.openaq.org/v3",
        }

    @patch("requests.Session.get")
    def test_full_query_workflow_bbox(self, mock_get, full_adapter_config):
        """Test complete query workflow with bounding box."""
        adapter = OpenAQAdapter(full_adapter_config)

        # Mock parameters response
        parameters_response = {
            "results": [{"id": 2, "name": "pm25", "displayName": "PM2.5"}]
        }

        # Mock locations response
        locations_response = {
            "results": [
                {
                    "id": 1001,
                    "name": "Integration Test Location",
                    "coordinates": {"latitude": 40.7128, "longitude": -74.0060},
                    "country": {"code": "US", "name": "United States"},
                    "timezone": "America/New_York",
                    "locality": "New York",
                    "sensors": [
                        {"id": 1675, "parameter": {"id": 2, "name": "pm25"}},
                    ],
                }
            ]
        }

        # Mock measurements response
        measurements_response = {
            "results": [
                {
                    "datetime": "2024-10-10T12:00:00Z",
                    "value": 15.2,
                    "parameter": {"id": 2, "name": "pm25", "units": "µg/m³"},
                }
            ]
        }

        # Setup mock responses in order: parameters, locations, measurements
        mock_param_response = Mock()
        mock_param_response.status_code = 200
        mock_param_response.json.return_value = parameters_response
        mock_param_response.raise_for_status.return_value = None

        mock_location_response = Mock()
        mock_location_response.status_code = 200
        mock_location_response.json.return_value = locations_response
        mock_location_response.raise_for_status.return_value = None

        mock_measurement_response = Mock()
        mock_measurement_response.status_code = 200
        mock_measurement_response.json.return_value = measurements_response
        mock_measurement_response.raise_for_status.return_value = None

        mock_get.side_effect = [
            mock_param_response,  # Parameter lookup
            mock_location_response,  # Location search
            mock_measurement_response,  # Measurements
        ]

        # Execute query
        result = adapter.query_measurements_by_region(
            bbox=[40.6, -74.2, 40.9, -73.7],
            parameters="pm25",
            date_from="2024-10-01",
            date_to="2024-10-10",
            limit=100,
        )

        # Verify results
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert "location_name" in result.columns
        assert "value" in result.columns
        assert result.iloc[0]["value"] == 15.2

    @patch("requests.Session.get")
    def test_workflow_with_empty_locations(self, mock_get, full_adapter_config):
        """Test workflow when no locations are found."""
        adapter = OpenAQAdapter(full_adapter_config)

        # Mock empty locations response
        empty_response = {"results": []}

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = empty_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = adapter.query_measurements_by_region(
            bbox=[40.6, -74.2, 40.9, -73.7], parameters="pm25"
        )

        assert isinstance(result, pd.DataFrame)
        assert result.empty

    @patch("requests.Session.get")
    def test_workflow_with_no_sensors(self, mock_get, full_adapter_config):
        """Test workflow when locations have no sensors."""
        adapter = OpenAQAdapter(full_adapter_config)

        # Mock locations without sensors
        locations_response = {
            "results": [
                {
                    "id": 1001,
                    "name": "No Sensors Location",
                    "coordinates": {"latitude": 40.7128, "longitude": -74.0060},
                    "country": {"code": "US", "name": "United States"},
                    "sensors": [],  # No sensors
                }
            ]
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = locations_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = adapter.query_measurements_by_region(bbox=[40.6, -74.2, 40.9, -73.7])

        assert isinstance(result, pd.DataFrame)
        assert result.empty
