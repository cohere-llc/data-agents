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
        data: pd.DataFrame | None = None,
        config: dict[str, Any] | None = None,
    ):
        """Initialize the tabular adapter.

        Args:
            data: Optional DataFrame to use as the data source
            config: Optional configuration dictionary
        """
        super().__init__(config)
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
            Dictionary containing standardized discovery information including
            record types (table schema), query parameters, and data format.
        """
        # For TabularAdapter, we have one "table" which is the loaded DataFrame
        table_name = "data"  # Default table name

        record_types = {}
        sample_data = {}

        if not self.data.empty:
            record_types[table_name] = {
                "description": "Main data table",
                "columns": list(self.data.columns),
                "dtypes": self.data.dtypes.to_dict(),
                "shape": self.data.shape,
                "row_count": len(self.data),
            }
            sample_data[table_name] = self.data.head(3).to_dict("records")

        return {
            "adapter_type": "tabular",
            "record_types": record_types,
            "query_parameters": {
                "column_selection": {
                    "description": "Select specific columns by name",
                    "type": "string",
                    "examples": list(self.data.columns)[:5]
                    if not self.data.empty
                    else [],
                },
                "filter_query": {
                    "description": "Pandas query string for filtering rows",
                    "type": "string",
                    "examples": [
                        "column_name > 10",
                        "column_name == 'value'",
                        "column_name.isin(['a', 'b'])",
                    ]
                    if not self.data.empty
                    else [],
                },
                "wildcard": {
                    "description": "Use '*' or 'all' to return all data",
                    "type": "string",
                    "examples": ["*", "all"],
                },
            },
            "data_format": {
                "type": "pandas.DataFrame",
                "description": (
                    "Returns data as a pandas DataFrame with columns and rows"
                ),
                "structure": "Tabular data with named columns and indexed rows",
            },
            "capabilities": {
                "supports_query": True,
                "supports_filtering": True,
                "supports_column_selection": True,
                "supports_aggregation": False,
                "supports_joins": False,
            },
            "sample_data": sample_data,
        }

    def add_data(self, data: pd.DataFrame) -> None:
        """Add data to the adapter.

        Args:
            data: DataFrame to add/replace current data
        """
        self.data = data.copy()
