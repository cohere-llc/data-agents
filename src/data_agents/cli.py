"""Command-line interface for data-agents."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from data_agents import __version__
from data_agents.adapters import (
    GBIFOccurrenceAdapter,
    NasaPowerAdapter,
    RESTAdapter,
    TabularAdapter,
)
from data_agents.core.adapter import Adapter
from data_agents.core.router import Router


def parse_nasa_query(query_string: str) -> tuple[str, dict[str, Any]]:
    """Parse NASA POWER query string into parameter name and kwargs.

    Args:
        query_string: Query string in format "PARAMETER_NAME key=value key2=value2"

    Returns:
        Tuple of (parameter_name, kwargs_dict)

    Example:
        parse_nasa_query("T2M latitude=40.7 longitude=-74.0 temporal=daily")
        Returns: ("T2M", {"latitude": 40.7, "longitude": -74.0, "temporal": "daily"})
    """
    parts = query_string.split()
    if not parts:
        raise ValueError("Empty query string")

    parameter_name = parts[0]
    kwargs: dict[str, Any] = {}

    for part in parts[1:]:
        if "=" not in part:
            continue
        key, value = part.split("=", 1)

        # Try to convert numeric values
        try:
            float_val = float(value)
            if float_val.is_integer():
                kwargs[key] = int(float_val)
            else:
                kwargs[key] = float_val
        except ValueError:
            # Keep as string if not numeric
            kwargs[key] = value

    return parameter_name, kwargs


def execute_router_query(router: Router, query_string: str) -> dict[str, pd.DataFrame]:
    """Execute a query on all adapters in a router, handling different adapter types.

    Args:
        router: The router containing adapters to query
        query_string: The query string

    Returns:
        Dictionary mapping adapter names to their query results
    """
    results = {}
    for name, adapter in router.adapters.items():
        try:
            results[name] = execute_adapter_query(adapter, query_string)
        except Exception as e:
            # Log error and continue with other adapters
            print(f"Error querying adapter '{name}': {e}")
            results[name] = pd.DataFrame()

    return results


def execute_adapter_query(adapter: Adapter, query_string: str) -> pd.DataFrame:
    """Execute a query on an adapter, handling different adapter types.

    Args:
        adapter: The adapter to query
        query_string: The query string

    Returns:
        DataFrame with query results
    """
    if isinstance(adapter, NasaPowerAdapter):
        # Parse NASA POWER query format: "PARAMETER_NAME key=value key2=value2"
        parameter_name, kwargs = parse_nasa_query(query_string)
        return adapter.query(parameter_name, **kwargs)
    else:
        # For other adapters, use the query string directly
        return adapter.query(query_string)


def load_config_file(config_path: str) -> dict[str, Any]:
    """Load configuration from JSON or YAML file.

    Args:
        config_path: Path to the configuration file

    Returns:
        Dictionary containing the configuration

    Raises:
        FileNotFoundError: If the config file doesn't exist
        ValueError: If the config file format is invalid
    """
    config_file = Path(config_path)

    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file {config_path} not found")

    try:
        with open(config_file) as f:
            if config_file.suffix.lower() in [".yaml", ".yml"]:
                try:
                    import yaml
                except ImportError:
                    raise ValueError(
                        f"YAML support not available. Please install PyYAML to read "
                        f"{config_path}. Run: pip install PyYAML"
                    ) from None

                try:
                    result: dict[str, Any] = yaml.safe_load(f)
                    return result
                except yaml.YAMLError as e:
                    raise ValueError(
                        f"Invalid YAML format in configuration file {config_path}: {e}"
                    ) from None
            else:
                try:
                    result = json.load(f)
                    return result
                except json.JSONDecodeError as e:
                    raise ValueError(
                        f"Invalid JSON format in configuration file {config_path}: {e}"
                    ) from None
    except ValueError:
        # Re-raise ValueError exceptions (our custom messages)
        raise
    except Exception as e:
        # Handle any other unexpected exceptions
        raise ValueError(
            f"Failed to read configuration file {config_path}: {e}"
        ) from None


def create_adapter_from_config(
    adapter_config: dict[str, Any],
) -> Optional[Adapter]:
    """Create an adapter from configuration.

    Args:
        adapter_config: Configuration dictionary for the adapter

    Returns:
        Adapter instance or None if creation failed
    """
    adapter_type = adapter_config.get("type")

    if adapter_type == "rest":
        base_url = adapter_config.get("base_url")

        if not base_url:
            print("Error: REST adapter missing required 'base_url'")
            return None

        try:
            return RESTAdapter(base_url, adapter_config)
        except Exception as e:
            print(f"Error: Failed to create REST adapter: {e}")
            return None

    elif adapter_type == "tabular":
        csv_file = adapter_config.get("csv_file")

        if not csv_file:
            print("Error: Tabular adapter missing required 'csv_file'")
            return None

        try:
            csv_path = Path(csv_file)
            if not csv_path.exists():
                print(f"Error: CSV file {csv_file} not found")
                return None

            data = pd.read_csv(csv_file)
            return TabularAdapter({"data": data})
        except Exception as e:
            print(f"Error: Failed to create tabular adapter: {e}")
            return None

    elif adapter_type == "nasa_power":
        try:
            return NasaPowerAdapter()
        except Exception as e:
            print(f"Error: Failed to create NASA POWER adapter: {e}")
            return None

    elif adapter_type == "gbif_occurrence":
        try:
            return GBIFOccurrenceAdapter(adapter_config)
        except Exception as e:
            print(f"Error: Failed to create GBIF Occurrence adapter: {e}")
            return None
    else:
        print(
            f"Error: Unknown adapter type '{adapter_type}'. "
            f"Supported types: rest, tabular, nasa_power, gbif_occurrence"
        )
        return None


def create_router_from_config(config_file: str) -> Router:
    """Create a router with adapters from configuration.

    Args:
        config_file: Path to router configuration file

    Returns:
        Router instance with configured adapters
    """
    router = Router()

    try:
        config = load_config_file(config_file)

        # Load adapters from configuration
        adapters_config = config.get("adapters", {})
        for adapter_name, adapter_config in adapters_config.items():
            adapter = create_adapter_from_config(adapter_config)
            if adapter:
                router[adapter_name] = adapter

    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    return router


def create_single_adapter_from_config(
    config_file: str,
) -> Optional[Adapter]:
    """Create a single adapter from configuration.

    Args:
        config_file: Path to adapter configuration file

    Returns:
        Adapter instance or None if creation failed
    """
    try:
        config = load_config_file(config_file)
        return create_adapter_from_config(config)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        return None


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Data Agents CLI - A prototype for general data agents",
        prog="data-agents",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Demo command - demonstrates the Router/Adapter functionality
    subparsers.add_parser(
        "demo", help="Run a demonstration of the Router/Adapter functionality"
    )

    # Info command - supports both router and adapter configs
    info_parser = subparsers.add_parser(
        "info", help="Get router or adapter information"
    )
    info_group = info_parser.add_mutually_exclusive_group(required=True)
    info_group.add_argument("--router-config", help="Path to router configuration file")
    info_group.add_argument(
        "--adapter-config", help="Path to adapter configuration file"
    )

    # List adapters command
    list_parser = subparsers.add_parser(
        "list-adapters", help="List all adapters in a router"
    )
    list_parser.add_argument(
        "--router-config", required=True, help="Path to router configuration file"
    )

    # Discover command - supports both router and adapter configs
    discover_parser = subparsers.add_parser(
        "discover", help="Discover queryable parameters with type information"
    )
    discover_group = discover_parser.add_mutually_exclusive_group(required=True)
    discover_group.add_argument(
        "--router-config", help="Path to router configuration file"
    )
    discover_group.add_argument(
        "--adapter-config", help="Path to adapter configuration file"
    )

    # Query command - supports both router and adapter configs
    query_parser = subparsers.add_parser(
        "query", help="Query data through router or adapter"
    )
    query_parser.add_argument("query_string", help="Query string to execute")
    query_group = query_parser.add_mutually_exclusive_group(required=True)
    query_group.add_argument(
        "--router-config", help="Path to router configuration file"
    )
    query_group.add_argument(
        "--adapter-config", help="Path to adapter configuration file"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "demo":
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
        customers_adapter = TabularAdapter({"customers": customers_data})
        orders_adapter = TabularAdapter({"orders": orders_data})

        # Add adapters to router using bracket notation
        router["customers"] = customers_adapter
        router["orders"] = orders_adapter

        print("Demo router created with sample data")
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

    elif args.command == "info":
        if args.router_config:
            # Get router information
            router = create_router_from_config(args.router_config)
            info = router.to_dict()
            print(json.dumps(info, indent=2, default=str))
        elif args.adapter_config:
            # Get adapter information
            adapter = create_single_adapter_from_config(args.adapter_config)
            if adapter:
                info = adapter.to_dict()
                print(json.dumps(info, indent=2, default=str))
            else:
                sys.exit(1)

    elif args.command == "list-adapters":
        router = create_router_from_config(args.router_config)
        if router.adapters:
            print("Available adapters:")
            for adapter_name, adapter in router.adapters.items():
                print(f"  - {adapter_name} ({adapter.__class__.__name__})")
        else:
            print("No adapters registered")

    elif args.command == "discover":
        if args.router_config:
            # Discover all adapters in router
            router = create_router_from_config(args.router_config)
            discoveries = router.discover_all()
            for adapter_name, discovery in discoveries.items():
                print(f"\n{adapter_name}:")
                print(json.dumps(discovery, indent=2, default=str))
        elif args.adapter_config:
            # Discover single adapter
            adapter = create_single_adapter_from_config(args.adapter_config)
            if adapter:
                discovery = adapter.discover()
                print(json.dumps(discovery, indent=2, default=str))
            else:
                sys.exit(1)

    elif args.command == "query":
        if args.router_config:
            # Query all adapters in router
            router = create_router_from_config(args.router_config)
            results = execute_router_query(router, args.query_string)
            for adapter_name, result in results.items():
                print(f"\n--- Results from {adapter_name} ---")
                if not result.empty:
                    print(result.to_string(index=False))
                else:
                    print("Query returned no results")
        elif args.adapter_config:
            # Query single adapter
            adapter = create_single_adapter_from_config(args.adapter_config)
            if adapter:
                try:
                    result = execute_adapter_query(adapter, args.query_string)
                    if not result.empty:
                        print(result.to_string(index=False))
                    else:
                        print("Query returned no results")
                except Exception as e:
                    print(f"Query failed: {e}")
                    sys.exit(1)
            else:
                sys.exit(1)


if __name__ == "__main__":
    main()
