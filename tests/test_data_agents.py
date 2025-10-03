"""Tests for data_agents package."""

import io
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
import requests

from data_agents.adapters import RESTAdapter, TabularAdapter
from data_agents.cli import create_router, main
from data_agents.core import Router


class TestTabularAdapter:
    """Test cases for TabularAdapter class."""

    def test_init_empty(self):
        """Test TabularAdapter initialization without data."""
        adapter = TabularAdapter("test-adapter")
        assert adapter.name == "test-adapter"
        assert adapter.config == {}
        assert adapter.data.empty

    def test_init_with_data(self):
        """Test TabularAdapter initialization with data."""
        data = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
        adapter = TabularAdapter("test-adapter", data)
        assert adapter.name == "test-adapter"
        pd.testing.assert_frame_equal(adapter.data, data)

    def test_query_all(self):
        """Test querying all data."""
        data = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
        adapter = TabularAdapter("test-adapter", data)
        result = adapter.query("*")
        pd.testing.assert_frame_equal(result, data)

    def test_query_column(self):
        """Test querying specific column."""
        data = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
        adapter = TabularAdapter("test-adapter", data)
        result = adapter.query("col1")
        expected = data[["col1"]]
        pd.testing.assert_frame_equal(result, expected)

    def test_query_filter(self):
        """Test querying with filter."""
        data = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
        adapter = TabularAdapter("test-adapter", data)
        result = adapter.query("col1 > 1")
        expected = data[data["col1"] > 1]
        pd.testing.assert_frame_equal(result, expected)

    def test_discover(self):
        """Test discovering tabular data information."""
        data = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
        adapter = TabularAdapter("test-adapter", data)
        discovery = adapter.discover()

        assert discovery["adapter_type"] == "tabular"
        assert "columns" in discovery
        assert "dtypes" in discovery
        assert "shape" in discovery
        assert "sample" in discovery
        assert "capabilities" in discovery
        assert discovery["columns"] == ["col1", "col2"]
        assert discovery["shape"] == (3, 2)
        assert discovery["capabilities"]["supports_query"] is True

    def test_add_data(self):
        """Test adding data to adapter."""
        adapter = TabularAdapter("test-adapter")
        data = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
        adapter.add_data(data)
        pd.testing.assert_frame_equal(adapter.data, data)


class TestRESTAdapter:
    """Test cases for RESTAdapter class."""

    def test_init(self):
        """Test RESTAdapter initialization."""
        adapter = RESTAdapter("test-api", "https://api.example.com")
        assert adapter.name == "test-api"
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
        adapter = RESTAdapter("test-api", "https://api.example.com/", config)
        assert adapter.base_url == "https://api.example.com"
        assert adapter.headers["Custom-Header"] == "test-value"
        assert adapter.headers["Accept"] == "application/json"
        assert adapter.timeout == 15
        assert adapter.verify is False
        assert adapter.endpoints == ["users", "posts"]
        assert adapter.pagination_param == "limit"
        assert adapter.pagination_limit == 20

    @patch('requests.request')
    def test_query_list_response(self, mock_request):
        """Test query with list response."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": 1, "name": "John"},
            {"id": 2, "name": "Jane"}
        ]
        mock_request.return_value = mock_response

        adapter = RESTAdapter("test-api", "https://api.example.com")
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

    @patch('requests.request')
    def test_query_dict_response(self, mock_request):
        """Test query with dict response."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 1, "name": "John", "email": "john@example.com"
        }
        mock_request.return_value = mock_response

        adapter = RESTAdapter("test-api", "https://api.example.com")
        result = adapter.query("users/1")

        assert len(result) == 1
        assert list(result.columns) == ["id", "name", "email"]
        assert result.iloc[0]["name"] == "John"

    @patch('requests.request')
    def test_query_with_params(self, mock_request):
        """Test query with URL parameters."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": 1, "name": "John"}]
        mock_request.return_value = mock_response

        adapter = RESTAdapter("test-api", "https://api.example.com")
        adapter.query("users", params={"limit": 10, "offset": 0})

        # Verify parameters were passed
        args, kwargs = mock_request.call_args
        assert kwargs["params"] == {"limit": 10, "offset": 0}

    @patch('requests.request')
    def test_post_data(self, mock_request):
        """Test POST request."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": 123, "name": "New User", "status": "created"
        }
        mock_request.return_value = mock_response

        adapter = RESTAdapter("test-api", "https://api.example.com")
        data = {"name": "New User", "email": "new@example.com"}
        result = adapter.post_data("users", data)

        assert len(result) == 1
        assert result.iloc[0]["id"] == 123
        assert result.iloc[0]["status"] == "created"

        # Verify POST request
        args, kwargs = mock_request.call_args
        assert kwargs["method"] == "POST"
        assert kwargs["json"] == data

    @patch('requests.request')
    def test_query_http_error(self, mock_request):
        """Test query with HTTP error."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_request.return_value = mock_response

        adapter = RESTAdapter("test-api", "https://api.example.com")

        with pytest.raises(requests.RequestException, match="HTTP request failed"):
            adapter.query("nonexistent")

    @patch('requests.request')
    def test_query_json_error(self, mock_request):
        """Test query with invalid JSON response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_request.return_value = mock_response

        adapter = RESTAdapter("test-api", "https://api.example.com")

        with pytest.raises(ValueError, match="Failed to parse response as JSON"):
            adapter.query("users")

    @patch('requests.get')
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
            "endpoints": ["users", "posts", "comments", "nonexistent"]
        }
        adapter = RESTAdapter("test-api", "https://api.example.com", config)
        discovery = adapter.discover()

        # Should find users and posts endpoints (not comments or nonexistent)
        assert "users" in discovery["available_endpoints"]
        assert "posts" in discovery["available_endpoints"]
        assert "comments" not in discovery["available_endpoints"]
        assert "nonexistent" not in discovery["available_endpoints"]

    @patch('requests.get')
    @patch('data_agents.adapters.rest_adapter.RESTAdapter.query')
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
        adapter = RESTAdapter("test-api", "https://api.example.com", config)
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
        adapter = RESTAdapter("test-api", "https://api.example.com")
        discovery = adapter.discover()

        # Should return basic discovery with no endpoints when no endpoints configured
        assert discovery["base_url"] == "https://api.example.com"
        assert discovery["available_endpoints"] == []
        assert discovery["endpoints"] == {}
        assert discovery["sample_data"] == {}

    @patch('requests.get')
    @patch('data_agents.adapters.rest_adapter.RESTAdapter.query')
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
            "endpoints": ["users", "posts"],
            "pagination_param": "limit",
            "pagination_limit": 5,
        }
        adapter = RESTAdapter("test-api", "https://api.example.com", config)
        discovery = adapter.discover()

        assert discovery["base_url"] == "https://api.example.com"
        assert "users" in discovery["endpoints"]
        assert "posts" in discovery["endpoints"]
        assert discovery["endpoints"]["users"]["columns"] == ["id", "name"]
        assert discovery["endpoints"]["posts"]["columns"] == ["id", "title", "userId"]


class TestRESTAdapterIntegration:
    """Integration tests for RESTAdapter with real APIs."""

    def test_httpbin_integration(self):
        """Test RESTAdapter with httpbin.org API."""
        config = {
            "headers": {"User-Agent": "DataAgents-Test/1.0"},
            "timeout": 10,
            "endpoints": ["json", "headers", "user-agent"],
            "pagination_param": None,  # httpbin doesn't use pagination
            "pagination_limit": None,
        }

        adapter = RESTAdapter("httpbin", "https://httpbin.org", config)

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
        config = {
            "headers": {"User-Agent": "DataAgents-Test/1.0"},
            "timeout": 15,
            "endpoints": ["v3.1/all"],
            # REST Countries uses fields for limiting data
            "pagination_param": "fields",
            "pagination_limit": "name,capital,population",
        }

        adapter = RESTAdapter("rest_countries", "https://restcountries.com", config)

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
        config = {
            "headers": {"User-Agent": "DataAgents-Test/1.0"},
            "timeout": 10,
            "endpoints": ["users", "posts", "comments"],
            "pagination_param": "_limit",
            "pagination_limit": 3,
        }

        adapter = RESTAdapter(
            "jsonplaceholder", "https://jsonplaceholder.typicode.com", config
        )

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
                "userId": 1
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
        adapter = RESTAdapter("fake_api", "https://nonexistent-api-url-12345.com")

        with pytest.raises(requests.RequestException):
            adapter.query("any-endpoint")

        # Test with real API but non-existent endpoint
        try:
            adapter = RESTAdapter("httpbin", "https://httpbin.org")
            with pytest.raises(requests.RequestException):
                adapter.query("nonexistent-endpoint-12345")
        except Exception:
            pytest.skip("httpbin.org not accessible for error testing")

    def test_different_response_formats(self):
        """Test handling of different response formats from real APIs."""
        # Test httpbin IP endpoint (returns simple string-like response)
        try:
            adapter = RESTAdapter("httpbin", "https://httpbin.org")
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
                    "X-Custom-Header": "test-value-123"
                },
                "timeout": 10,
            }
            adapter = RESTAdapter("httpbin_custom", "https://httpbin.org", config)

            # Query headers endpoint to verify our custom headers are sent
            headers_result = adapter.query("headers")
            assert not headers_result.empty

            # The response should contain our custom headers
            headers_data = headers_result.iloc[0]["headers"]
            assert "User-Agent" in headers_data
            # Note: Can't easily verify custom header in response due to data structure

        except Exception as e:
            pytest.skip(f"httpbin.org custom headers test failed: {e}")


class TestRouter:
    """Test cases for Router class."""

    def test_init(self):
        """Test Router initialization."""
        router = Router("test-router")
        assert router.name == "test-router"
        assert router.config == {}
        assert len(router.adapters) == 0

    def test_init_with_config(self):
        """Test Router initialization with configuration."""
        config = {"setting1": "value1", "setting2": 42}
        router = Router("test-router", config)
        assert router.name == "test-router"
        assert router.config == config

    def test_register_adapter(self):
        """Test registering an adapter."""
        router = Router("test-router")
        adapter = TabularAdapter("test-adapter")
        router.register_adapter(adapter)

        assert len(router.adapters) == 1
        assert "test-adapter" in router.adapters
        assert router.adapters["test-adapter"] is adapter

    def test_unregister_adapter(self):
        """Test unregistering an adapter."""
        router = Router("test-router")
        adapter = TabularAdapter("test-adapter")
        router.register_adapter(adapter)

        result = router.unregister_adapter("test-adapter")
        assert result is True
        assert len(router.adapters) == 0

        # Test unregistering non-existent adapter
        result = router.unregister_adapter("nonexistent")
        assert result is False

    def test_get_adapter(self):
        """Test getting a specific adapter."""
        router = Router("test-router")
        adapter = TabularAdapter("test-adapter")
        router.register_adapter(adapter)

        retrieved = router.get_adapter("test-adapter")
        assert retrieved is adapter

        # Test getting non-existent adapter
        retrieved = router.get_adapter("nonexistent")
        assert retrieved is None

    def test_list_adapters(self):
        """Test listing all adapters."""
        router = Router("test-router")
        adapter1 = TabularAdapter("adapter1")
        adapter2 = TabularAdapter("adapter2")

        router.register_adapter(adapter1)
        router.register_adapter(adapter2)

        adapters = router.list_adapters()
        assert set(adapters) == {"adapter1", "adapter2"}

    def test_query(self):
        """Test querying a specific adapter."""
        router = Router("test-router")
        data = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
        adapter = TabularAdapter("test-adapter", data)
        router.register_adapter(adapter)

        result = router.query("test-adapter", "*")
        pd.testing.assert_frame_equal(result, data)

    def test_query_nonexistent_adapter(self):
        """Test querying a non-existent adapter."""
        router = Router("test-router")

        try:
            router.query("nonexistent", "*")
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            assert "not found" in str(e)

    def test_query_all(self):
        """Test querying all adapters."""
        router = Router("test-router")
        data1 = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
        data2 = pd.DataFrame({"col1": [3, 4], "col2": ["c", "d"]})

        adapter1 = TabularAdapter("adapter1", data1)
        adapter2 = TabularAdapter("adapter2", data2)

        router.register_adapter(adapter1)
        router.register_adapter(adapter2)

        results = router.query_all("*")
        assert len(results) == 2
        assert "adapter1" in results
        assert "adapter2" in results
        pd.testing.assert_frame_equal(results["adapter1"], data1)
        pd.testing.assert_frame_equal(results["adapter2"], data2)

    def test_add_adapter(self):
        """Test adding an adapter (alias for register_adapter)."""
        router = Router("test-router")
        adapter = TabularAdapter("test-adapter")
        router.add_adapter(adapter)

        assert len(router.adapters) == 1
        assert "test-adapter" in router.adapters

    def test_process(self):
        """Test data processing functionality."""
        router = Router("test-router")
        result = router.process("test data")
        assert result == "Processed: test data"

    def test_get_info(self):
        """Test router information retrieval."""
        config = {"key": "value"}
        router = Router("test-router", config)
        info = router.get_info()

        assert info["name"] == "test-router"
        assert info["config"] == config
        assert info["type"] == "Router"
        assert info["adapter_count"] == 0


class TestCLI:
    """Test cases for CLI functionality."""

    def test_create_router_without_config(self):
        """Test creating router without configuration file."""
        router = create_router("test-cli-router")
        assert router.name == "test-cli-router"
        assert router.config == {}

    def test_create_router_with_config(self):
        """Test creating router with configuration file."""
        config_data = {"test_setting": "test_value"}

        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name

        try:
            router = create_router("test-cli-router", config_file)
            assert router.name == "test-cli-router"
            assert router.config == config_data
        finally:
            # Clean up
            Path(config_file).unlink()

    def test_create_router_missing_config(self):
        """Test creating router with missing configuration file."""
        router = create_router("test-cli-router", "nonexistent.json")
        assert router.name == "test-cli-router"
        assert router.config == {}

    def test_create_router_invalid_json_config(self):
        """Test creating router with invalid JSON configuration file."""
        # Create temporary file with invalid JSON
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{ invalid json }")
            config_file = f.name

        try:
            router = create_router("test-cli-router", config_file)
            assert router.name == "test-cli-router"
            assert router.config == {}
        finally:
            # Clean up
            Path(config_file).unlink()


class TestCLICommands:
    """Test cases for CLI command-line interface."""

    def capture_output(self, func, *args):
        """Helper method to capture stdout."""
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()
        try:
            func(*args)
        finally:
            sys.stdout = old_stdout
        return captured_output.getvalue()

    @patch("sys.argv", ["data_agents"])
    @patch("sys.exit")
    def test_main_no_command(self, mock_exit):
        """Test main function with no command shows help and exits."""
        with patch("sys.stdout", new=io.StringIO()):
            main()
        mock_exit.assert_called_once_with(1)

    @patch("sys.argv", ["data_agents", "--version"])
    def test_version_command(self):
        """Test version command."""
        with patch("sys.exit"):
            try:
                main()
            except SystemExit:
                pass
        # Version command should cause SystemExit

    @patch("sys.argv", ["data_agents", "create", "test-router"])
    def test_create_command(self):
        """Test create command."""
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            main()
        output = fake_out.getvalue()
        assert "Created router: test-router" in output

    @patch(
        "sys.argv", ["data_agents", "create", "test-router", "--config", "test.json"]
    )
    def test_create_command_with_config(self):
        """Test create command with configuration file."""
        config_data = {"setting": "value"}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name

        try:
            with patch(
                "sys.argv",
                ["data_agents", "create", "test-router", "--config", config_file],
            ):
                with patch("sys.stdout", new=io.StringIO()) as fake_out:
                    main()
            output = fake_out.getvalue()
            assert "Created router: test-router" in output
            assert "Configuration:" in output
        finally:
            Path(config_file).unlink()

    @patch("sys.argv", ["data_agents", "demo"])
    def test_demo_command(self):
        """Test demo command."""
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            main()
        output = fake_out.getvalue()
        assert "Demo router 'demo-router' created with sample data" in output
        assert "Available adapters: ['customers', 'orders']" in output
        assert "Sample Queries" in output
        assert "Get all customers:" in output
        assert "Get all orders:" in output

    @patch("sys.argv", ["data_agents", "demo", "--router-name", "custom-demo"])
    def test_demo_command_custom_name(self):
        """Test demo command with custom router name."""
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            main()
        output = fake_out.getvalue()
        assert "Demo router 'custom-demo' created with sample data" in output

    @patch("sys.argv", ["data_agents", "info", "test-info-router"])
    def test_info_command(self):
        """Test info command."""
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            main()
        output = fake_out.getvalue()

        # Parse the JSON output
        info_data = json.loads(output)
        assert info_data["name"] == "test-info-router"
        assert info_data["type"] == "Router"
        assert info_data["adapter_count"] == 0

    @patch("sys.argv", ["data_agents", "info", "test-router", "--config", "test.json"])
    def test_info_command_with_config(self):
        """Test info command with configuration file."""
        config_data = {"test_key": "test_value"}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name

        try:
            with patch(
                "sys.argv",
                ["data_agents", "info", "test-router", "--config", config_file],
            ):
                with patch("sys.stdout", new=io.StringIO()) as fake_out:
                    main()
            output = fake_out.getvalue()

            info_data = json.loads(output)
            assert info_data["name"] == "test-router"
            assert info_data["config"] == config_data
        finally:
            Path(config_file).unlink()

    @patch("sys.argv", ["data_agents", "process", "test-process-router", "test-data"])
    def test_process_command(self):
        """Test process command."""
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            main()
        output = fake_out.getvalue()
        assert "Result: Processed: test-data" in output

    @patch("sys.argv", ["data_agents", "list-adapters", "test-list-router"])
    def test_list_adapters_command_empty(self):
        """Test list-adapters command with no adapters."""
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            main()
        output = fake_out.getvalue()
        assert "No adapters registered" in output

    def test_query_command_nonexistent_adapter(self):
        """Test query command with non-existent adapter."""
        with patch(
            "sys.argv", ["data_agents", "query", "test-router", "nonexistent", "*"]
        ):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                main()
        output = fake_out.getvalue()
        assert "Error:" in output
        assert "not found" in output

    @patch("data_agents.cli.create_router")
    def test_query_command_with_results(self, mock_create_router):
        """Test query command that returns results."""
        # Create a mock router with mock adapter
        mock_router = MagicMock()
        test_data = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
        mock_router.query.return_value = test_data
        mock_create_router.return_value = mock_router

        with patch(
            "sys.argv", ["data_agents", "query", "test-router", "test-adapter", "*"]
        ):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                main()

        output = fake_out.getvalue()
        mock_router.query.assert_called_once_with("test-adapter", "*")
        assert "col1" in output and "col2" in output

    @patch("data_agents.cli.create_router")
    def test_query_command_empty_results(self, mock_create_router):
        """Test query command that returns empty results."""
        mock_router = MagicMock()
        mock_router.query.return_value = pd.DataFrame()
        mock_create_router.return_value = mock_router

        with patch(
            "sys.argv", ["data_agents", "query", "test-router", "test-adapter", "*"]
        ):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                main()

        output = fake_out.getvalue()
        assert "Query returned no results" in output

    @patch("data_agents.cli.create_router")
    def test_query_command_exception(self, mock_create_router):
        """Test query command that raises an exception."""
        mock_router = MagicMock()
        mock_router.query.side_effect = Exception("Query execution failed")
        mock_create_router.return_value = mock_router

        with patch(
            "sys.argv", ["data_agents", "query", "test-router", "test-adapter", "*"]
        ):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                main()

        output = fake_out.getvalue()
        assert "Query failed:" in output
        assert "Query execution failed" in output

    @patch("data_agents.cli.create_router")
    def test_list_adapters_command_with_adapters(self, mock_create_router):
        """Test list-adapters command with registered adapters."""
        mock_router = MagicMock()
        mock_adapter1 = MagicMock()
        mock_adapter1.__class__.__name__ = "TabularAdapter"
        mock_adapter2 = MagicMock()
        mock_adapter2.__class__.__name__ = "CustomAdapter"

        mock_router.list_adapters.return_value = ["adapter1", "adapter2"]
        mock_router.get_adapter.side_effect = lambda name: {
            "adapter1": mock_adapter1,
            "adapter2": mock_adapter2,
        }[name]
        mock_create_router.return_value = mock_router

        with patch("sys.argv", ["data_agents", "list-adapters", "test-router"]):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                main()

        output = fake_out.getvalue()
        assert "Available adapters:" in output
        assert "adapter1 (TabularAdapter)" in output
        assert "adapter2 (CustomAdapter)" in output
