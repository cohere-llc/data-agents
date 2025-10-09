#!/usr/bin/env python3
"""
Example demonstrating configurable RESTAdapter with different APIs.

This example shows how to configure the RESTAdapter for different
REST APIs by providing API-specific configuration.
"""

from data_agents.adapters import RESTAdapter
from data_agents.core import Router


def create_jsonplaceholder_adapter() -> RESTAdapter:
    """Create a RESTAdapter configured for JSONPlaceholder API."""
    config = {
        "headers": {"User-Agent": "DataAgents-ConfigExample/1.0"},
        "timeout": 15,
        # JSONPlaceholder endpoints for discovery
        "endpoints": ["users", "posts", "comments", "albums", "photos", "todos"],
        "pagination_param": "_limit",
        "pagination_limit": 5,
    }

    return RESTAdapter(
        name="jsonplaceholder",
        base_url="https://jsonplaceholder.typicode.com",
        config=config,
    )


def create_httpbin_adapter() -> RESTAdapter:
    """Create a RESTAdapter configured for httpbin.org API."""
    config = {
        "headers": {"User-Agent": "DataAgents-ConfigExample/1.0"},
        "timeout": 10,
        # httpbin endpoints for discovery
        "endpoints": ["json", "headers", "user-agent", "ip", "uuid"],
        # httpbin doesn't use pagination
        "pagination_param": None,
        "pagination_limit": None,
    }

    return RESTAdapter(name="httpbin", base_url="https://httpbin.org", config=config)


def create_rest_countries_adapter() -> RESTAdapter:
    """Create a RESTAdapter configured for REST Countries API."""
    config = {
        "headers": {"User-Agent": "DataAgents-ConfigExample/1.0"},
        "timeout": 20,
        # REST Countries endpoints for discovery
        "endpoints": ["v3.1/all", "v3.1/name/united", "v3.1/alpha/us"],
        # REST Countries supports fields parameter for limiting data
        "pagination_param": "fields",
        "pagination_limit": "name,capital,population",  # Limit fields instead of count
    }

    return RESTAdapter(
        name="rest_countries", base_url="https://restcountries.com", config=config
    )


def demonstrate_api_adapter(adapter_name: str, adapter: RESTAdapter) -> None:
    """Demonstrate functionality of a specific API adapter."""
    print(f"\n🔍 Testing {adapter_name} API")
    print("-" * 40)

    # Get discovery information
    discovery = adapter.discover()
    available_endpoints = discovery.get("available_endpoints", [])
    schema_endpoints = list(discovery.get("endpoints", {}).keys())

    if available_endpoints:
        print(f"✅ Available endpoints: {available_endpoints}")

    if schema_endpoints:
        print(f"✅ Schema endpoints: {schema_endpoints}")

        # Test first schema endpoint
        first_endpoint = schema_endpoints[0]
        try:
            result = adapter.query(first_endpoint)
            print(f"✅ Query '{first_endpoint}' returned {len(result)} records")
            if not result.empty:
                print(f"   Columns: {list(result.columns)}")
                print(f"   Sample data shape: {result.shape}")
        except Exception as e:
            print(f"❌ Query '{first_endpoint}' failed: {e}")

    if not available_endpoints and not schema_endpoints:
        print("❌ No endpoints found in discovery")

    print(f"🔍 Discovery info: base_url={discovery.get('base_url', 'N/A')}")
    print(
        f"   Available: {len(available_endpoints)} endpoints, "
        f"Schema: {len(schema_endpoints)} endpoints"
    )


def main() -> None:
    """Main function demonstrating RESTAdapter configuration and discovery."""
    print("🔧 Configurable REST Adapter Examples")
    print("=" * 50)

    # Create adapters for different APIs
    adapters = {
        "JSONPlaceholder": create_jsonplaceholder_adapter(),
        "httpbin.org": create_httpbin_adapter(),
        "REST Countries": create_rest_countries_adapter(),
    }

    # Test each adapter
    for name, adapter in adapters.items():
        demonstrate_api_adapter(name, adapter)

    print("\n🏢 Router Integration with Multiple APIs")
    print("-" * 45)

    # Create router and register all adapters
    router = Router()
    for adapter_name, adapter in adapters.items():
        router[adapter_name] = adapter

    print(f"Router has {len(router.adapters)} adapters:")
    for adapter_name in router.adapters.keys():
        print(f"  - {adapter_name}")

    # Demonstrate queries through router
    print("\n📊 Sample Queries Through Router")
    print("-" * 35)

    try:
        # Query JSONPlaceholder users
        jsonplaceholder_adapter = router["jsonplaceholder"]
        if jsonplaceholder_adapter:
            users = jsonplaceholder_adapter.query("users")
            print(f"✅ JSONPlaceholder users: {len(users)} records")
    except Exception as e:
        print(f"❌ JSONPlaceholder users query failed: {e}")

    try:
        # Query httpbin JSON endpoint
        httpbin_adapter = router["httpbin"]
        if httpbin_adapter:
            httpbin_json = httpbin_adapter.query("json")
            print(f"✅ HTTPBin JSON endpoint: {len(httpbin_json)} records")
    except Exception as e:
        print(f"❌ HTTPBin JSON query failed: {e}")

    try:
        # Query REST Countries
        countries_adapter = router["rest_countries"]
        if countries_adapter:
            countries = countries_adapter.query(
                "name/United States"
            )  # Get info about USA
            print(f"✅ REST Countries (USA): {len(countries)} records")
    except Exception as e:
        print(f"❌ REST Countries query failed: {e}")

    print("\n💡 Configuration Examples")
    print("-" * 30)

    print("Example configurations for different APIs:")

    print("\n1. E-commerce API Configuration:")
    print(
        """
    ecommerce_config = {
        "headers": {"Authorization": "Bearer YOUR_TOKEN"},
        "endpoints": ["products", "orders", "customers"],
        "pagination_param": "limit",
        "pagination_limit": 20,
    }
    """
    )

    print("2. Social Media API Configuration:")
    print(
        """
    social_config = {
        "headers": {"X-API-Key": "YOUR_API_KEY"},
        "endpoints": ["posts", "users", "comments"],
        "pagination_param": "per_page",
        "pagination_limit": 10,
    }
    """
    )

    print("3. Financial API Configuration:")
    print(
        """
    finance_config = {
        "headers": {"Accept": "application/json"},
        "auth": ("username", "password"),
        "endpoints": ["accounts", "transactions"],
        "pagination_param": "count",
        "pagination_limit": 50,
    }
    """
    )

    print("\n✨ Configuration Complete!")
    print("The RESTAdapter is now fully configurable and can work with any REST API")
    print("by providing appropriate configuration parameters.")


if __name__ == "__main__":
    main()
