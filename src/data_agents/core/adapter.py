"""Base adapter class for data agents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import pandas as pd


class Adapter(ABC):
    """Base adapter class for accessing different types of data sources.

    The Adapter class provides a standardized interface for accessing data
    from various sources like databases, APIs, files, etc. Users can extend
    this class to create custom adapters for their specific data sources.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the adapter.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}

    @abstractmethod
    def query(self, query: str, **kwargs: Any) -> pd.DataFrame:
        """Execute a query against the data source.

        Args:
            query: Query string or identifier
            **kwargs: Additional query parameters

        Returns:
            DataFrame containing the query results
        """
        pass

    @abstractmethod
    def discover(self) -> dict[str, Any]:
        """Discover capabilities and schema information for the data source.

        This method should return structured information about what can be queried,
        how to query it, and what the returned data looks like.

        Returns:
            Dictionary containing discovery information with the following structure:
            - adapter_type: Type of adapter (e.g., 'rest', 'tabular')
            - record_types: Dict mapping record type names to their descriptions
              - For TabularAdapter: table names and their schemas
              - For RESTAdapter: endpoint names and their schemas
            - query_parameters: Dict describing supported query parameters
            - data_format: Description of the returned data format
            - capabilities: Dict of supported operations and features
            - sample_data: Optional sample records for each record type
        """
        pass

    def to_dict(self: Adapter) -> dict[str, Any]:
        """Returns a dictionary representation of the adapter.

        Returns:
            Dictionary containing adapter information
        """
        return {
            "type": self.__class__.__name__,
            "config": self.config,
        }
