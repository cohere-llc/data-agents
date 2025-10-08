"""Tabular adapter implementation for data agents."""

from __future__ import annotations

from typing import Any

import pandas as pd

from ..core.adapter import Adapter


class TabularAdapter(Adapter):
    """Default adapter for tabular data sources.

    This adapter provides basic functionality for working with tabular data
    and serves as a reference implementation for custom adapters. It supports
    multiple named tables for more complex data scenarios.
    """

    def __init__(
        self,
        data: pd.DataFrame | dict[str, pd.DataFrame] | None = None,
        config: dict[str, Any] | None = None,
    ):
        """Initialize the tabular adapter.

        Args:
            data: Optional DataFrame or dict of named DataFrames to use as data sources.
                  If a single DataFrame is provided, it will be stored as "data".
                  If a dict is provided, each key-value pair represents a named table.
            config: Optional configuration dictionary
        """
        super().__init__(config)

        # Initialize the tables dictionary
        self.tables: dict[str, pd.DataFrame] = {}

        if data is not None:
            if isinstance(data, pd.DataFrame):
                # Single DataFrame - store as "data" table
                self.tables["data"] = data.copy()
            elif isinstance(data, dict):
                # Multiple named DataFrames
                for name, df in data.items():
                    if isinstance(df, pd.DataFrame):
                        self.tables[name] = df.copy()
                    else:
                        raise ValueError(
                            f"All values in data dict must be DataFrames, "
                            f"got {type(df)} for '{name}'"
                        )
            else:
                raise ValueError(
                    f"data must be a DataFrame or dict of DataFrames, got {type(data)}"
                )

    @property
    def data(self) -> pd.DataFrame:
        """Backward compatibility property for single table access.

        Returns the first table if available, or empty DataFrame if no tables exist.
        """
        if not self.tables:
            return pd.DataFrame()
        # Return the first table for backward compatibility
        return next(iter(self.tables.values()))

    def query(self: TabularAdapter, query: str, **kwargs: Any) -> pd.DataFrame:
        """Execute a query against the tabular data.

        Args:
            query: Query string. Can be:
                   - Table name to return entire table
                   - "table_name.column_name" to select a column from a specific table
                   - "*" or "all" to return the first/default table
                   - Pandas query string for the default table
            **kwargs: Additional query parameters including:
                     - table: Specify which table to query
                       (overrides table from query string)

        Returns:
            DataFrame containing the query results
        """
        # Handle table specification from kwargs
        specified_table = kwargs.get("table")

        # Parse query for table.column syntax
        if "." in query and not specified_table:
            parts = query.split(".", 1)
            if len(parts) == 2 and parts[0] in self.tables:
                specified_table = parts[0]
                query = parts[1]

        # Determine which table to query
        if specified_table:
            if specified_table not in self.tables:
                raise ValueError(
                    f"Table '{specified_table}' not found. "
                    f"Available tables: {list(self.tables.keys())}"
                )
            target_data = self.tables[specified_table]
        elif query in self.tables:
            # Query is a table name - return the entire table
            return self.tables[query].copy()
        else:
            # Use the default table (backward compatibility)
            target_data = self.data

        # Handle wildcard queries
        if query == "*" or query == "all":
            return target_data.copy()

        # Simple column selection
        if query in target_data.columns:
            return target_data[[query]].copy()

        # For more complex queries, users can extend this method
        try:
            # Try to use query as a pandas query string
            return target_data.query(query).copy()
        except Exception:
            # If query fails, return empty DataFrame
            return pd.DataFrame()

    def discover(self) -> dict[str, Any]:
        """Discover capabilities and schema information for the tabular data.

        Returns:
            Dictionary containing standardized discovery information including
            record types (table schemas), query parameters, and data format.
        """
        record_types = {}
        sample_data = {}

        # Process each table
        for table_name, table_df in self.tables.items():
            if not table_df.empty:
                record_types[table_name] = {
                    "description": f"Data table: {table_name}",
                    "columns": list(table_df.columns),
                    "dtypes": table_df.dtypes.to_dict(),
                    "shape": table_df.shape,
                    "row_count": len(table_df),
                }
                sample_data[table_name] = table_df.head(3).to_dict("records")

        # Generate examples for query parameters
        all_columns = []
        table_names = list(self.tables.keys())
        for df in self.tables.values():
            all_columns.extend(df.columns.tolist())
        all_columns = list(set(all_columns))  # Remove duplicates

        return {
            "adapter_type": "tabular",
            "record_types": record_types,
            "query_parameters": {
                "table_name": {
                    "description": "Name of the table to query",
                    "type": "string",
                    "examples": table_names[:3],
                    "required": False,
                    "note": "If not specified, uses the first/default table",
                },
                "table_column_syntax": {
                    "description": (
                        "Query specific table and column using 'table.column' syntax"
                    ),
                    "type": "string",
                    "examples": [
                        f"{table}.{col}"
                        for table, df in list(self.tables.items())[:2]
                        for col in df.columns.tolist()[:2]
                    ]
                    if self.tables
                    else [],
                    "required": False,
                },
                "column_selection": {
                    "description": "Select specific columns by name",
                    "type": "string",
                    "examples": all_columns[:5],
                    "required": False,
                },
                "filter_query": {
                    "description": "Pandas query string for filtering rows",
                    "type": "string",
                    "examples": [
                        "column_name > 10",
                        "column_name == 'value'",
                        "column_name.isin(['a', 'b'])",
                    ]
                    if all_columns
                    else [],
                    "required": False,
                },
                "wildcard": {
                    "description": (
                        "Use '*' or 'all' to return all data from default table"
                    ),
                    "type": "string",
                    "examples": ["*", "all"],
                    "required": False,
                },
                "table_kwarg": {
                    "description": "Specify table using 'table' keyword argument",
                    "type": "string",
                    "examples": table_names[:3],
                    "required": False,
                    "usage": "query('column_name', table='table_name')",
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
                "supports_multiple_tables": True,
                "supports_table_selection": True,
                "supports_aggregation": False,
                "supports_joins": False,
            },
            "sample_data": sample_data,
        }

    def add_data(self, data: pd.DataFrame, table_name: str = "data") -> None:
        """Add data to the adapter.

        Args:
            data: DataFrame to add/replace
            table_name: Name for the table (default: "data")
        """
        self.tables[table_name] = data.copy()

    def add_tables(self, tables: dict[str, pd.DataFrame]) -> None:
        """Add multiple tables to the adapter.

        Args:
            tables: Dictionary mapping table names to DataFrames
        """
        for name, df in tables.items():
            if isinstance(df, pd.DataFrame):
                self.tables[name] = df.copy()
            else:
                raise ValueError(
                    f"All values must be DataFrames, got {type(df)} for '{name}'"
                )

    def get_table(self, table_name: str) -> pd.DataFrame:
        """Get a specific table by name.

        Args:
            table_name: Name of the table to retrieve

        Returns:
            DataFrame for the specified table

        Raises:
            ValueError: If table name doesn't exist
        """
        if table_name not in self.tables:
            raise ValueError(
                f"Table '{table_name}' not found. "
                f"Available tables: {list(self.tables.keys())}"
            )
        return self.tables[table_name].copy()

    def list_tables(self) -> list[str]:
        """List all available table names.

        Returns:
            List of table names
        """
        return list(self.tables.keys())

    def remove_table(self, table_name: str) -> None:
        """Remove a table from the adapter.

        Args:
            table_name: Name of the table to remove

        Raises:
            ValueError: If table name doesn't exist
        """
        if table_name not in self.tables:
            raise ValueError(
                f"Table '{table_name}' not found. "
                f"Available tables: {list(self.tables.keys())}"
            )
        del self.tables[table_name]
