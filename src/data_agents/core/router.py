"""Router implementation for managing data adapters."""

from __future__ import annotations

from typing import Any

import pandas as pd

from .adapter import Adapter


class Router:
    """Router for managing and querying a collection of Adapter instances.

    The Router acts as the primary interface for accessing data from multiple sources
    through registered Adapters. It provides methods to register adapters,
    execute queries across adapters, and retrieve metadata.
    """

    def __init__(self, name: str = "default", config: dict[str, Any] | None = None):
        """Initialize the router.

        Args:
            name: Name for this router instance
            config: Optional configuration dictionary
        """
        self.name = name
        self.config = config or {}
        self.adapters: dict[str, Adapter] = {}

    def register_adapter(self, adapter: Adapter) -> None:
        """Register an adapter with the router.

        Args:
            adapter: Adapter instance to register
        """
        self.adapters[adapter.name] = adapter

    def unregister_adapter(self, name: str) -> bool:
        """Unregister an adapter from the router.

        Args:
            name: Name of the adapter to unregister

        Returns:
            True if adapter was found and removed, False otherwise
        """
        if name in self.adapters:
            del self.adapters[name]
            return True
        return False

    def get_adapter(self, name: str) -> Adapter | None:
        """Get a specific adapter by name.

        Args:
            name: Name of the adapter to retrieve

        Returns:
            Adapter instance if found, None otherwise
        """
        return self.adapters.get(name)

    def list_adapters(self) -> list[str]:
        """Get a list of all registered adapter names.

        Returns:
            List of adapter names
        """
        return list(self.adapters.keys())

    def query(self, adapter_name: str, query: str, **kwargs: Any) -> pd.DataFrame:
        """Execute a query on a specific adapter.

        Args:
            adapter_name: Name of the adapter to query
            query: Query string to execute
            **kwargs: Additional query parameters

        Returns:
            DataFrame containing query results

        Raises:
            ValueError: If adapter is not found
        """
        adapter = self.get_adapter(adapter_name)
        if adapter is None:
            raise ValueError(f"Adapter '{adapter_name}' not found")

        return adapter.query(query, **kwargs)

    def query_all(self, query: str, **kwargs: Any) -> dict[str, pd.DataFrame]:
        """Execute a query on all registered adapters.

        Args:
            query: Query string to execute
            **kwargs: Additional query parameters

        Returns:
            Dictionary mapping adapter names to their query results
        """
        results = {}
        for name, adapter in self.adapters.items():
            try:
                results[name] = adapter.query(query, **kwargs)
            except Exception as e:
                # Log error and continue with other adapters
                print(f"Error querying adapter '{name}': {e}")
                results[name] = pd.DataFrame()

        return results

    def discover(self, adapter_name: str) -> dict[str, Any]:
        """Get discovery information for a specific adapter.

        Args:
            adapter_name: Name of the adapter

        Returns:
            Discovery information dictionary

        Raises:
            ValueError: If adapter is not found
        """
        adapter = self.get_adapter(adapter_name)
        if adapter is None:
            raise ValueError(f"Adapter '{adapter_name}' not found")

        return adapter.discover()

    def discover_all(self) -> dict[str, dict[str, Any]]:
        """Get discovery information for all registered adapters.

        Returns:
            Dictionary mapping adapter names to their discovery information
        """
        discoveries = {}
        for name, adapter in self.adapters.items():
            try:
                discoveries[name] = adapter.discover()
            except Exception as e:
                print(f"Error discovering adapter '{name}': {e}")
                discoveries[name] = {}

        return discoveries

    def add_adapter(self, adapter: Adapter) -> None:
        """Add an adapter to the router (alias for register_adapter).

        Args:
            adapter: Adapter instance to add
        """
        self.register_adapter(adapter)

    def process(self: Router, data: Any) -> Any:
        """Process input data and return results.

        Args:
            data: Input data to process

        Returns:
            Processed data
        """
        # Placeholder implementation for backward compatibility
        print(f"Router {self.name} processing data: {data}")
        return f"Processed: {data}"

    def get_info(self: Router) -> dict[str, Any]:
        """Get information about the router and its adapters.

        Returns:
            Dictionary containing router information
        """
        adapters_info = {
            name: adapter.get_info() for name, adapter in self.adapters.items()
        }
        return {
            "name": self.name,
            "type": "Router",
            "config": self.config,
            "adapter_count": len(self.adapters),
            "adapters": adapters_info,
        }
