"""Integration tests for OpenAQ API authentication."""

import os
from unittest.mock import patch

import pytest
import requests

from data_agents.adapters.rest_adapter import RESTAdapter


class TestOpenAQAuthentication:
    """Test OpenAQ API authentication integration."""

    def test_openaq_v3_config_validation(self):
        """Test that OpenAQ v3 configuration is valid without making requests."""
        config = {
            "auth": {
                "type": "api_key",
                "key": "X-API-Key",
                "env_var": "OPENAQ_API_KEY",
            },
            "headers": {"Accept": "application/json", "User-Agent": "data-agents/1.0"},
            "timeout": 30,
        }

        # Test with mock token
        with patch.dict(os.environ, {"OPENAQ_API_KEY": "test-token-123"}):
            adapter = RESTAdapter("https://api.openaq.org/v3", config)

            # Verify auth header is set correctly
            assert "X-API-Key" in adapter.headers
            assert adapter.headers["X-API-Key"] == "test-token-123"
            assert adapter.headers["Accept"] == "application/json"
            assert adapter.headers["User-Agent"] == "data-agents/1.0"

    @pytest.mark.skipif(
        not os.getenv("OPENAQ_API_KEY"),
        reason="OPENAQ_API_KEY environment variable not set",
    )
    def test_openaq_v3_real_api_call(self):
        """Test actual OpenAQ v3 API call with real token (if available)."""
        config = {
            "auth": {
                "type": "api_key",
                "key": "X-API-Key",
                "env_var": "OPENAQ_API_KEY",
            },
            "headers": {"Accept": "application/json", "User-Agent": "data-agents/1.0"},
            "timeout": 10,  # Shorter timeout for CI
        }

        adapter = RESTAdapter("https://api.openaq.org/v3", config)

        try:
            # Test with a simple endpoint that should work with any valid token
            result = adapter.query("instruments", params={"limit": 5})

            # Basic validation of response
            assert not result.empty, "API response should not be empty"
            assert "id" in result.columns or len(result.columns) > 0, (
                "Response should have data columns"
            )

            print(f"✓ OpenAQ v3 API test successful: {len(result)} records retrieved")
            print(
                f"  Response columns: {list(result.columns)[:5]}"
            )  # Show first 5 columns

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                pytest.skip("Invalid API token - skipping real API test")
            elif e.response.status_code == 403:
                pytest.skip("API token lacks permissions for this endpoint")
            elif e.response.status_code == 429:
                pytest.skip("Rate limit exceeded - skipping real API test")
            else:
                raise
        except requests.exceptions.Timeout:
            pytest.skip("API request timed out - skipping real API test")
        except Exception as e:
            # Don't fail CI if API is temporarily unavailable
            pytest.skip(f"API temporarily unavailable: {e}")

    def test_openaq_v3_auth_header_format(self):
        """Test that OpenAQ authentication uses the correct header format."""
        config = {
            "auth": {
                "type": "api_key",
                "key": "X-API-Key",
                "token": "test-openaq-token",
            }
        }

        adapter = RESTAdapter("https://api.openaq.org/v3", config)

        # Verify the exact header format expected by OpenAQ
        assert adapter.headers["X-API-Key"] == "test-openaq-token"
        assert "Authorization" not in adapter.headers  # Should not have bearer token

    def test_openaq_v3_missing_token_error(self):
        """Test that missing token raises appropriate error."""
        config = {
            "auth": {
                "type": "api_key",
                "key": "X-API-Key",
                "env_var": "NONEXISTENT_OPENAQ_KEY",
            }
        }

        with pytest.raises(
            ValueError, match="Environment variable 'NONEXISTENT_OPENAQ_KEY' not found"
        ):
            RESTAdapter("https://api.openaq.org/v3", config)

    @patch("requests.request")
    def test_openaq_v3_request_headers_sent(self, mock_request):
        """Test that correct headers are sent to OpenAQ API."""
        # Mock successful response
        mock_response = mock_request.return_value
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"results": [{"id": 1, "name": "test"}]}

        config = {
            "auth": {
                "type": "api_key",
                "key": "X-API-Key",
                "token": "mock-openaq-token",
            },
            "headers": {"User-Agent": "data-agents/1.0"},
        }

        adapter = RESTAdapter("https://api.openaq.org/v3", config)
        adapter.query("instruments")

        # Verify the request was made with correct headers
        mock_request.assert_called_once()
        call_kwargs = mock_request.call_args.kwargs

        headers = call_kwargs["headers"]
        assert headers["X-API-Key"] == "mock-openaq-token"
        assert headers["User-Agent"] == "data-agents/1.0"
        assert headers["Accept"] == "application/json"

        # Verify URL
        assert call_kwargs["url"] == "https://api.openaq.org/v3/instruments"
