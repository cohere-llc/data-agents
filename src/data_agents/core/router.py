"""Router module for managing data adapters."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pandas as pd

from data_agents.core.adapter import Adapter


class Router:
    """Router for managing and querying a collection of Adapter instances.

    The Router acts as the primary interface for accessing data from multiple sources
    through registered Adapters. It provides methods to register adapters,
    execute queries across adapters, and retrieve metadata.
    """

    def __init__(self, adapters: dict[str, Adapter] | None = None):
        """Initialize the router.

        Args:
            adapters: Optional dictionary of adapter instances to register
        """
        self.adapters: dict[str, Adapter] = adapters or {}

    def __setitem__(self, key: str, adapter: Adapter) -> None:
        """Register an adapter with the router.

        Args:
            key: Name/identifier for the adapter
            adapter: Adapter instance to register
        """
        self.adapters[key] = adapter

    def __delitem__(self, key: str) -> bool:
        """Unregister an adapter from the router.

        Args:
            key: Name of the adapter to unregister

        Returns:
            True if adapter was found and removed, False otherwise
        """
        if key in self.adapters:
            del self.adapters[key]
            return True
        return False

    def __getitem__(self, key: str) -> Adapter | None:
        """Get an adapter by name.

        Args:
            key: Adapter name

        Returns:
            Adapter instance if found, None otherwise
        """
        return self.adapters.get(key)

    def __len__(self) -> int:
        """Return the number of registered adapters."""
        return len(self.adapters)

    def __iter__(self) -> Iterator[Adapter]:
        """Iterate over registered adapters."""
        return iter(self.adapters.values())

    def __contains__(self, key: str) -> bool:
        """Check if an adapter with the given name is registered.

        Args:
            key: Name of the adapter to check

        Returns:
            True if adapter is registered, False otherwise
        """
        return key in self.adapters

    def __repr__(self) -> str:
        return f"<Router adapters={list(self.adapters.keys())}>"

    def __str__(self) -> str:
        return f"Router with {len(self.adapters)} adapters"

    def __hash__(self) -> int:
        return hash(
            frozenset((key, hash(adapter)) for key, adapter in self.adapters.items())
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Router):
            return NotImplemented
        return hash(self) == hash(other)

    def __copy__(self) -> Router:
        return Router(self.adapters.copy())

    def __deepcopy__(self, memo: dict[int, Any] | None = None) -> Router:
        from copy import deepcopy

        memo = memo or {}
        return Router(deepcopy(self.adapters, memo))

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

    def to_dict(self: Router) -> dict[str, Any]:
        """Returns information about the router and its adapters.

        Returns:
            Dictionary containing router information
        """
        adapters_info = {
            name: adapter.to_dict() for name, adapter in self.adapters.items()
        }
        return {
            "type": "Router",
            "adapter_count": len(self.adapters),
            "adapters": adapters_info,
        }
