"""REST Adapter for OpenAPI Specifications."""

from typing import Any, Hashable, Optional
from ..core.adapter import Adapter

from openapi_core import OpenAPI

import pandas as pd

class OpenAPIAdapter(Adapter):
    """Adapter for RESTful APIs defined by OpenAPI specifications."""

    def __init__(self, openapi_spec: dict[Hashable, Any], config: Optional[dict[str, Any]] = None):
        """Initialize the OpenAPI adapter.

        Args:
            openapi_spec: The OpenAPI specification as a dictionary.
            config: Optional configuration dictionary.
        """
        if config is None:
            raise ValueError("Config dictionary is required for OpenAPIAdapter")
        super().__init__(config)
        self._raw_spec = openapi_spec
        self.openapi_spec = OpenAPI.from_dict(openapi_spec)
        if "base_url" not in self.config:
            raise ValueError("Config must include 'base_url' for OpenAPIAdapter")
        if not isinstance(self.config["base_url"], str):
            raise ValueError("'base_url' in config must be a string")
        self.base_url = self.config.get("base_url", "")


    def query(self, query: str, **kwargs: Any) -> pd.DataFrame:
        """Execute a query against the specified API endpoint.

        Args:
            endpoint: The API endpoint to query.
            **kwargs: Additional query parameters.

        Returns:
            Dictionary containing the query results.
        """
        # Implementation of the query method
        return pd.DataFrame()

    def discover(self) -> dict[str, Any]:
        """Discover capabilities and schema information from the OpenAPI spec.

        Returns:
            Dictionary containing discovery information.
        """
        return self._raw_spec