#!/usr/bin/env python3
"""
Example demonstrating the Router/Adapter architecture in data-agents.

This script shows how to:
1. Create a Router with multiple adapters
2. Query data from different sources
3. Work with tabular data through adapters
4. Extend the base Adapter class for custom data sources
"""

from typing import Any, Optional

import pandas as pd

from data_agents import Router
from data_agents.adapters import TabularAdapter
from data_agents.core import Adapter


class MockAPIAdapter(Adapter):
    """Example custom adapter that simulates an API data source."""

    def __init__(
        self, name: str, api_endpoint: str, config: Optional[dict[str, Any]] = None
    ):
        super().__init__(name, config)
        self.api_endpoint = api_endpoint
        # Simulate API data
        self._mock_data = pd.DataFrame(
            {
                "api_id": [1001, 1002, 1003],
                "service": ["auth", "billing", "analytics"],
                "status": ["active", "active", "maintenance"],
                "response_time_ms": [45, 120, 250],
            }
        )

    def query(self, query: str, **kwargs: Any) -> pd.DataFrame:
        """Simulate API queries."""
        if query == "*" or query == "all":
            return self._mock_data.copy()
        elif query == "active":
            return self._mock_data[self._mock_data["status"] == "active"].copy()
        elif query in self._mock_data.columns:
            return self._mock_data[[query]].copy()
        else:
            # Try pandas query
            try:
                return self._mock_data.query(query).copy()
            except Exception:
                return pd.DataFrame()

    def discover(self) -> dict[str, Any]:
        """Return API discovery information."""
        return {
            "adapter_type": "mock_api",
            "base_url": self.api_endpoint,
            "columns": list(self._mock_data.columns),
            "dtypes": self._mock_data.dtypes.to_dict(),
            "shape": self._mock_data.shape,
            "sample": self._mock_data.head(1).to_dict("records"),
            "capabilities": {
                "supports_query": True,
                "supports_filtering": True,
                "real_time": False,
            },
            "last_updated": "2025-10-03T10:00:00Z",
        }


def main() -> None:
    """Run the example demonstration."""
    print("=== Data Agents Router/Adapter Example ===\n")

    # Create a Router
    router = Router("example-router", {"environment": "demo"})
    print(f"Created router: {router.name}")

    # 1. Create tabular data sources
    print("\n1. Creating tabular data sources...")

    # Customer data
    # Create customer data with realistic business information
    customers_data = pd.DataFrame(
        {
            "customer_id": [1, 2, 3, 4, 5],
            "name": [
                "Alice Johnson",
                "Bob Smith",
                "Charlie Brown",
                "Diana Prince",
                "Eve Adams",
            ],
            "email": [
                "alice@example.com",
                "bob@example.com",
                "charlie@example.com",
                "diana@example.com",
                "eve@example.com",
            ],
            "signup_date": pd.to_datetime(
                ["2023-01-15", "2023-02-20", "2023-03-10", "2023-04-05", "2023-05-12"]
            ),
            "plan": ["premium", "basic", "premium", "basic", "enterprise"],
            "monthly_spend": [99.99, 29.99, 99.99, 29.99, 299.99],
        }
    )

    # Order data
    # Create order data with purchase history
    orders_data = pd.DataFrame(
        {
            "order_id": [101, 102, 103, 104, 105, 106],
            "customer_id": [1, 2, 1, 3, 2, 4],
            "product": [
                "Pro License",
                "Basic License",
                "Add-on Pack",
                "Pro License",
                "Support",
                "Basic License",
            ],
            "amount": [99.99, 29.99, 19.99, 99.99, 49.99, 29.99],
            "order_date": pd.to_datetime(
                [
                    "2023-06-01",
                    "2023-06-02",
                    "2023-06-03",
                    "2023-06-04",
                    "2023-06-05",
                    "2023-06-06",
                ]
            ),
        }
    )

    # 2. Create adapters
    print("2. Creating adapters...")

    customers_adapter = TabularAdapter("customers", customers_data)
    orders_adapter = TabularAdapter("orders", orders_data)
    api_adapter = MockAPIAdapter("services", "https://api.example.com/services")

    # 3. Register adapters with the router
    print("3. Registering adapters with router...")

    router.add_adapter(customers_adapter)
    router.add_adapter(orders_adapter)
    router.add_adapter(api_adapter)

    print(f"Registered adapters: {router.list_adapters()}")

    # 4. Query individual adapters
    print("\n4. Querying individual adapters...")

    print("\n--- All Customers ---")
    all_customers = router.query("customers", "*")
    print(all_customers.to_string(index=False))

    print("\n--- Premium Customers ---")
    premium_customers = router.query("customers", "plan == 'premium'")
    print(premium_customers[["name", "plan", "monthly_spend"]].to_string(index=False))

    print("\n--- Recent Orders (last 3) ---")
    all_orders = router.query("orders", "*")
    recent_orders = all_orders.tail(3)
    print(recent_orders.to_string(index=False))

    print("\n--- Active Services (from API) ---")
    active_services = router.query("services", "active")
    print(active_services.to_string(index=False))

    # 5. Query all adapters
    print("\n5. Querying all adapters...")

    all_results = router.query_all("*")
    for adapter_name, data in all_results.items():
        print(f"\n{adapter_name.upper()}: {len(data)} records")
        print(data.head(2).to_string(index=False))

    # 6. Get discovery information
    print("\n6. Discovery information...")

    discoveries = router.discover_all()
    for adapter_name, discovery in discoveries.items():
        print(f"\n{adapter_name.upper()} Discovery:")
        if "columns" in discovery:
            print(f"  Columns: {', '.join(discovery['columns'])}")
        if "shape" in discovery:
            print(f"  Shape: {discovery['shape']}")
        if "adapter_type" in discovery:
            print(f"  Type: {discovery['adapter_type']}")
        if "capabilities" in discovery:
            print(f"  Capabilities: {discovery['capabilities']}")

    # 7. Router information
    print("\n7. Router information...")

    info = router.get_info()
    print(f"Router Name: {info['name']}")
    print(f"Router Type: {info['type']}")
    print(f"Adapter Count: {info['adapter_count']}")

    print("\nAdapters:")
    for adapter_name, adapter_info in info["adapters"].items():
        print(f"  - {adapter_name}: {adapter_info['type']}")

    print("\n=== Example completed successfully! ===")


if __name__ == "__main__":
    main()
