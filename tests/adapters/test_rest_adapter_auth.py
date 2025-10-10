"""Tests for REST adapter token authentication functionality."""

import os
from unittest.mock import MagicMock, patch

import pytest

from data_agents.adapters.rest_adapter import RESTAdapter


class TestRESTAdapterAuthentication:
    """Test token authentication features in REST adapter."""

    def test_basic_auth_tuple_backward_compatibility(self):
        """Test that basic auth tuples still work."""
        config = {"auth": ("username", "password")}

        adapter = RESTAdapter("https://example.com", config)

        assert adapter.auth == ("username", "password")
        assert "Authorization" not in adapter.headers

    def test_bearer_token_string_format(self):
        """Test simple string format is treated as bearer token."""
        config = {"auth": "test-token-123"}

        adapter = RESTAdapter("https://example.com", config)

        assert adapter.auth is None
        assert adapter.headers["Authorization"] == "Bearer test-token-123"

    def test_bearer_token_dict_format(self):
        """Test dict format with bearer token."""
        config = {"auth": {"type": "bearer", "token": "test-bearer-token"}}

        adapter = RESTAdapter("https://example.com", config)

        assert adapter.auth is None
        assert adapter.headers["Authorization"] == "Bearer test-bearer-token"

    def test_api_key_auth(self):
        """Test API key authentication."""
        config = {
            "auth": {"type": "api_key", "key": "X-API-Key", "token": "test-api-key"}
        }

        adapter = RESTAdapter("https://example.com", config)

        assert adapter.auth is None
        assert adapter.headers["X-API-Key"] == "test-api-key"

    def test_api_key_custom_header(self):
        """Test API key with custom header name."""
        config = {
            "auth": {
                "type": "api_key",
                "key": "X-Custom-API-Key",
                "token": "custom-key-value",
            }
        }

        adapter = RESTAdapter("https://example.com", config)

        assert adapter.headers["X-Custom-API-Key"] == "custom-key-value"

    def test_basic_auth_dict_format(self):
        """Test basic auth using dict format."""
        config = {"auth": {"type": "basic", "username": "user", "password": "pass"}}

        adapter = RESTAdapter("https://example.com", config)

        assert adapter.auth == ("user", "pass")
        assert "Authorization" not in adapter.headers

    @patch.dict(os.environ, {"TEST_API_KEY": "env-api-key-123"})
    def test_bearer_token_from_env_var(self):
        """Test bearer token from environment variable."""
        config = {"auth": {"type": "bearer", "env_var": "TEST_API_KEY"}}

        adapter = RESTAdapter("https://example.com", config)

        assert adapter.headers["Authorization"] == "Bearer env-api-key-123"

    @patch.dict(os.environ, {"TEST_API_KEY": "env-api-key-456"})
    def test_api_key_from_env_var(self):
        """Test API key from environment variable."""
        config = {
            "auth": {"type": "api_key", "key": "X-API-Key", "env_var": "TEST_API_KEY"}
        }

        adapter = RESTAdapter("https://example.com", config)

        assert adapter.headers["X-API-Key"] == "env-api-key-456"

    @patch.dict(os.environ, {"TEST_TOKEN": "github-secret-token"})
    def test_string_token_with_env_var_reference(self):
        """Test string token with environment variable reference."""
        config = {"auth": "${TEST_TOKEN}"}

        adapter = RESTAdapter("https://example.com", config)

        assert adapter.headers["Authorization"] == "Bearer github-secret-token"

    def test_missing_env_var_raises_error(self):
        """Test that missing environment variable raises ValueError."""
        config = {"auth": {"type": "bearer", "env_var": "NONEXISTENT_VAR"}}

        with pytest.raises(
            ValueError, match="Environment variable 'NONEXISTENT_VAR' not found"
        ):
            RESTAdapter("https://example.com", config)

    def test_string_env_var_reference_missing_raises_error(self):
        """Test that missing env var in string reference raises error."""
        config = {"auth": "${NONEXISTENT_VAR}"}

        with pytest.raises(
            ValueError, match="Environment variable 'NONEXISTENT_VAR' not found"
        ):
            RESTAdapter("https://example.com", config)

    def test_missing_token_and_env_var_raises_error(self):
        """Test that missing both token and env_var raises error."""
        config = {
            "auth": {
                "type": "bearer"
                # Missing both token and env_var
            }
        }

        with pytest.raises(
            ValueError, match="Either 'token' or 'env_var' must be provided"
        ):
            RESTAdapter("https://example.com", config)

    def test_unsupported_auth_type_raises_error(self):
        """Test that unsupported auth type raises error."""
        config = {
            "auth": {
                "type": "oauth2",  # Unsupported type
                "token": "some-token",
            }
        }

        with pytest.raises(ValueError, match="Unsupported auth type: oauth2"):
            RESTAdapter("https://example.com", config)

    def test_no_auth_config_works(self):
        """Test that adapter works without auth configuration."""
        adapter = RESTAdapter("https://example.com")

        assert adapter.auth is None
        assert "Authorization" not in adapter.headers

    def test_empty_auth_config_works(self):
        """Test that empty auth config is handled gracefully."""
        config = {"auth": None}

        adapter = RESTAdapter("https://example.com", config)

        assert adapter.auth is None
        assert "Authorization" not in adapter.headers

    @patch("requests.request")
    def test_auth_headers_sent_in_request(self, mock_request):
        """Test that authentication headers are included in requests."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [{"test": "data"}]
        mock_request.return_value = mock_response

        config = {"auth": {"type": "api_key", "key": "X-API-Key", "token": "test-key"}}

        adapter = RESTAdapter("https://example.com", config)
        adapter.query("test")

        # Verify the request was made with correct headers
        mock_request.assert_called_once()
        call_args = mock_request.call_args

        assert "headers" in call_args.kwargs
        headers = call_args.kwargs["headers"]
        assert headers["X-API-Key"] == "test-key"
        assert headers["Accept"] == "application/json"

    @patch("requests.request")
    def test_basic_auth_sent_in_request(self, mock_request):
        """Test that basic auth is included in requests."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [{"test": "data"}]
        mock_request.return_value = mock_response

        config = {"auth": ("username", "password")}

        adapter = RESTAdapter("https://example.com", config)
        adapter.query("test")

        # Verify the request was made with correct auth
        mock_request.assert_called_once()
        call_args = mock_request.call_args

        assert "auth" in call_args.kwargs
        assert call_args.kwargs["auth"] == ("username", "password")
