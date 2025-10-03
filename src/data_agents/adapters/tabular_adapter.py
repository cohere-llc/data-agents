"""Tabular adapter implementation for data agents."""

from __future__ import annotations

from typing import Any

import pandas as pd

from ..core.adapter import Adapter


class TabularAdapter(Adapter):
    """Default adapter for tabular data sources.

    This adapter provides basic functionality for working with tabular data
    and serves as a reference implementation for custom adapters.
    """

    def __init__(
        self,
        name: str,
        data: pd.DataFrame | None = None,
        config: dict[str, Any] | None = None,
    ):
        """Initialize the tabular adapter.

        Args:
            name: The name/identifier for this adapter
            data: Optional DataFrame to use as the data source
            config: Optional configuration dictionary
        """
        super().__init__(name, config)
        self.data = data if data is not None else pd.DataFrame()

    def query(self: TabularAdapter, query: str, **kwargs: Any) -> pd.DataFrame:
        """Execute a query against the tabular data.

        Args:
            query: Query string (supports basic pandas operations)
            **kwargs: Additional query parameters

        Returns:
            DataFrame containing the query results
        """
        if query == "*" or query == "all":
            return self.data.copy()

        # Simple column selection
        if query in self.data.columns:
            return self.data[[query]].copy()

        # For more complex queries, users can extend this method
        try:
            # Try to use query as a pandas query string
            return self.data.query(query).copy()
        except Exception:
            # If query fails, return empty DataFrame
            return pd.DataFrame()

    def discover(self) -> dict[str, Any]:
        """Discover capabilities and schema information for the tabular data.

        Returns:
            Dictionary containing column names, types, basic stats, and capabilities
        """
        return {
            "adapter_type": "tabular",
            "columns": list(self.data.columns),
            "dtypes": self.data.dtypes.to_dict(),
            "shape": self.data.shape,
            "sample": self.data.head().to_dict() if not self.data.empty else {},
            "capabilities": {
                "supports_query": True,
                "supports_filtering": True,
                "supports_column_selection": True,
            }
        }

    def add_data(self, data: pd.DataFrame) -> None:
        """Add data to the adapter.

        Args:
            data: DataFrame to add/replace current data
        """
        self.data = data.copy()
