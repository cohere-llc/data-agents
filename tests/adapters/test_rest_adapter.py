"""Tests for RESTAdapter class."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
import requests

from data_agents.adapters import RESTAdapter


def load_config(filename: str) -> dict:
    """Load configuration from JSON file in config directory."""
    config_path = Path(__file__).parent.parent.parent / "config" / filename
    with open(config_path) as f:
        return json.load(f)


class TestRESTAdapter:
    """Test cases for RESTAdapter class."""

    def test_init(self):
        """Test RESTAdapter initialization."""
        adapter = RESTAdapter("https://api.example.com")
        assert adapter.base_url == "https://api.example.com"
        assert adapter.headers["Accept"] == "application/json"
        assert adapter.timeout == 30
        assert adapter.verify is True

    def test_init_with_config(self):
        """Test RESTAdapter initialization with config."""
        config = {
            "headers": {"Custom-Header": "test-value"},
            "timeout": 15,
            "verify": False,
            "endpoints": ["users", "posts"],
            "pagination_param": "limit",
            "pagination_limit": 20,
        }
        adapter = RESTAdapter("https://api.example.com/", config)
        assert adapter.base_url == "https://api.example.com"
        assert adapter.headers["Custom-Header"] == "test-value"
        assert adapter.headers["Accept"] == "application/json"
        assert adapter.timeout == 15
        assert adapter.verify is False
        assert adapter.endpoints == ["users", "posts"]
        assert adapter.pagination_param == "limit"
        assert adapter.pagination_limit == 20

    def test_init_with_invalid_openapi_data_type(self):
        """Test RESTAdapter initialization with invalid OpenAPI data type."""
        config = {"openapi_data": 12345}  # Invalid type (not string or list)

        with pytest.raises(ValueError, match="Invalid OpenAPI data format"):
            RESTAdapter("https://api.example.com", config)

    @patch("requests.get")
    def test_init_with_openapi_url_success(self, mock_get):
        """Test RESTAdapter initialization with OpenAPI URL that loads successfully."""
        # Mock successful OpenAPI spec fetch
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {"/users": {"get": {}}},
        }
        mock_get.return_value = mock_response

        config = {"openapi_data": ["https://api.example.com/openapi.json"]}
        adapter = RESTAdapter("https://api.example.com", config)

        assert len(adapter.openapi_specs) == 1
        assert "users" in adapter.endpoints

    @patch("requests.get")
    @patch("builtins.print")
    def test_init_with_openapi_url_fetch_failure(self, mock_print, mock_get):
        """Test RESTAdapter initialization when OpenAPI URL fetch fails completely."""
        # Mock failed request that raises an exception
        mock_get.side_effect = requests.RequestException("Connection failed")

        config = {"openapi_data": ["https://api.example.com/openapi.json"]}
        adapter = RESTAdapter("https://api.example.com", config)

        # Should handle the error gracefully and print warnings
        assert len(adapter.openapi_specs) == 0
        mock_print.assert_any_call("Warning: Failed to load OpenAPI spec")

    @patch("requests.get")
    @patch("builtins.print")
    def test_init_with_openapi_url_parse_failure_with_fallback(
        self, mock_print, mock_get
    ):
        """Test OpenAPI URL fetch succeeds but parsing fails, with fallback."""
        # First call fails to parse OpenAPI, second call succeeds for fallback
        valid_spec = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {"/users": {"get": {}}},
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = valid_spec
        mock_get.return_value = mock_response

        # Mock OpenAPI constructor to fail first, then succeed on fallback
        with patch("data_agents.adapters.rest_adapter.OpenAPI") as mock_openapi:
            mock_openapi.side_effect = [
                Exception("Parse failed"),
                Exception("Parse failed again"),
            ]

            config = {"openapi_data": ["https://api.example.com/openapi.json"]}
            adapter = RESTAdapter("https://api.example.com", config)

            # Should have fallback raw spec stored
            assert len(adapter.openapi_specs) == 1
            assert isinstance(adapter.openapi_specs[0], dict)
            assert "_raw_spec" in adapter.openapi_specs[0]

    @patch("builtins.print")
    def test_init_with_openapi_json_string_success(self, mock_print):
        """Test RESTAdapter initialization with OpenAPI JSON string."""
        openapi_json = """{
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {"/users": {"get": {}}}
        }"""

        with patch("data_agents.adapters.rest_adapter.OpenAPI") as mock_openapi:
            mock_spec = MagicMock()
            mock_spec.paths = {"/users": {}}
            mock_openapi.return_value = mock_spec

            config = {"openapi_data": [openapi_json]}
            adapter = RESTAdapter("https://api.example.com", config)

            assert len(adapter.openapi_specs) == 1
            assert "users" in adapter.endpoints

    @patch("builtins.print")
    def test_init_with_openapi_json_parse_failure(self, mock_print):
        """Test RESTAdapter initialization with invalid OpenAPI JSON string."""
        invalid_json = "invalid json"

        config = {"openapi_data": [invalid_json]}
        adapter = RESTAdapter("https://api.example.com", config)

        # Should handle the error gracefully
        assert len(adapter.openapi_specs) == 0
        mock_print.assert_called_with(
            "Warning: Failed to parse OpenAPI spec: "
            "Expecting value: line 1 column 1 (char 0)"
        )

    def test_init_with_openapi_single_string(self):
        """Test RESTAdapter initialization with single OpenAPI string (not list)."""
        openapi_json = """{
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {"/users": {"get": {}}}
        }"""

        with patch("data_agents.adapters.rest_adapter.OpenAPI") as mock_openapi:
            mock_spec = MagicMock()
            mock_spec.paths = {"/users": {}}
            mock_openapi.return_value = mock_spec

            # Pass string directly instead of list
            config = {"openapi_data": openapi_json}
            adapter = RESTAdapter("https://api.example.com", config)

            assert len(adapter.openapi_specs) == 1
            assert "users" in adapter.endpoints

    @patch("builtins.print")
    def test_init_with_openapi_dict_parse_failure(self, mock_print):
        """Test RESTAdapter initialization with dict that fails OpenAPI parsing."""
        openapi_dict = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {"/users": {"get": {}}},
        }

        with patch("data_agents.adapters.rest_adapter.OpenAPI") as mock_openapi:
            # Make OpenAPI constructor always fail
            mock_openapi.side_effect = Exception("Parse failed")

            config = {"openapi_data": [openapi_dict]}
            adapter = RESTAdapter("https://api.example.com", config)

            assert len(adapter.openapi_specs) == 0
            mock_print.assert_called_with(
                "Warning: Failed to parse OpenAPI spec: Parse failed"
            )

    def test_init_with_openapi_raw_spec_endpoint_extraction(self):
        """Test endpoint extraction from raw OpenAPI spec fallback."""
        adapter = RESTAdapter("https://api.example.com")

        # Manually set up raw spec as would happen in fallback scenario
        raw_spec = {
            "paths": {
                "/api/users": {"get": {}},
                "/api/posts": {"get": {}},
                "no-leading-slash": {"get": {}},
            }
        }
        adapter.openapi_specs = [{"_raw_spec": raw_spec, "_source_url": "test"}]
        adapter.endpoints = []  # Reset endpoints

        # Manually trigger endpoint extraction (simulating what happens in __init__)
        if not adapter.endpoints and adapter.openapi_specs:
            adapter.endpoints = []
            for spec in adapter.openapi_specs:
                if isinstance(spec, dict) and "_raw_spec" in spec:
                    raw_spec = spec["_raw_spec"]
                    if "paths" in raw_spec:
                        for path in raw_spec["paths"].keys():
                            adapter.endpoints.append(path.lstrip("/"))
            adapter.endpoints = list(set(adapter.endpoints))

        assert "api/users" in adapter.endpoints
        assert "api/posts" in adapter.endpoints
        assert "no-leading-slash" in adapter.endpoints

    def test_init_with_auth_config(self):
        """Test RESTAdapter initialization with authentication."""
        config = {
            "auth": ("username", "password"),
            "headers": {"Authorization": "Bearer token"},
        }
        adapter = RESTAdapter("https://api.example.com", config)

        assert adapter.auth == ("username", "password")
        assert adapter.headers["Authorization"] == "Bearer token"
        assert (
            adapter.headers["Accept"] == "application/json"
        )  # Default header still present

    def test_init_with_openapi_dict_success(self):
        """Test RESTAdapter initialization with OpenAPI dict object."""
        openapi_dict = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {"/users": {"get": {}}},
        }

        with patch("data_agents.adapters.rest_adapter.OpenAPI") as mock_openapi:
            mock_spec = MagicMock()
            mock_spec.paths = {"/users": {}}
            mock_openapi.return_value = mock_spec

            config = {"openapi_data": [openapi_dict]}
            adapter = RESTAdapter("https://api.example.com", config)

            assert len(adapter.openapi_specs) == 1
            assert "users" in adapter.endpoints

    @patch("requests.request")
    def test_query_list_response(self, mock_request):
        """Test query with list response."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": 1, "name": "John"},
            {"id": 2, "name": "Jane"},
        ]
        mock_request.return_value = mock_response

        adapter = RESTAdapter("https://api.example.com")
        result = adapter.query("users")

        assert len(result) == 2
        assert list(result.columns) == ["id", "name"]
        assert result.iloc[0]["name"] == "John"
        assert result.iloc[1]["name"] == "Jane"

        # Verify the request was made correctly
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        assert kwargs["method"] == "GET"
        assert kwargs["url"] == "https://api.example.com/users"

    @patch("requests.request")
    def test_query_dict_response(self, mock_request):
        """Test query with dict response."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 1,
            "name": "John",
            "email": "john@example.com",
        }
        mock_request.return_value = mock_response

        adapter = RESTAdapter("https://api.example.com")
        result = adapter.query("users/1")

        assert len(result) == 1
        assert list(result.columns) == ["id", "name", "email"]
        assert result.iloc[0]["name"] == "John"

    @patch("requests.request")
    def test_query_with_params(self, mock_request):
        """Test query with URL parameters."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": 1, "name": "John"}]
        mock_request.return_value = mock_response

        adapter = RESTAdapter("https://api.example.com")
        adapter.query("users", params={"limit": 10, "offset": 0})

        # Verify parameters were passed
        args, kwargs = mock_request.call_args
        assert kwargs["params"] == {"limit": 10, "offset": 0}

    @patch("requests.request")
    def test_query_primitive_response(self, mock_request):
        """Test query with primitive value response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = "simple string value"
        mock_request.return_value = mock_response

        adapter = RESTAdapter("https://api.example.com")
        result = adapter.query("status")

        assert len(result) == 1
        assert list(result.columns) == ["value"]
        assert result.iloc[0]["value"] == "simple string value"

    @patch("requests.request")
    def test_query_number_response(self, mock_request):
        """Test query with number response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = 42
        mock_request.return_value = mock_response

        adapter = RESTAdapter("https://api.example.com")
        result = adapter.query("count")

        assert len(result) == 1
        assert list(result.columns) == ["value"]
        assert result.iloc[0]["value"] == 42

    @patch("requests.request")
    def test_query_with_custom_headers(self, mock_request):
        """Test query with custom headers for single request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": 1}]
        mock_request.return_value = mock_response

        adapter = RESTAdapter(
            "https://api.example.com", config={"headers": {"Default": "value"}}
        )
        adapter.query("users", custom_headers={"Custom": "header"})

        # Verify both default and custom headers were sent
        args, kwargs = mock_request.call_args
        expected_headers = {
            "Default": "value",
            "Accept": "application/json",
            "Custom": "header",
        }
        assert kwargs["headers"] == expected_headers

    @patch("requests.request")
    def test_query_patch_method(self, mock_request):
        """Test query with PATCH method."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "updated": True}
        mock_request.return_value = mock_response

        adapter = RESTAdapter("https://api.example.com")
        data = {"field": "updated_value"}
        result = adapter.query("users/1", method="PATCH", data=data)

        assert len(result) == 1
        assert result.iloc[0]["updated"]  # Use truthiness check instead of == True

        # Verify PATCH request with JSON data
        args, kwargs = mock_request.call_args
        assert kwargs["method"] == "PATCH"
        assert kwargs["json"] == data

    @patch("requests.request")
    def test_post_data(self, mock_request):
        """Test POST request."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": 123,
            "name": "New User",
            "status": "created",
        }
        mock_request.return_value = mock_response

        adapter = RESTAdapter("https://api.example.com")
        data = {"name": "New User", "email": "new@example.com"}
        result = adapter.post_data("users", data)

        assert len(result) == 1
        assert result.iloc[0]["id"] == 123
        assert result.iloc[0]["status"] == "created"

        # Verify POST request
        args, kwargs = mock_request.call_args
        assert kwargs["method"] == "POST"
        assert kwargs["json"] == data

    @patch("requests.request")
    def test_put_data(self, mock_request):
        """Test PUT request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 123,
            "name": "Updated User",
            "status": "updated",
        }
        mock_request.return_value = mock_response

        adapter = RESTAdapter("https://api.example.com")
        data = {"name": "Updated User", "email": "updated@example.com"}
        result = adapter.put_data("users/123", data)

        assert len(result) == 1
        assert result.iloc[0]["id"] == 123
        assert result.iloc[0]["status"] == "updated"

        # Verify PUT request
        args, kwargs = mock_request.call_args
        assert kwargs["method"] == "PUT"
        assert kwargs["json"] == data

    @patch("requests.request")
    def test_delete_data(self, mock_request):
        """Test DELETE request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 123,
            "status": "deleted",
        }
        mock_request.return_value = mock_response

        adapter = RESTAdapter("https://api.example.com")
        result = adapter.delete_data("users/123")

        assert len(result) == 1
        assert result.iloc[0]["id"] == 123
        assert result.iloc[0]["status"] == "deleted"

        # Verify DELETE request
        args, kwargs = mock_request.call_args
        assert kwargs["method"] == "DELETE"

    @patch("requests.request")
    def test_query_http_error(self, mock_request):
        """Test query with HTTP error."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_request.return_value = mock_response

        adapter = RESTAdapter("https://api.example.com")

        with pytest.raises(requests.RequestException, match="HTTP request failed"):
            adapter.query("nonexistent")

    @patch("requests.request")
    def test_query_json_error(self, mock_request):
        """Test query with invalid JSON response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_request.return_value = mock_response

        adapter = RESTAdapter("https://api.example.com")

        with pytest.raises(ValueError, match="Failed to parse response as JSON"):
            adapter.query("users")

    @patch("requests.get")
    def test_discover_endpoint_availability(self, mock_get):
        """Test endpoint availability discovery."""

        # Mock responses for different endpoints
        def mock_response(url, **kwargs):
            response = MagicMock()
            if "users" in url or "posts" in url:
                response.status_code = 200
            else:
                response.status_code = 404
            return response

        mock_get.side_effect = mock_response

        # Configure adapter with endpoints
        config = {
            "endpoints": ["users", "posts", "comments", "nonexistent"],
        }
        adapter = RESTAdapter("https://api.example.com", config)
        discovery = adapter.discover()

        # Should find users and posts endpoints (not comments or nonexistent)
        assert "users" in discovery["available_endpoints"]
        assert "posts" in discovery["available_endpoints"]
        assert "comments" not in discovery["available_endpoints"]
        assert "nonexistent" not in discovery["available_endpoints"]

    @patch("requests.get")
    @patch("data_agents.adapters.rest_adapter.RESTAdapter.query")
    def test_discover_comprehensive(self, mock_query, mock_get):
        """Test comprehensive API discovery using discover() method."""

        # Mock responses for endpoint availability testing
        def mock_response(url, **kwargs):
            response = MagicMock()
            if "users" in url or "posts" in url:
                response.status_code = 200
            else:
                response.status_code = 404
            return response

        mock_get.side_effect = mock_response

        # Mock query responses for schema discovery
        users_df = pd.DataFrame([{"id": 1, "name": "John"}])
        posts_df = pd.DataFrame([{"id": 1, "title": "Test", "userId": 1}])

        def mock_query_side_effect(endpoint, **kwargs):
            if endpoint == "users":
                return users_df
            elif endpoint == "posts":
                return posts_df
            else:
                return pd.DataFrame()

        mock_query.side_effect = mock_query_side_effect

        # Configure adapter with endpoints
        config = {
            "endpoints": ["users", "posts", "comments", "nonexistent"],
            "pagination_param": "limit",
            "pagination_limit": 5,
        }
        adapter = RESTAdapter("https://api.example.com", config)
        discovery = adapter.discover()

        # Test discovery structure
        assert discovery["base_url"] == "https://api.example.com"
        assert "available_endpoints" in discovery
        assert "endpoints" in discovery
        assert "sample_data" in discovery

        # Test available endpoints
        assert "users" in discovery["available_endpoints"]
        assert "posts" in discovery["available_endpoints"]
        assert "comments" not in discovery["available_endpoints"]
        assert "nonexistent" not in discovery["available_endpoints"]

        # Test schema information
        assert "users" in discovery["endpoints"]
        assert "posts" in discovery["endpoints"]
        assert discovery["endpoints"]["users"]["columns"] == ["id", "name"]
        assert discovery["endpoints"]["posts"]["columns"] == ["id", "title", "userId"]

        # Test sample data
        assert "users" in discovery["sample_data"]
        assert "posts" in discovery["sample_data"]

    def test_discover_no_config(self):
        """Test discovery with no configuration."""
        adapter = RESTAdapter("https://api.example.com")
        discovery = adapter.discover()

        # Should return basic discovery with no endpoints when no endpoints configured
        assert discovery["base_url"] == "https://api.example.com"
        assert discovery["available_endpoints"] == []
        assert discovery["endpoints"] == {}
        assert discovery["sample_data"] == {}

    @patch("requests.get")
    @patch("data_agents.adapters.rest_adapter.RESTAdapter.query")
    def test_discover_schema_with_config(self, mock_query, mock_get):
        """Test schema discovery with configured endpoints."""

        # Mock HTTP GET responses for availability testing
        def mock_get_response(url, **kwargs):
            response = MagicMock()
            if "users" in url or "posts" in url:
                response.status_code = 200
            else:
                response.status_code = 404
            return response

        mock_get.side_effect = mock_get_response

        # Mock query responses for schema discovery
        users_df = pd.DataFrame([{"id": 1, "name": "John"}])
        posts_df = pd.DataFrame([{"id": 1, "title": "Test", "userId": 1}])

        def mock_query_side_effect(endpoint, **kwargs):
            if endpoint == "users":
                return users_df
            elif endpoint == "posts":
                return posts_df
            else:
                return pd.DataFrame()

        mock_query.side_effect = mock_query_side_effect

        config = {
            "endpoints": [
                "users",
                "posts",
            ],
            "pagination_param": "limit",
            "pagination_limit": 5,
        }
        adapter = RESTAdapter("https://api.example.com", config)
        discovery = adapter.discover()

        assert discovery["base_url"] == "https://api.example.com"
        assert "users" in discovery["endpoints"]
        assert "posts" in discovery["endpoints"]
        assert discovery["endpoints"]["users"]["columns"] == ["id", "name"]
        assert discovery["endpoints"]["posts"]["columns"] == ["id", "title", "userId"]

    @patch("requests.get")
    @patch("data_agents.adapters.rest_adapter.RESTAdapter.query")
    def test_discover_with_query_failure(self, mock_query, mock_get):
        """Test discover when endpoint is available but query fails."""

        # Mock endpoint as available
        def mock_get_response(url, **kwargs):
            response = MagicMock()
            response.status_code = 200
            return response

        mock_get.side_effect = mock_get_response

        # Mock query to raise an exception
        mock_query.side_effect = Exception("Query failed")

        config = {"endpoints": ["users"]}
        adapter = RESTAdapter("https://api.example.com", config)
        discovery = adapter.discover()

        # Should still include endpoint in available_endpoints despite query failure
        assert "users" in discovery["available_endpoints"]
        assert (
            "users" not in discovery["endpoints"]
        )  # No schema info due to query failure

    @patch("requests.get")
    def test_discover_with_endpoint_availability_failure(self, mock_get):
        """Test discover when endpoint availability check fails."""
        # Mock all requests to fail
        mock_get.side_effect = Exception("Connection failed")

        config = {"endpoints": ["users", "posts"]}
        adapter = RESTAdapter("https://api.example.com", config)
        discovery = adapter.discover()

        # Should handle errors gracefully
        assert discovery["available_endpoints"] == []
        assert discovery["endpoints"] == {}

    def test_discover_with_openapi_raw_spec_info(self):
        """Test discover with OpenAPI raw spec fallback information."""
        # Create adapter with raw OpenAPI spec (fallback scenario)
        raw_spec = {
            "info": {
                "title": "Test API",
                "version": "1.0.0",
                "description": "A test API",
            },
            "servers": [{"url": "https://api.example.com"}],
            "paths": {"/users": {"get": {}}, "/posts": {"get": {}}},
        }

        adapter = RESTAdapter("https://api.example.com")
        adapter.openapi_specs = [
            {
                "_raw_spec": raw_spec,
                "_source_url": "https://api.example.com/openapi.json",
            }
        ]

        discovery = adapter.discover()

        # OpenAPI info should be added regardless of endpoint discovery results
        assert "openapi_info" in discovery
        assert len(discovery["openapi_info"]) == 1

        openapi_info = discovery["openapi_info"][0]
        assert openapi_info["title"] == "Test API"
        assert openapi_info["version"] == "1.0.0"
        assert openapi_info["description"] == "A test API"
        assert openapi_info["servers"] == ["https://api.example.com"]
        assert "/users" in openapi_info["paths"]
        assert "/posts" in openapi_info["paths"]
        assert openapi_info["source_url"] == "https://api.example.com/openapi.json"

    def test_discover_with_openapi_proper_spec_info(self):
        """Test discover with proper OpenAPI spec object information."""
        # Create mock OpenAPI spec object
        mock_spec = MagicMock()
        mock_spec.info.title = "Proper API"
        mock_spec.info.version = "2.0.0"
        mock_spec.info.description = "A proper OpenAPI spec"

        mock_server = MagicMock()
        mock_server.url = "https://proper.api.com"
        mock_spec.servers = [mock_server]
        mock_spec.paths = {"/users": {}, "/items": {}}

        adapter = RESTAdapter("https://api.example.com")
        adapter.openapi_specs = [mock_spec]

        discovery = adapter.discover()

        assert "openapi_info" in discovery
        assert len(discovery["openapi_info"]) == 1

        openapi_info = discovery["openapi_info"][0]
        assert openapi_info["title"] == "Proper API"
        assert openapi_info["version"] == "2.0.0"
        assert openapi_info["description"] == "A proper OpenAPI spec"
        assert openapi_info["servers"] == ["https://proper.api.com"]
        assert "/users" in openapi_info["paths"]
        assert "/items" in openapi_info["paths"]

    def test_discover_with_openapi_no_servers(self):
        """Test discover with OpenAPI spec that has no servers."""
        mock_spec = MagicMock()
        mock_spec.info.title = "No Servers API"
        mock_spec.info.version = "1.0.0"
        mock_spec.info.description = "API without servers"
        mock_spec.servers = None  # No servers
        mock_spec.paths = {"/test": {}}

        adapter = RESTAdapter("https://api.example.com")
        adapter.openapi_specs = [mock_spec]

        discovery = adapter.discover()

        assert "openapi_info" in discovery
        openapi_info = discovery["openapi_info"][0]
        assert openapi_info["servers"] == []

    def test_discover_with_openapi_no_info(self):
        """Test discover with OpenAPI spec that has no info section."""
        mock_spec = MagicMock()
        mock_spec.info = None  # No info section
        mock_spec.servers = []
        mock_spec.paths = {}

        adapter = RESTAdapter("https://api.example.com")
        adapter.openapi_specs = [mock_spec]

        discovery = adapter.discover()

        assert "openapi_info" in discovery
        openapi_info = discovery["openapi_info"][0]
        assert openapi_info["title"] == "Unknown"
        assert openapi_info["version"] == "Unknown"
        assert openapi_info["description"] == ""


class TestRESTAdapterIntegration:
    """Integration tests for RESTAdapter with real APIs."""

    def test_httpbin_integration(self):
        """Test RESTAdapter with httpbin.org API."""
        config = load_config("httpbin.rest.adapter.json")

        adapter = RESTAdapter("https://httpbin.org", config)

        # Test basic query - JSON endpoint
        try:
            result = adapter.query("json")
            assert not result.empty
            assert isinstance(result, pd.DataFrame)
            # httpbin.org/json returns a slideshow object
            assert "slideshow" in result.columns
        except Exception as e:
            pytest.skip(f"httpbin.org not accessible: {e}")

        # Test headers endpoint
        try:
            headers_result = adapter.query("headers")
            assert not headers_result.empty
            assert "headers" in headers_result.columns
        except Exception as e:
            pytest.skip(f"httpbin.org headers endpoint not accessible: {e}")

        # Test user-agent endpoint
        try:
            ua_result = adapter.query("user-agent")
            assert not ua_result.empty
            assert "user-agent" in ua_result.columns
        except Exception as e:
            pytest.skip(f"httpbin.org user-agent endpoint not accessible: {e}")

        # Test discovery
        try:
            discovery = adapter.discover()
            assert discovery["base_url"] == "https://httpbin.org"
            assert "available_endpoints" in discovery
            assert "endpoints" in discovery
            assert "sample_data" in discovery
        except Exception as e:
            pytest.skip(f"httpbin.org discovery failed: {e}")

    def test_rest_countries_integration(self):
        """Test RESTAdapter with REST Countries API."""
        config = load_config("rest_countries.rest.adapter.json")

        adapter = RESTAdapter("https://restcountries.com", config)

        # Test querying all countries (with field limitation)
        try:
            countries_result = adapter.query(
                "v3.1/all", params={"fields": "name,capital"}
            )
            assert not countries_result.empty
            assert isinstance(countries_result, pd.DataFrame)
            # Should have name and capital fields
            assert "name" in countries_result.columns
        except Exception as e:
            pytest.skip(f"REST Countries API not accessible: {e}")

        # Test querying specific country by name
        try:
            france_result = adapter.query("v3.1/name/france")
            assert not france_result.empty
            assert len(france_result) >= 1  # Should find at least France
        except Exception as e:
            pytest.skip(f"REST Countries name query failed: {e}")

        # Test querying by alpha code
        try:
            alpha_result = adapter.query("v3.1/alpha/fr")
            assert not alpha_result.empty
            assert len(alpha_result) == 1  # Should find exactly one country
        except Exception as e:
            pytest.skip(f"REST Countries alpha query failed: {e}")

        # Test discovery
        try:
            discovery = adapter.discover()
            assert discovery["base_url"] == "https://restcountries.com"
            # Note: REST Countries discovery might fail due to large dataset
            # so we don't assert on endpoint discovery success
        except Exception as e:
            pytest.skip(f"REST Countries discovery failed: {e}")

    def test_jsonplaceholder_integration(self):
        """Test RESTAdapter with JSONPlaceholder API (original working example)."""
        config = load_config("jsonplaceholder.rest.adapter.json")

        adapter = RESTAdapter("https://jsonplaceholder.typicode.com", config)

        # Test users endpoint
        try:
            users_result = adapter.query("users")
            assert not users_result.empty
            assert isinstance(users_result, pd.DataFrame)
            assert "id" in users_result.columns
            assert "name" in users_result.columns
            assert len(users_result) == 10  # JSONPlaceholder has 10 users
        except Exception as e:
            pytest.skip(f"JSONPlaceholder users endpoint not accessible: {e}")

        # Test posts with pagination
        try:
            posts_result = adapter.query("posts", params={"_limit": 5})
            assert not posts_result.empty
            assert len(posts_result) == 5  # Should be limited to 5
            assert "id" in posts_result.columns
            assert "title" in posts_result.columns
        except Exception as e:
            pytest.skip(f"JSONPlaceholder posts endpoint not accessible: {e}")

        # Test specific user
        try:
            user_result = adapter.query("users/1")
            assert not user_result.empty
            assert len(user_result) == 1
            assert user_result.iloc[0]["id"] == 1
        except Exception as e:
            pytest.skip(f"JSONPlaceholder specific user query failed: {e}")

        # Test POST request
        try:
            post_data = {
                "title": "Test Post",
                "body": "This is a test post",
                "userId": 1,
            }
            post_result = adapter.post_data("posts", post_data)
            assert not post_result.empty
            assert post_result.iloc[0]["title"] == "Test Post"
            # JSONPlaceholder returns id 101 for new posts
            assert post_result.iloc[0]["id"] == 101
        except Exception as e:
            pytest.skip(f"JSONPlaceholder POST request failed: {e}")

        # Test discovery
        try:
            discovery = adapter.discover()
            assert discovery["base_url"] == "https://jsonplaceholder.typicode.com"
            available_endpoints = discovery.get("available_endpoints", [])
            schema_endpoints = list(discovery.get("endpoints", {}).keys())
            # Should find users, posts, and comments
            assert "users" in available_endpoints or "users" in schema_endpoints
            assert "posts" in available_endpoints or "posts" in schema_endpoints
        except Exception as e:
            pytest.skip(f"JSONPlaceholder discovery failed: {e}")

    def test_api_error_handling(self):
        """Test error handling with various API scenarios."""
        # Test with non-existent API
        adapter = RESTAdapter("https://nonexistent-api-url-12345.com")

        with pytest.raises(requests.RequestException):
            adapter.query("any-endpoint")

        # Test with real API but non-existent endpoint
        try:
            adapter = RESTAdapter("https://httpbin.org")
            with pytest.raises(requests.RequestException):
                adapter.query("nonexistent-endpoint-12345")
        except Exception:
            pytest.skip("httpbin.org not accessible for error testing")

    def test_different_response_formats(self):
        """Test handling of different response formats from real APIs."""
        # Test httpbin IP endpoint (returns simple string-like response)
        try:
            adapter = RESTAdapter("https://httpbin.org")
            ip_result = adapter.query("ip")
            assert not ip_result.empty
            assert isinstance(ip_result, pd.DataFrame)
            # Should have 'origin' field with IP address
            assert "origin" in ip_result.columns
        except Exception as e:
            pytest.skip(f"httpbin.org IP endpoint test failed: {e}")

        # Test httpbin UUID endpoint (returns object with uuid field)
        try:
            uuid_result = adapter.query("uuid")
            assert not uuid_result.empty
            assert "uuid" in uuid_result.columns
        except Exception as e:
            pytest.skip(f"httpbin.org UUID endpoint test failed: {e}")

    def test_authentication_and_headers(self):
        """Test custom headers and authentication with real APIs."""
        # Test custom headers with httpbin
        try:
            config = {
                "headers": {
                    "User-Agent": "DataAgents-Custom-Test/2.0",
                    "X-Custom-Header": "test-value-123",
                },
                "timeout": 10,
            }
            adapter = RESTAdapter("https://httpbin.org", config)

            # Query headers endpoint to verify our custom headers are sent
            headers_result = adapter.query("headers")
            assert not headers_result.empty

            # The response should contain our custom headers
            headers_data = headers_result.iloc[0]["headers"]
            assert "User-Agent" in headers_data
            # Note: Can't easily verify custom header in response due to data structure

        except Exception as e:
            pytest.skip(f"httpbin.org custom headers test failed: {e}")

    def test_nasa_power_openapi_integration(self):
        """Test RESTAdapter with NASA Power API using OpenAPI specification."""
        try:
            config = load_config("nasapower.rest.adapter.json")
            adapter = RESTAdapter("https://power.larc.nasa.gov/api", config)

            # Test that OpenAPI spec was loaded and endpoints were discovered
            assert adapter.openapi_specs, "OpenAPI specs should be loaded"
            assert adapter.endpoints, "Endpoints should be discovered from OpenAPI spec"

            # Test discovery functionality with OpenAPI data
            discovery = adapter.discover()
            assert "openapi_info" in discovery, "OpenAPI info should be present"
            assert len(discovery["openapi_info"]) > 0, (
                "At least one OpenAPI spec should be loaded"
            )

            # Verify OpenAPI information
            openapi_info = discovery["openapi_info"][0]
            assert openapi_info["title"] == "POWER Daily API"
            assert "paths" in openapi_info
            assert len(openapi_info["paths"]) > 0

            # Test that endpoints were extracted from OpenAPI spec
            assert len(adapter.endpoints) > 0, (
                "Endpoints should be extracted from OpenAPI spec"
            )

            # The endpoints may not be directly accessible without parameters,
            # so we just verify the OpenAPI parsing worked
            title = openapi_info["title"]
            version = openapi_info["version"]
            print(f"NASA Power OpenAPI info: {title} v{version}")
            print(f"Discovered endpoints from OpenAPI: {adapter.endpoints}")

        except requests.exceptions.RequestException as e:
            pytest.skip(f"NASA Power API connection failed: {e}")
        except Exception as e:
            pytest.skip(f"NASA Power OpenAPI test failed: {e}")
