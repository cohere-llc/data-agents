#!/usr/bin/env python3
"""
Example demonstrating token-based authentication with the REST adapter.

This example shows how to use the enhanced REST adapter with:
1. API key authentication using environment variables
2. Bearer token authentication
3. GitHub Actions secrets integration

Run this example with:
    export OPENAQ_API_KEY="your-api-key-here"
    python examples/token_auth_example.py

For GitHub Actions, set OPENAQ_API_KEY as a repository secret.
"""

import sys
from pathlib import Path

# Add the src directory to the path so we can import data_agents
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data_agents.adapters.rest_adapter import RESTAdapter


def test_api_key_with_env_var():
    """Test API key authentication using environment variable."""
    print("Testing API key authentication with environment variable...")

    # Configuration using environment variable for API key
    config = {
        "auth": {"type": "api_key", "key": "X-API-Key", "env_var": "OPENAQ_API_KEY"},
        "timeout": 10,
    }

    try:
        adapter = RESTAdapter("https://api.openaq.org/v2", config)

        # Check if the auth header was set correctly
        if "X-API-Key" in adapter.headers:
            print("✓ API key authentication configured successfully")
            print("  Header 'X-API-Key' is set")
        else:
            print("✗ API key not found in headers")

        return adapter

    except ValueError as e:
        if "Environment variable" in str(e):
            print(f"⚠ Environment variable OPENAQ_API_KEY not set: {e}")
            print("  Set it with: export OPENAQ_API_KEY='your-api-key'")
        else:
            print(f"✗ Configuration error: {e}")
        return None
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return None


def test_bearer_token_direct():
    """Test bearer token authentication with direct token."""
    print("\nTesting bearer token authentication...")

    # Configuration with direct bearer token
    config = {"auth": {"type": "bearer", "token": "sample-bearer-token-123"}}

    try:
        adapter = RESTAdapter("https://httpbin.org", config)

        # Check if the authorization header was set correctly
        auth_header = adapter.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            print("✓ Bearer token authentication configured successfully")
            print(f"  Authorization header: {auth_header[:20]}...")
        else:
            print("✗ Bearer token not found in headers")

        return adapter

    except Exception as e:
        print(f"✗ Error configuring bearer token: {e}")
        return None


def test_string_token_format():
    """Test simple string token format (automatically treated as bearer)."""
    print("\nTesting simple string token format...")

    # Simple string format - should be treated as bearer token
    config = {"auth": "simple-token-123"}

    try:
        adapter = RESTAdapter("https://httpbin.org", config)

        # Check if the authorization header was set correctly
        auth_header = adapter.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            print("✓ String token authentication configured successfully")
            print(f"  Authorization header: {auth_header}")
        else:
            print("✗ String token not converted to bearer token")

        return adapter

    except Exception as e:
        print(f"✗ Error configuring string token: {e}")
        return None


def test_basic_auth_compatibility():
    """Test that basic auth still works (backward compatibility)."""
    print("\nTesting basic auth backward compatibility...")

    # Configuration with basic auth tuple
    config = {"auth": ("username", "password")}

    try:
        adapter = RESTAdapter("https://httpbin.org", config)

        # Check if basic auth is set
        if adapter.auth == ("username", "password"):
            print("✓ Basic auth configured successfully")
            print("  Auth tuple is set correctly")
        else:
            print("✗ Basic auth not configured correctly")

        return adapter

    except Exception as e:
        print(f"✗ Error configuring basic auth: {e}")
        return None


def test_github_actions_pattern():
    """Demonstrate GitHub Actions secrets pattern."""
    print("\nDemonstrating GitHub Actions secrets pattern...")

    # This is how you'd configure it in a GitHub Action
    config = {
        "auth": {
            "type": "api_key",
            "key": "X-API-Key",
            "env_var": "OPENAQ_API_KEY",  # This would be set from secrets in GHA
        }
    }

    print("GitHub Actions workflow snippet:")
    print("""
    steps:
      - name: Run data agent with API key
        env:
          OPENAQ_API_KEY: ${{ secrets.OPENAQ_API_KEY }}
        run: |
          python examples/token_auth_example.py
    """)

    return config


def main():
    """Run all authentication tests."""
    print("REST Adapter Token Authentication Examples")
    print("=" * 50)

    # Test different authentication methods
    api_key_adapter = test_api_key_with_env_var()
    bearer_adapter = test_bearer_token_direct()
    string_adapter = test_string_token_format()
    basic_adapter = test_basic_auth_compatibility()
    github_config = test_github_actions_pattern()

    print("\nSummary:")
    print(f"  API Key (env var): {'✓' if api_key_adapter else '✗'}")
    print(f"  Bearer Token:      {'✓' if bearer_adapter else '✗'}")
    print(f"  String Token:      {'✓' if string_adapter else '✗'}")
    print(f"  Basic Auth:        {'✓' if basic_adapter else '✗'}")
    print(f"  GitHub Pattern:    {'✓' if github_config else '✗'}")

    # If we have a working adapter, try a simple request
    working_adapter = bearer_adapter or string_adapter or basic_adapter
    if working_adapter:
        print("\nTesting a simple request with HTTPBin...")
        try:
            # Use HTTPBin to test authentication headers
            result = working_adapter.query("headers")
            print("✓ Request successful!")
            print(f"  Response shape: {result.shape}")

            # Show what headers were sent
            if not result.empty and "headers" in result.columns:
                headers = result["headers"].iloc[0]
                if isinstance(headers, dict):
                    auth_headers = {
                        k: v
                        for k, v in headers.items()
                        if "auth" in k.lower() or "api" in k.lower()
                    }
                    if auth_headers:
                        print(f"  Auth headers sent: {list(auth_headers.keys())}")

        except Exception as e:
            print(f"⚠ Request failed: {e}")


if __name__ == "__main__":
    main()
