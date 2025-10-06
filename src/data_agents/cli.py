"""Command-line interface for data-agents."""

import argparse
import json
import sys
from typing import Union

import pandas as pd

from data_agents.adapters import TabularAdapter
from data_agents.core.router import Router


def create_router(name: str, config_file: Union[str, None] = None) -> Router:
    """Create a new router."""
    # Future: config could be used for adapter configuration
    if config_file:
        try:
            with open(config_file) as f:
                # Load config for future use in adapter configuration
                _config = json.load(f)  # noqa: F841
        except FileNotFoundError:
            print(f"Warning: Configuration file {config_file} not found")
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in configuration file {config_file}")

    return Router()


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Data Agents CLI - A prototype for general data agents"
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new router")
    create_parser.add_argument("name", help="Name for the router")
    create_parser.add_argument("--config", help="Path to JSON configuration file")

    # Demo command - demonstrates the Router/Adapter functionality
    demo_parser = subparsers.add_parser(
        "demo", help="Run a demonstration of Router/Adapter functionality"
    )
    demo_parser.add_argument(
        "--router-name", default="demo-router", help="Name for the demo router"
    )

    # Query command
    query_parser = subparsers.add_parser("query", help="Query data through a router")
    query_parser.add_argument("router_name", help="Name for the router")
    query_parser.add_argument("adapter_name", help="Name of the adapter to query")
    query_parser.add_argument("query", help="Query string to execute")
    query_parser.add_argument("--config", help="Path to JSON configuration file")

    # List adapters command
    list_parser = subparsers.add_parser(
        "list-adapters", help="List all adapters in a router"
    )
    list_parser.add_argument("router_name", help="Name for the router")
    list_parser.add_argument("--config", help="Path to JSON configuration file")

    # Process command (legacy)
    process_parser = subparsers.add_parser("process", help="Process data with a router")
    process_parser.add_argument("name", help="Name for the router")
    process_parser.add_argument("data", help="Data to process")
    process_parser.add_argument("--config", help="Path to JSON configuration file")

    # Info command
    info_parser = subparsers.add_parser("info", help="Get router information")
    info_parser.add_argument("name", help="Name for the router")
    info_parser.add_argument("--config", help="Path to JSON configuration file")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "create":
        router = create_router(args.name, args.config)
        print(f"Created router: {args.name}")
        # Future: Display configuration if loaded

    elif args.command == "demo":
        # Create a demo router with sample data
        router = Router()

        # Create sample datasets
        customers_data = pd.DataFrame(
            {
                "id": [1, 2, 3, 4, 5],
                "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
                "age": [25, 30, 35, 28, 42],
                "city": ["New York", "London", "Tokyo", "Paris", "Sydney"],
            }
        )

        orders_data = pd.DataFrame(
            {
                "order_id": [101, 102, 103, 104, 105],
                "customer_id": [1, 2, 1, 3, 2],
                "product": ["Laptop", "Phone", "Tablet", "Monitor", "Keyboard"],
                "amount": [1200, 800, 400, 300, 100],
            }
        )

        # Create adapters
        customers_adapter = TabularAdapter("customers", customers_data)
        orders_adapter = TabularAdapter("orders", orders_data)

        # Add adapters to router using bracket notation
        router["customers"] = customers_adapter
        router["orders"] = orders_adapter

        print(f"Demo router '{args.router_name}' created with sample data")
        print(f"Available adapters: {list(router.adapters.keys())}")

        # Show sample queries
        print("\n--- Sample Queries ---")

        print("\n1. Get all customers:")
        customers_adapter = router["customers"]  # type: ignore[assignment]
        if customers_adapter is not None:
            result = customers_adapter.query("*")
            print(result.to_string(index=False))

        print("\n2. Get all orders:")
        orders_adapter = router["orders"]  # type: ignore[assignment]
        if orders_adapter is not None:
            result = orders_adapter.query("*")
            print(result.to_string(index=False))

        print("\n3. Query customers over 30:")
        customers_adapter = router["customers"]  # type: ignore[assignment]
        if customers_adapter is not None:
            result = customers_adapter.query("age > 30")
            print(result.to_string(index=False))

        print("\n4. Get discovery information:")
        discoveries = router.discover_all()
        for adapter_name, discovery in discoveries.items():
            print(f"\n{adapter_name} discovery:")
            print(f"  Columns: {discovery.get('columns', [])}")
            print(f"  Shape: {discovery.get('shape', (0, 0))}")
            print(f"  Adapter Type: {discovery.get('adapter_type', 'unknown')}")

    elif args.command == "query":
        router = create_router(args.router_name, args.config)
        try:
            adapter = router[args.adapter_name]
            if adapter is None:
                print(f"Error: Adapter '{args.adapter_name}' not found")
                sys.exit(1)
            result = adapter.query(args.query)
            if not result.empty:
                print(result.to_string(index=False))
            else:
                print("Query returned no results")
        except Exception as e:
            print(f"Query failed: {e}")

    elif args.command == "list-adapters":
        router = create_router(args.router_name, args.config)
        if router.adapters:
            print("Available adapters:")
            for adapter_name, adapter in router.adapters.items():
                print(f"  - {adapter_name} ({adapter.__class__.__name__})")
        else:
            print("No adapters registered")

    elif args.command == "process":
        router = create_router(args.name, args.config)
        # Process command would need to be implemented based on specific requirements
        print("Process command not yet implemented")

    elif args.command == "info":
        router = create_router(args.name, args.config)
        info = router.to_dict()
        print(json.dumps(info, indent=2, default=str))


if __name__ == "__main__":
    main()
