"""Base adapter class for data agents."""

from abc import ABC, abstractmethod
from typing import Any, Optional

import pandas as pd


class Adapter(ABC):
    """Base adapter class for accessing different types of data sources.

    The Adapter class provides a standardized interface for accessing data
    from various sources like databases, APIs, files, etc. Users can extend
    this class to create custom adapters for their specific data sources.
    """

    def __init__(self, name: str, config: Optional[dict[str, Any]] = None):
        """Initialize the adapter.

        Args:
            name: The name/identifier for this adapter
            config: Optional configuration dictionary
        """
        self.name = name
        self.config = config or {}

    @abstractmethod
    def query(self, query: str, **kwargs) -> pd.DataFrame:
        """Execute a query against the data source.

        Args:
            query: Query string or identifier
            **kwargs: Additional query parameters

        Returns:
            DataFrame containing the query results
        """
        pass

    @abstractmethod
    def get_schema(self) -> dict[str, Any]:
        """Get schema information for the data source.

        Returns:
            Dictionary containing schema/metadata information
        """
        pass

    def get_info(self) -> dict[str, Any]:
        """Get information about this adapter.

        Returns:
            Dictionary containing adapter information
        """
        return {
            "name": self.name,
            "type": self.__class__.__name__,
            "config": self.config,
        }
