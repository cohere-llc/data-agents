"""REST adapter implementation for data agents."""

from __future__ import annotations

from typing import Any
from urllib.parse import urljoin

import pandas as pd
import requests
from openapi3 import OpenAPI  # type: ignore[import-untyped]

from ..core.adapter import Adapter


class RESTAdapter(Adapter):
    """REST API adapter for accessing data from REST endpoints.

    This adapter provides functionality for querying REST APIs and converting
    responses to pandas DataFrames. It's designed to work with JSON APIs
    and includes support for authentication, custom headers, and query parameters.
    """

    def __init__(
        self,
        base_url: str,
        config: dict[str, Any] | None = None,
    ):
        """Initialize the REST adapter.

        Args:
            base_url: Base URL for the REST API
            config: Optional configuration dictionary with keys:
                - headers: Dict of HTTP headers to include with requests
                - auth: Authentication tuple (username, password) for basic auth
                - timeout: Request timeout in seconds (default: 30)
                - verify: Whether to verify SSL certificates (default: True)
                - endpoints: List of endpoints to discover (used for both availability
                  checking and schema discovery)
                - pagination_param: Parameter name for pagination
                  (e.g., '_limit', 'limit')
                - pagination_limit: Default limit for pagination (default: 10)
                - openapi_data: OpenAPI specification data for schema discovery
        """
        super().__init__(config)
        self.base_url = base_url.rstrip("/")

        # Extract configuration
        self.headers = self.config.get("headers", {})
        self.auth = self.config.get("auth")
        self.timeout = self.config.get("timeout", 30)
        self.verify = self.config.get("verify", True)

        # Schema and endpoint discovery configuration
        self.endpoints = self.config.get("endpoints", [])
        self.pagination_param = self.config.get("pagination_param", "limit")
        self.pagination_limit = self.config.get("pagination_limit", 10)

        self.openapi_data = self.config.get("openapi_data")
        self.openapi_specs = []
        if self.openapi_data:
            if isinstance(self.openapi_data, str):
                self.openapi_data = [self.openapi_data]
            if not isinstance(self.openapi_data, list):
                data_type = type(self.openapi_data)
                raise ValueError(
                    f"Invalid OpenAPI data format: expected list, got {data_type}"
                )

            # Load OpenAPI specs from URLs or data
            for openapi_source in self.openapi_data:
                if isinstance(openapi_source, str) and (
                    openapi_source.startswith("http://")
                    or openapi_source.startswith("https://")
                ):
                    # Fetch OpenAPI spec from URL
                    try:
                        response = requests.get(
                            openapi_source, timeout=self.timeout, verify=self.verify
                        )
                        response.raise_for_status()
                        spec_json = response.json()
                        # Try with validation disabled for potentially malformed specs
                        try:
                            spec = OpenAPI(spec_json, validate=True)
                        except Exception:
                            # Fall back to no validation if spec has issues
                            spec = OpenAPI(spec_json, validate=False)
                        self.openapi_specs.append(spec)
                    except Exception as e:
                        print("Warning: Failed to load OpenAPI spec")
                        print(f"Source: {openapi_source}")
                        print(f"Error: {e}")
                        # Store basic info for fallback
                        try:
                            response = requests.get(
                                openapi_source, timeout=self.timeout, verify=self.verify
                            )
                            response.raise_for_status()
                            spec_json = response.json()
                            # Store as raw JSON for basic path extraction
                            self.openapi_specs.append(
                                {"_raw_spec": spec_json, "_source_url": openapi_source}
                            )
                        except Exception:
                            pass
                else:
                    # Assume it's OpenAPI spec content
                    try:
                        import json

                        if isinstance(openapi_source, str):
                            spec_json = json.loads(openapi_source)
                        else:
                            spec_json = openapi_source
                        try:
                            spec = OpenAPI(spec_json, validate=True)
                        except Exception:
                            spec = OpenAPI(spec_json, validate=False)
                        self.openapi_specs.append(spec)
                    except Exception as e:
                        print(f"Warning: Failed to parse OpenAPI spec: {e}")

            # Extract endpoints from OpenAPI specs if not explicitly provided
            if not self.endpoints and self.openapi_specs:
                self.endpoints = []
                for spec in self.openapi_specs:
                    if isinstance(spec, dict) and "_raw_spec" in spec:
                        # Handle raw spec fallback
                        raw_spec = spec["_raw_spec"]
                        if "paths" in raw_spec:
                            for path in raw_spec["paths"].keys():
                                self.endpoints.append(path.lstrip("/"))
                    elif hasattr(spec, "paths") and spec.paths:
                        # Handle proper OpenAPI object
                        for path in spec.paths:
                            self.endpoints.append(path.lstrip("/"))
                self.endpoints = list(set(self.endpoints))  # Deduplicate

        # Set default headers
        if "Accept" not in self.headers:
            self.headers["Accept"] = "application/json"

    def query(self: RESTAdapter, query: str, **kwargs: Any) -> pd.DataFrame:
        """Execute a query against the REST API.

        Args:
            query: Endpoint path (e.g., 'users', 'posts', 'posts/1/comments')
            **kwargs: Additional query parameters including:
                - params: Dict of URL query parameters
                - method: HTTP method (default: 'GET')
                - data: Request body data for POST/PUT requests
                - custom_headers: Additional headers for this request

        Returns:
            DataFrame containing the API response data

        Raises:
            requests.RequestException: If the HTTP request fails
            ValueError: If the response cannot be converted to DataFrame
        """
        # Build the full URL
        endpoint = query.lstrip("/")
        url = urljoin(self.base_url + "/", endpoint)

        # Prepare request parameters
        method = kwargs.get("method", "GET").upper()
        params = kwargs.get("params", {})
        data = kwargs.get("data")
        custom_headers = kwargs.get("custom_headers", {})

        # Combine headers
        request_headers = {**self.headers, **custom_headers}

        try:
            # Make the HTTP request
            response = requests.request(
                method=method,
                url=url,
                params=params,
                json=data if method in ["POST", "PUT", "PATCH"] else None,
                headers=request_headers,
                auth=self.auth,
                timeout=self.timeout,
                verify=self.verify,
            )

            # Raise an exception for bad status codes
            response.raise_for_status()

            # Parse JSON response
            json_data = response.json()

            # Convert to DataFrame
            if isinstance(json_data, list):
                # List of objects - convert directly
                return pd.DataFrame(json_data)
            elif isinstance(json_data, dict):
                # Single object - wrap in list
                return pd.DataFrame([json_data])
            else:
                # Primitive value - create simple DataFrame
                return pd.DataFrame({"value": [json_data]})

        except requests.RequestException as e:
            raise requests.RequestException(f"HTTP request failed: {e}") from e
        except (ValueError, KeyError) as e:
            raise ValueError(f"Failed to parse response as JSON: {e}") from e

    def discover(self: RESTAdapter) -> dict[str, Any]:
        """Discover API capabilities including available endpoints and schema.

        This method performs comprehensive API discovery by:
        1. Testing endpoint availability
        2. Gathering schema information from the same endpoints
        3. Combining both into a unified discovery result

        Returns:
            Dictionary containing:
            - base_url: The API base URL
            - available_endpoints: List of endpoints that respond successfully
            - endpoints: Schema information for each endpoint including columns,
              dtypes, and samples
            - sample_data: Sample records from each endpoint
        """
        discovery_info: dict[str, Any] = {
            "base_url": self.base_url,
            "available_endpoints": [],
            "endpoints": {},
            "sample_data": {},
        }

        # Use configured endpoints for both availability and schema discovery
        if not self.endpoints:
            return discovery_info

        for endpoint in self.endpoints:
            # 1. Test endpoint availability
            try:
                response = requests.get(
                    urljoin(self.base_url + "/", endpoint),
                    headers=self.headers,
                    auth=self.auth,
                    timeout=self.timeout,
                    verify=self.verify,
                )
                if response.status_code == 200:
                    discovery_info["available_endpoints"].append(endpoint)

                    # 2. Gather schema information for available endpoints
                    try:
                        # Try to get first few records with pagination if configured
                        params = {}
                        if self.pagination_param and self.pagination_limit:
                            params[self.pagination_param] = self.pagination_limit

                        sample_df = self.query(endpoint, params=params)
                        if not sample_df.empty:
                            discovery_info["endpoints"][endpoint] = {
                                "columns": list(sample_df.columns),
                                "dtypes": sample_df.dtypes.to_dict(),
                                "sample_count": len(sample_df),
                            }
                            discovery_info["sample_data"][endpoint] = sample_df.head(
                                1
                            ).to_dict("records")
                    except Exception:
                        # Endpoint is available but schema discovery failed
                        # Still keep it in available_endpoints
                        continue
            except Exception:
                # Endpoint not available, skip
                continue

        # Add OpenAPI information if available
        if self.openapi_specs:
            openapi_info = []
            for spec in self.openapi_specs:
                if isinstance(spec, dict) and "_raw_spec" in spec:
                    # Handle raw spec fallback
                    raw_spec = spec["_raw_spec"]
                    spec_info = {
                        "title": raw_spec.get("info", {}).get("title", "Unknown"),
                        "version": raw_spec.get("info", {}).get("version", "Unknown"),
                        "description": raw_spec.get("info", {}).get("description", ""),
                        "servers": [
                            server.get("url") for server in raw_spec.get("servers", [])
                        ],
                        "paths": list(raw_spec.get("paths", {}).keys()),
                        "source_url": spec.get("_source_url", "Unknown"),
                    }
                else:
                    # Handle proper OpenAPI object
                    servers = []
                    if spec.servers:
                        servers = [server.url for server in spec.servers]
                    spec_info = {
                        "title": spec.info.title if spec.info else "Unknown",
                        "version": spec.info.version if spec.info else "Unknown",
                        "description": spec.info.description if spec.info else "",
                        "servers": servers,
                        "paths": list(spec.paths.keys()) if spec.paths else [],
                    }
                openapi_info.append(spec_info)
            discovery_info["openapi_info"] = openapi_info

        return discovery_info

    def post_data(
        self: RESTAdapter, endpoint: str, data: dict[str, Any]
    ) -> pd.DataFrame:
        """POST data to an endpoint.

        Args:
            endpoint: API endpoint path
            data: Data to post

        Returns:
            DataFrame containing the response
        """
        return self.query(endpoint, method="POST", data=data)

    def put_data(
        self: RESTAdapter, endpoint: str, data: dict[str, Any]
    ) -> pd.DataFrame:
        """PUT data to an endpoint.

        Args:
            endpoint: API endpoint path
            data: Data to put

        Returns:
            DataFrame containing the response
        """
        return self.query(endpoint, method="PUT", data=data)

    def delete_data(self: RESTAdapter, endpoint: str) -> pd.DataFrame:
        """DELETE data from an endpoint.

        Args:
            endpoint: API endpoint path

        Returns:
            DataFrame containing the response
        """
        return self.query(endpoint, method="DELETE")
