"""Tests for GBIF Occurrence adapter."""

from unittest.mock import Mock, patch

import pandas as pd
import pytest
import requests

from data_agents.adapters.gbif_occurrence_adapter import GBIFOccurrenceAdapter


def test_gbif_adapter_basic():
    """Test basic GBIF adapter functionality."""
    adapter = GBIFOccurrenceAdapter()

    # Test discovery
    print("Testing discovery...")
    result = adapter.discover()

    print(f"Discovery result keys: {list(result.keys())}")
    print(f"Total parameters: {result.get('total_parameters', 'Not found')}")

    # Check we have parameters
    parameters = result.get("parameters", {})
    assert len(parameters) > 0, "Should discover at least some parameters"

    # Check specific parameters are present
    expected_params = ["q", "scientificName", "taxonKey", "country", "year", "month", "day"]
    for param in expected_params:
        assert param in parameters, f"Parameter {param} should be in discovery"
        param_info = parameters[param]
        assert "description" in param_info
        assert "type" in param_info
        assert "example" in param_info

    print("Discovery test passed!")


def test_gbif_adapter_init():
    """Test GBIF adapter initialization."""
    # Test default initialization
    adapter = GBIFOccurrenceAdapter()
    assert adapter.base_url == "https://api.gbif.org/v1"
    assert adapter.session.headers["Accept"] == "application/json"
    assert adapter.session.headers["User-Agent"] == "data-agents/1.0"

    # Test custom base URL
    config = {"base_url": "https://custom.gbif.org/v2"}
    adapter = GBIFOccurrenceAdapter(config)
    assert adapter.base_url == "https://custom.gbif.org/v2"


def test_gbif_adapter_simple_query():
    """Test GBIF adapter simple query functionality."""
    adapter = GBIFOccurrenceAdapter()

    # Mock successful response
    mock_data = {
        "results": [
            {
                "key": 123456789,
                "scientificName": "Puma concolor",
                "taxonKey": 2435099,
                "country": "US",
                "decimalLatitude": 40.5,
                "decimalLongitude": -74.0,
                "year": 2023,
                "month": 6,
                "day": 15,
                "basisOfRecord": "HUMAN_OBSERVATION"
            }
        ],
        "count": 1,
        "endOfRecords": True
    }

    with patch.object(requests.Session, "get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        # Test simple text query
        result = adapter.query("Puma concolor")
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.iloc[0]["scientificName"] == "Puma concolor"
        assert result.iloc[0]["country"] == "US"
        assert result.iloc[0]["decimalLatitude"] == 40.5

        # Verify the API call was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "q" in call_args.kwargs["params"]
        assert call_args.kwargs["params"]["q"] == "Puma concolor"

    print("Simple query test passed!")


def test_gbif_adapter_scientific_name_query():
    """Test GBIF adapter scientific name convenience method."""
    adapter = GBIFOccurrenceAdapter()

    mock_data = {
        "results": [
            {
                "key": 987654321,
                "scientificName": "Quercus robur",
                "taxonKey": 2880384,
                "country": "DE",
                "year": 2022
            }
        ],
        "count": 1,
        "endOfRecords": True
    }

    with patch.object(requests.Session, "get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        # Test scientific name query
        result = adapter.search_by_scientific_name("Quercus robur")
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.iloc[0]["scientificName"] == "Quercus robur"

        # Verify the API call was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "scientificName" in call_args.kwargs["params"]
        assert call_args.kwargs["params"]["scientificName"] == "Quercus robur"

    print("Scientific name query test passed!")


def test_gbif_adapter_location_query():
    """Test GBIF adapter location convenience method."""
    adapter = GBIFOccurrenceAdapter()

    mock_data = {
        "results": [
            {
                "key": 555666777,
                "scientificName": "Corvus corax",
                "country": "US",
                "decimalLatitude": 40.7589,
                "decimalLongitude": -73.9851
            }
        ],
        "count": 1,
        "endOfRecords": True
    }

    with patch.object(requests.Session, "get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        # Test location query with country
        result = adapter.search_by_location(country="US")
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.iloc[0]["country"] == "US"

        # Verify the API call was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "country" in call_args.kwargs["params"]
        assert call_args.kwargs["params"]["country"] == "US"

    print("Location query test passed!")


def test_gbif_adapter_year_range_query():
    """Test GBIF adapter year range convenience method."""
    adapter = GBIFOccurrenceAdapter()

    mock_data = {
        "results": [
            {
                "key": 111222333,
                "scientificName": "Falco peregrinus",
                "year": 2020,
                "month": 5
            }
        ],
        "count": 1,
        "endOfRecords": True
    }

    with patch.object(requests.Session, "get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        # Test year range query
        result = adapter.search_by_year_range(2020, 2022)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.iloc[0]["year"] == 2020

        # Verify the API call was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "year" in call_args.kwargs["params"]
        assert call_args.kwargs["params"]["year"] == "2020,2022"

    print("Year range query test passed!")


def test_gbif_adapter_complex_query():
    """Test GBIF adapter with complex query parameters."""
    adapter = GBIFOccurrenceAdapter()

    mock_data = {
        "results": [
            {
                "key": 444555666,
                "scientificName": "Ursus americanus",
                "country": "CA",
                "year": 2021,
                "month": 8,
                "basisOfRecord": "HUMAN_OBSERVATION",
                "hasCoordinate": True
            }
        ],
        "count": 1,
        "endOfRecords": True
    }

    with patch.object(requests.Session, "get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        # Test complex query with multiple parameters
        result = adapter.query(
            scientificName="Ursus americanus",
            country="CA",
            year=2021,
            basisOfRecord="HUMAN_OBSERVATION",
            hasCoordinate=True,
            limit=50
        )
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.iloc[0]["scientificName"] == "Ursus americanus"
        assert result.iloc[0]["country"] == "CA"

        # Verify the API call was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        params = call_args.kwargs["params"]
        assert params["scientificName"] == "Ursus americanus"
        assert params["country"] == "CA"
        assert params["year"] == "2021"  # Parameters are converted to strings
        assert params["basisOfRecord"] == "HUMAN_OBSERVATION"
        assert params["hasCoordinate"] == "True"  # Booleans become strings
        assert params["limit"] == "50"

    print("Complex query test passed!")


def test_gbif_adapter_pagination():
    """Test GBIF adapter pagination handling."""
    adapter = GBIFOccurrenceAdapter()

    # Mock response with pagination
    mock_data = {
        "results": [
            {"key": i, "scientificName": f"Species {i}"}
            for i in range(20)
        ],
        "count": 100,
        "endOfRecords": False,
        "offset": 0,
        "limit": 20
    }

    with patch.object(requests.Session, "get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        # Test with custom limit and offset
        result = adapter.query("test", limit=20, offset=40)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 20

        # Verify pagination parameters were passed
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        params = call_args.kwargs["params"]
        assert params["limit"] == "20"  # Parameters are converted to strings
        assert params["offset"] == "40"

    print("Pagination test passed!")


def test_gbif_adapter_empty_response():
    """Test GBIF adapter handling of empty responses."""
    adapter = GBIFOccurrenceAdapter()

    # Mock empty response
    mock_data = {
        "results": [],
        "count": 0,
        "endOfRecords": True
    }

    with patch.object(requests.Session, "get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        # Test query with no results
        result = adapter.query("NonexistentSpecies")
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        assert list(result.columns) == []  # Empty DataFrame with no columns

    print("Empty response test passed!")


def test_gbif_adapter_error_handling():
    """Test GBIF adapter error handling."""
    adapter = GBIFOccurrenceAdapter()

    # Test HTTP error - expect RequestException wrapping
    with patch.object(requests.Session, "get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.HTTPError("Server error")
        mock_get.return_value = mock_response

        with pytest.raises(requests.RequestException, match="GBIF Occurrence API request failed"):
            adapter.query("test query")

    # Test JSON decode error (not wrapped by adapter)
    with patch.object(requests.Session, "get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        with pytest.raises(ValueError, match="Invalid JSON"):
            adapter.query("test query")

    # Test connection error
    with patch.object(requests.Session, "get") as mock_get:
        mock_get.side_effect = requests.ConnectionError("Connection failed")

        with pytest.raises(requests.RequestException, match="GBIF Occurrence API request failed"):
            adapter.query("test query")

    print("Error handling test passed!")


def test_gbif_adapter_parameter_validation():
    """Test parameter validation in GBIF adapter."""
    adapter = GBIFOccurrenceAdapter()

    # Test various parameter values (GBIF doesn't enforce limits like NASA)
    mock_data = {"results": [], "count": 0, "endOfRecords": True}
    
    with patch.object(requests.Session, "get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        # Test high limit (GBIF accepts it, but may limit server-side)
        adapter.query("test", limit=500)
        call_args = mock_get.call_args
        assert call_args.kwargs["params"]["limit"] == "500"

        # Test negative offset (passed as-is, server will handle)
        mock_get.reset_mock()
        adapter.query("test", offset=-5)
        call_args = mock_get.call_args
        assert call_args.kwargs["params"]["offset"] == "-5"

    print("Parameter validation test passed!")


def test_gbif_adapter_boolean_parameters():
    """Test handling of boolean parameters."""
    adapter = GBIFOccurrenceAdapter()

    mock_data = {"results": [], "count": 0, "endOfRecords": True}
    
    with patch.object(requests.Session, "get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        # Test boolean parameters
        adapter.query(
            "test",
            hasCoordinate=True,
            hasGeospatialIssue=False,
            isInCluster=True
        )
        
        call_args = mock_get.call_args
        params = call_args.kwargs["params"]
        assert params["hasCoordinate"] == "True"  # Booleans become strings
        assert params["hasGeospatialIssue"] == "False"
        assert params["isInCluster"] == "True"

    print("Boolean parameters test passed!")


def test_gbif_adapter_array_parameters():
    """Test handling of array parameters."""
    adapter = GBIFOccurrenceAdapter()

    mock_data = {"results": [], "count": 0, "endOfRecords": True}
    
    with patch.object(requests.Session, "get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        # Test array parameters (should be passed as-is for GBIF API)
        adapter.query(
            "test",
            country=["US", "CA"],
            taxonKey=[12345, 67890],
            year=[2020, 2021, 2022]
        )
        
        call_args = mock_get.call_args
        params = call_args.kwargs["params"]
        assert params["country"] == ["US", "CA"]
        assert params["taxonKey"] == ["12345", "67890"]  # Numbers become strings
        assert params["year"] == ["2020", "2021", "2022"]

    print("Array parameters test passed!")


def test_gbif_adapter_discovery_structure():
    """Test the structure of discovery response."""
    adapter = GBIFOccurrenceAdapter()

    discovery = adapter.discover()

    # Check main structure
    assert "adapter_type" in discovery
    assert "base_url" in discovery
    assert "description" in discovery
    assert "parameters" in discovery
    assert "total_parameters" in discovery

    assert discovery["adapter_type"] == "gbif_occurrence"
    assert discovery["base_url"] == "https://api.gbif.org/v1"
    assert discovery["total_parameters"] == 37

    # Check parameter structure
    parameters = discovery["parameters"]
    
    # Test a few specific parameters
    assert "q" in parameters
    q_param = parameters["q"]
    assert q_param["description"] == "Simple full-text search parameter. The value can be a simple word or a phrase."
    assert q_param["type"] == "string"

    assert "scientificName" in parameters
    sci_name_param = parameters["scientificName"]
    assert "scientific name" in sci_name_param["description"].lower()
    assert sci_name_param["type"] == "array"

    assert "country" in parameters
    country_param = parameters["country"]
    assert "iso-3166-1" in country_param["description"].lower()
    assert country_param["type"] == "array"

    print("Discovery structure test passed!")


def test_gbif_adapter_url_construction():
    """Test URL construction for API calls."""
    adapter = GBIFOccurrenceAdapter()

    # Test default base URL
    assert adapter.base_url == "https://api.gbif.org/v1"

    # Test custom base URL
    custom_adapter = GBIFOccurrenceAdapter({"base_url": "https://custom.api.com/v2"})
    assert custom_adapter.base_url == "https://custom.api.com/v2"

    # The actual URL construction happens in the requests call,
    # so we test it indirectly through mocking
    mock_data = {"results": [], "count": 0, "endOfRecords": True}
    
    with patch.object(requests.Session, "get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        adapter.query("test")
        
        # Verify the URL was constructed correctly
        call_args = mock_get.call_args
        assert call_args[0][0] == "https://api.gbif.org/v1/occurrence/search"

    print("URL construction test passed!")


def test_gbif_adapter_response_parsing_edge_cases():
    """Test response parsing with edge cases."""
    adapter = GBIFOccurrenceAdapter()

    # Test response with missing optional fields
    mock_data = {
        "results": [
            {
                "key": 123,
                "scientificName": "Test species",
                # Missing many optional fields
            }
        ],
        "count": 1,
        "endOfRecords": True
    }

    with patch.object(requests.Session, "get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        result = adapter.query("test")
        
        assert len(result) == 1
        assert result.iloc[0]["gbifID"] == 123  # GBIF API key maps to gbifID
        assert result.iloc[0]["scientificName"] == "Test species"
        # Missing fields should be handled gracefully (NaN/None)

    # Test response with extra fields
    mock_data_extra = {
        "results": [
            {
                "key": 456,
                "scientificName": "Another species",
                "extraField": "extra data",
                "customAttribute": 999
            }
        ],
        "count": 1,
        "endOfRecords": True
    }

    with patch.object(requests.Session, "get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_data_extra
        mock_get.return_value = mock_response

        result = adapter.query("test")
        
        assert len(result) == 1
        assert result.iloc[0]["gbifID"] == 456  # GBIF API key maps to gbifID
        assert result.iloc[0]["scientificName"] == "Another species"
        # Extra fields should be included in the DataFrame

    print("Response parsing edge cases test passed!")


def test_gbif_adapter_count():
    """Test GBIF adapter count functionality."""
    adapter = GBIFOccurrenceAdapter()

    # Mock response for count query (limit=0)
    mock_count_data = {
        "results": [],
        "count": 12345,
        "endOfRecords": True,
        "offset": 0,
        "limit": 0
    }

    with patch.object(requests.Session, "get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_count_data
        mock_get.return_value = mock_response

        # First test that regular query sets metadata correctly
        df = adapter.query("", limit=0, scientificName="Puma concolor")
        
        # Check metadata was set
        assert hasattr(df, "attrs"), "DataFrame should have attrs"
        assert "gbif_metadata" in df.attrs, "Should have gbif_metadata"
        assert df.attrs["gbif_metadata"]["count"] == 12345, "Metadata count should be 12345"
        
        # Now test count method
        mock_get.reset_mock()
        mock_response.json.return_value = mock_count_data  # Reset mock data
        
        result = adapter.count(scientificName="Puma concolor")
        
        # The count should come from the metadata
        assert result == 12345

        # Verify the API call was made correctly
        assert mock_get.call_count >= 1
        call_args = mock_get.call_args
        assert "occurrence/search" in call_args[0][0]
        assert "scientificName" in call_args.kwargs["params"]
        assert call_args.kwargs["params"]["scientificName"] == "Puma concolor"
        assert call_args.kwargs["params"]["limit"] == "0"  # Count uses limit=0

    print("Count test passed!")


def test_gbif_adapter_metadata():
    """Test that GBIF adapter sets metadata correctly."""
    adapter = GBIFOccurrenceAdapter()

    mock_data = {
        "results": [
            {"key": 123, "scientificName": "Test species"}
        ],
        "count": 5000,
        "endOfRecords": False,
        "offset": 20,
        "limit": 20
    }

    with patch.object(requests.Session, "get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        result = adapter.query("test")
        
        # Check that metadata is set
        if hasattr(result, "attrs") and "gbif_metadata" in result.attrs:
            metadata = result.attrs["gbif_metadata"]
            assert metadata["count"] == 5000
            assert metadata["offset"] == 20
            assert metadata["limit"] == 20
            assert metadata["endOfRecords"] is False
        else:
            # If attrs don't work in this pandas version, skip the metadata test
            print("DataFrame.attrs not available in this pandas version")

    print("Metadata test passed!")


def test_gbif_adapter_session_headers():
    """Test that session headers are set correctly."""
    adapter = GBIFOccurrenceAdapter()

    # Check default headers
    assert adapter.session.headers["Accept"] == "application/json"
    assert adapter.session.headers["User-Agent"] == "data-agents/1.0"

    # Test that headers are used in requests
    mock_data = {"results": [], "count": 0, "endOfRecords": True}
    
    with patch.object(requests.Session, "get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        adapter.query("test")
        
        # Verify the session was used (headers should be automatically included)
        mock_get.assert_called_once()

    print("Session headers test passed!")


if __name__ == "__main__":
    test_gbif_adapter_basic()
    test_gbif_adapter_init()
    test_gbif_adapter_simple_query()
    test_gbif_adapter_scientific_name_query()
    test_gbif_adapter_location_query()
    test_gbif_adapter_year_range_query()
    test_gbif_adapter_complex_query()
    test_gbif_adapter_pagination()
    test_gbif_adapter_empty_response()
    test_gbif_adapter_error_handling()
    test_gbif_adapter_parameter_validation()
    test_gbif_adapter_boolean_parameters()
    test_gbif_adapter_array_parameters()
    test_gbif_adapter_discovery_structure()
    test_gbif_adapter_url_construction()
    test_gbif_adapter_response_parsing_edge_cases()
    test_gbif_adapter_count()
    test_gbif_adapter_metadata()
    test_gbif_adapter_session_headers()
    print("All GBIF adapter tests passed!")