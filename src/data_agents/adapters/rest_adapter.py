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
                # Extract the path part of the base URL to compare against OpenAPI paths
                from urllib.parse import urlparse

                base_parsed = urlparse(self.base_url)
                base_path = base_parsed.path.rstrip("/")

                for spec in self.openapi_specs:
                    if isinstance(spec, dict) and "_raw_spec" in spec:
                        # Handle raw spec fallback
                        raw_spec = spec["_raw_spec"]
                        if "paths" in raw_spec:
                            for path in raw_spec["paths"].keys():
                                # Remove base path if the OpenAPI path includes it
                                if base_path and path.startswith(base_path):
                                    endpoint = path[len(base_path) :].lstrip("/")
                                else:
                                    endpoint = path.lstrip("/")
                                if endpoint:  # Only add non-empty endpoints
                                    self.endpoints.append(endpoint)
                    elif hasattr(spec, "paths") and spec.paths:
                        # Handle proper OpenAPI object
                        for path in spec.paths:
                            # Remove base path if the OpenAPI path includes it
                            if base_path and path.startswith(base_path):
                                endpoint = path[len(base_path) :].lstrip("/")
                            else:
                                endpoint = path.lstrip("/")
                            if endpoint:  # Only add non-empty endpoints
                                self.endpoints.append(endpoint)
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
        """Discover API capabilities including available endpoints and comprehensive query information.

        This method performs comprehensive API discovery by:
        1. Testing endpoint availability
        2. Extracting parameter requirements from OpenAPI specs and error responses
        3. Providing detailed parameter information including types, formats, and examples
        4. Including response format information

        Returns:
            Dictionary containing comprehensive discovery information with detailed
            parameter specifications for forming queries.
        """
        endpoints = {}

        # Use configured endpoints for discovery
        if self.endpoints:
            for endpoint in self.endpoints:
                endpoint_info = self._discover_endpoint(endpoint)
                if endpoint_info:
                    endpoints[endpoint] = endpoint_info

        discovery_info = {
            "adapter_type": "rest",
            "base_url": self.base_url,
            "endpoints": endpoints,
        }

        # Add consolidated OpenAPI information
        if self.openapi_specs:
            openapi_info = self._get_openapi_info()
            if openapi_info:
                discovery_info["openapi_info"] = openapi_info

        return discovery_info

    def _discover_endpoint(self, endpoint: str) -> dict[str, Any] | None:
        """Discover information for a single endpoint.
        
        Args:
            endpoint: The endpoint path to discover
            
        Returns:
            Dictionary with endpoint information or None if not available
        """
        try:
            # Test endpoint availability
            response = requests.get(
                urljoin(self.base_url + "/", endpoint),
                headers=self.headers,
                auth=self.auth,
                timeout=self.timeout,
                verify=self.verify,
            )
            
            endpoint_url = urljoin(self.base_url + "/", endpoint)
            
            # Handle different response scenarios
            if response.status_code == 200:
                return self._handle_successful_endpoint(endpoint, endpoint_url, response)
            elif response.status_code in [400, 422]:
                return self._handle_parameterized_endpoint(endpoint, endpoint_url, response)
            else:
                return None
                
        except Exception:
            return None

    def _handle_successful_endpoint(self, endpoint: str, endpoint_url: str, response: requests.Response) -> dict[str, Any]:
        """Handle endpoints that respond successfully without parameters."""
        endpoint_info = {
            "description": f"REST endpoint: {endpoint}",
            "url": endpoint_url,
            "method": "GET",
            "required_parameters": {},
            "optional_parameters": {},
        }
        
        # Try to get sample data and response format
        try:
            params = {}
            if self.pagination_param and self.pagination_limit:
                params[self.pagination_param] = self.pagination_limit
                
            sample_df = self.query(endpoint, params=params)
            if not sample_df.empty:
                # Convert sample data to a clean format
                sample_record = sample_df.head(1).to_dict("records")[0]
                endpoint_info["response_format"] = {
                    "type": "object" if isinstance(sample_record, dict) else "array",
                    "sample_data": sample_record,
                    "columns": list(sample_df.columns),
                }
                
                # Add parameter info for pagination if supported
                if self.pagination_param:
                    endpoint_info["optional_parameters"][self.pagination_param] = {
                        "type": "integer",
                        "description": f"Limit number of results (pagination)",
                        "minimum": 1,
                    }
        except Exception:
            pass
            
        # Enhance with OpenAPI spec information if available
        self._enhance_endpoint_from_openapi(endpoint, endpoint_info)
        
        return endpoint_info

    def _handle_parameterized_endpoint(self, endpoint: str, endpoint_url: str, response: requests.Response) -> dict[str, Any]:
        """Handle endpoints that require parameters (422/400 responses)."""
        endpoint_info = {
            "description": f"REST endpoint: {endpoint}",
            "url": endpoint_url,
            "method": "GET",
            "required_parameters": {},
            "optional_parameters": {},
        }
        
        # Extract parameter requirements from error response
        try:
            error_data = response.json()
            if "detail" in error_data and isinstance(error_data["detail"], list):
                for error in error_data["detail"]:
                    if error.get("type") == "missing" and "loc" in error:
                        loc = error["loc"]
                        if len(loc) >= 2 and loc[0] == "query":
                            param_name = loc[1]
                            endpoint_info["required_parameters"][param_name] = {
                                "type": "string",  # Default type
                                "description": f"Required parameter: {param_name}",
                            }
        except Exception:
            pass
        
        # Enhance with detailed OpenAPI spec information
        self._enhance_endpoint_from_openapi(endpoint, endpoint_info)
        
        return endpoint_info

    def _enhance_endpoint_from_openapi(self, endpoint: str, endpoint_info: dict[str, Any]) -> None:
        """Enhance endpoint information using OpenAPI specifications."""
        if not self.openapi_specs:
            return
            
        for spec in self.openapi_specs:
            if isinstance(spec, dict) and "_raw_spec" in spec:
                # Handle raw spec fallback
                spec_data = spec["_raw_spec"]
                endpoint_path = f"/{endpoint}" if not endpoint.startswith("/") else endpoint
                paths = spec_data.get("paths", {})
                
                for path, path_info in paths.items():
                    if path == endpoint_path or path.endswith(f"/{endpoint}"):
                        self._extract_openapi_parameters(path_info, endpoint_info)
                        self._extract_openapi_description(path_info, endpoint_info)
                        break
            elif hasattr(spec, "paths") and spec.paths:
                # Handle proper OpenAPI object
                endpoint_path = f"/{endpoint}" if not endpoint.startswith("/") else endpoint
                
                for path, path_obj in spec.paths.items():
                    if path == endpoint_path or path.endswith(f"/{endpoint}"):
                        # Extract from OpenAPI objects directly
                        self._extract_openapi_parameters_from_object(path_obj, endpoint_info, spec)
                        self._extract_openapi_description_from_object(path_obj, endpoint_info)
                        break

    def _extract_openapi_parameters_from_object(self, path_obj: Any, endpoint_info: dict[str, Any], spec: Any) -> None:
        """Extract parameter information from OpenAPI path object."""
        if not hasattr(path_obj, "get") or not path_obj.get:
            return
            
        get_operation = path_obj.get
        if not hasattr(get_operation, "parameters") or not get_operation.parameters:
            return
            
        for param in get_operation.parameters:
            param_name = param.name
            if not param_name:
                continue
                
            param_spec = {
                "type": "string",  # Default
                "description": param.description or f"Parameter: {param_name}",
            }
            
            # Extract schema information
            if hasattr(param, "schema") and param.schema:
                schema = param.schema
                
                # Handle schema references
                if hasattr(schema, "ref") and schema.ref:
                    resolved_schema = self._resolve_schema_ref_from_object(schema.ref, spec)
                    if resolved_schema:
                        param_spec.update(self._extract_schema_info_from_object(resolved_schema))
                else:
                    param_spec.update(self._extract_schema_info_from_object(schema))
                
            # Add example if available
            if hasattr(param, "example") and param.example is not None:
                param_spec["example"] = param.example
                
            # Determine if required
            is_required = getattr(param, "required", False)
            target_params = endpoint_info["required_parameters"] if is_required else endpoint_info["optional_parameters"]
            target_params[param_name] = param_spec

    def _extract_openapi_description_from_object(self, path_obj: Any, endpoint_info: dict[str, Any]) -> None:
        """Extract description from OpenAPI path object."""
        if not hasattr(path_obj, "get") or not path_obj.get:
            return
            
        get_operation = path_obj.get
        summary = getattr(get_operation, "summary", "")
        description = getattr(get_operation, "description", "")
        
        if summary:
            endpoint_info["description"] = summary
        elif description:
            endpoint_info["description"] = description

    def _extract_schema_info_from_object(self, schema: Any) -> dict[str, Any]:
        """Extract schema information from OpenAPI schema object."""
        info = {}
        
        if hasattr(schema, "type") and schema.type:
            info["type"] = schema.type
        if hasattr(schema, "format") and schema.format:
            info["format"] = schema.format
        if hasattr(schema, "minimum") and schema.minimum is not None:
            info["minimum"] = schema.minimum
        if hasattr(schema, "maximum") and schema.maximum is not None:
            info["maximum"] = schema.maximum
        if hasattr(schema, "enum") and schema.enum:
            info["enum"] = list(schema.enum)
        if hasattr(schema, "default") and schema.default is not None:
            info["default"] = schema.default
        if hasattr(schema, "pattern") and schema.pattern:
            info["pattern"] = schema.pattern
            
        return info

    def _resolve_schema_ref_from_object(self, ref: str, spec: Any) -> Any:
        """Resolve a schema reference from OpenAPI object."""
        if not ref.startswith("#/"):
            return None
            
        path_parts = ref[2:].split("/")  # Remove '#/' and split
        
        if not hasattr(spec, "components") or not spec.components:
            return None
            
        current = spec.components
        for part in path_parts[1:]:  # Skip 'components' as we already have it
            if hasattr(current, part):
                current = getattr(current, part)
            else:
                return None
                
        return current

    def _extract_openapi_parameters(self, path_info: dict[str, Any], endpoint_info: dict[str, Any]) -> None:
        """Extract parameter information from OpenAPI path specification."""
        # Look for GET method parameters
        get_method = path_info.get("get", {})
        parameters = get_method.get("parameters", [])
        
        for param in parameters:
            param_name = param.get("name")
            if not param_name:
                continue
                
            param_spec = {
                "type": "string",  # Default
                "description": param.get("description", f"Parameter: {param_name}"),
            }
            
            # Extract schema information
            schema = param.get("schema", {})
            if schema:
                # Handle schema references
                if "$ref" in schema:
                    resolved_schema = self._resolve_schema_ref(schema["$ref"])
                    if resolved_schema:
                        param_spec.update(self._extract_schema_info(resolved_schema))
                else:
                    param_spec.update(self._extract_schema_info(schema))
                
            # Add example if available in OpenAPI spec
            if "example" in param:
                param_spec["example"] = param["example"]
                
            # Determine if required
            is_required = param.get("required", False)
            target_params = endpoint_info["required_parameters"] if is_required else endpoint_info["optional_parameters"]
            target_params[param_name] = param_spec

    def _resolve_schema_ref(self, ref: str) -> dict[str, Any] | None:
        """Resolve a schema reference like '#/components/schemas/Communities'."""
        if not ref.startswith("#/"):
            return None
            
        # Extract the path from the reference
        path_parts = ref[2:].split("/")  # Remove '#/' and split
        
        for spec in self.openapi_specs:
            spec_data = None
            if isinstance(spec, dict) and "_raw_spec" in spec:
                spec_data = spec["_raw_spec"]
            elif hasattr(spec, "__dict__"):
                spec_data = self._openapi_to_dict(spec)
                
            if not spec_data:
                continue
                
            # Navigate through the path to find the referenced schema
            current = spec_data
            for part in path_parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    current = None
                    break
                    
            if current and isinstance(current, dict):
                return current
                
        return None

    def _extract_openapi_description(self, path_info: dict[str, Any], endpoint_info: dict[str, Any]) -> None:
        """Extract description from OpenAPI path specification."""
        get_method = path_info.get("get", {})
        summary = get_method.get("summary", "")
        description = get_method.get("description", "")
        
        if summary:
            endpoint_info["description"] = summary
        elif description:
            endpoint_info["description"] = description

    def _extract_schema_info(self, schema: dict[str, Any]) -> dict[str, Any]:
        """Extract schema information into parameter specification."""
        info = {}
        
        if "type" in schema:
            info["type"] = schema["type"]
        if "format" in schema:
            info["format"] = schema["format"]
        if "minimum" in schema:
            info["minimum"] = schema["minimum"]
        if "maximum" in schema:
            info["maximum"] = schema["maximum"]
        if "enum" in schema:
            info["enum"] = schema["enum"]
        if "default" in schema:
            info["default"] = schema["default"]
        if "pattern" in schema:
            info["pattern"] = schema["pattern"]
            
        return info

    def _get_example_value(self, param_name: str) -> Any:
        """Get example value from OpenAPI spec or return None if not available."""
        # This method now only returns None - examples should come from OpenAPI specs
        return None

    def _openapi_to_dict(self, spec: Any) -> dict[str, Any] | None:
        """Convert OpenAPI object to dictionary."""
        try:
            result = {}
            if hasattr(spec, "info"):
                result["info"] = {
                    "title": spec.info.title if spec.info else "Unknown",
                    "version": spec.info.version if spec.info else "Unknown",
                    "description": spec.info.description if spec.info else "",
                }
            if hasattr(spec, "paths") and spec.paths:
                result["paths"] = {}
                for path, path_obj in spec.paths.items():
                    result["paths"][path] = self._path_to_dict(path_obj)
            return result
        except Exception:
            return None

    def _path_to_dict(self, path_obj: Any) -> dict[str, Any]:
        """Convert OpenAPI path object to dictionary."""
        result = {}
        for method in ["get", "post", "put", "delete", "patch"]:
            if hasattr(path_obj, method):
                method_obj = getattr(path_obj, method)
                if method_obj:
                    result[method] = self._operation_to_dict(method_obj)
        return result

    def _operation_to_dict(self, operation: Any) -> dict[str, Any]:
        """Convert OpenAPI operation object to dictionary."""
        result = {}
        if hasattr(operation, "summary"):
            result["summary"] = operation.summary
        if hasattr(operation, "description"):
            result["description"] = operation.description
        if hasattr(operation, "parameters"):
            result["parameters"] = []
            for param in operation.parameters:
                result["parameters"].append(self._parameter_to_dict(param))
        return result

    def _parameter_to_dict(self, param: Any) -> dict[str, Any]:
        """Convert OpenAPI parameter object to dictionary."""
        result = {}
        if hasattr(param, "name"):
            result["name"] = param.name
        if hasattr(param, "description"):
            result["description"] = param.description
        if hasattr(param, "required"):
            result["required"] = param.required
        if hasattr(param, "schema"):
            result["schema"] = self._schema_to_dict(param.schema)
        return result

    def _schema_to_dict(self, schema: Any) -> dict[str, Any]:
        """Convert OpenAPI schema object to dictionary."""
        result = {}
        for attr in ["type", "format", "minimum", "maximum", "enum", "default", "pattern"]:
            if hasattr(schema, attr):
                value = getattr(schema, attr)
                if value is not None:
                    result[attr] = value
        return result

    def _get_openapi_info(self) -> dict[str, Any] | None:
        """Get consolidated OpenAPI information."""
        if not self.openapi_specs:
            return None
            
        # Use the first spec for basic info
        spec = self.openapi_specs[0]
        
        if isinstance(spec, dict) and "_raw_spec" in spec:
            raw_spec = spec["_raw_spec"]
            info = raw_spec.get("info", {})
            return {
                "title": info.get("title", "Unknown"),
                "version": info.get("version", "Unknown"),
                "description": info.get("description", ""),
            }
        elif hasattr(spec, "info") and spec.info:
            return {
                "title": spec.info.title or "Unknown",
                "version": spec.info.version or "Unknown", 
                "description": spec.info.description or "",
            }
        
        return None

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
