"""
OpenAQ Air Quality Data Adapter

A specialized adapter for querying OpenAQ air quality measurement data
with geographic filtering and parameter-based queries.
"""

import os
from typing import Any, Optional, Union

import pandas as pd
import requests

from data_agents.core.adapter import Adapter


class OpenAQAdapter(Adapter):
    """
    OpenAQ Air Quality Data Adapter

    This adapter provides specialized methods for querying OpenAQ air quality
    measurement data with geographic filtering (lat/lon ranges, bounding boxes)
    and parameter-based filtering.

    Features:
    - Query measurements by geographic region (bounding box or center point + radius)
    - Filter by air quality parameters (PM2.5, NO2, O3, etc.)
    - Date range filtering
    - Automatic location discovery and sensor querying
    - Data aggregation and formatting
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """
        Initialize OpenAQ adapter.

        Args:
            config: Configuration dictionary containing:
                - api_key: OpenAQ API key (can use env var OPENAQ_API_KEY)
                - base_url: API base URL (default: https://api.openaq.org/v3)
        """
        self.config = config or {}
        self.base_url = self.config.get("base_url", "https://api.openaq.org/v3")

        # Setup authentication
        self.api_key = self._get_api_key()
        self.headers = {}
        if self.api_key:
            self.headers["X-API-Key"] = self.api_key

        self.session = requests.Session()
        self.session.headers.update(self.headers)

        # Cache for parameter and location data
        self._parameters_cache: Optional[list[dict[str, Any]]] = None

    def _get_api_key(self) -> Optional[str]:
        """Get API key from config or environment."""
        if self.config:
            api_key = self.config.get("api_key")
            if api_key and isinstance(api_key, str):
                return str(api_key)

        # Try environment variable
        return os.getenv("OPENAQ_API_KEY")

    def query_measurements_by_region(
        self,
        bbox: Optional[list[float]] = None,
        center: Optional[dict[str, float]] = None,
        radius: Optional[int] = None,
        parameters: Optional[Union[str, list[str]]] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: Optional[int] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """
        Query air quality measurements for a geographic region.

        Args:
            bbox: Bounding box as [min_lon, min_lat, max_lon, max_lat]
            center: Center point as {"lat": float, "lon": float}
            radius: Search radius in meters (used with center, max 25000)
            parameters: Parameter name(s) to filter by (e.g., "pm25", ["pm25", "no2"])
            date_from: Start date (ISO format or YYYY-MM-DD)
            date_to: End date (ISO format or YYYY-MM-DD)
            limit: Maximum number of measurements to return
            **kwargs: Additional query parameters

        Returns:
            DataFrame containing measurement data with columns:
            - location_id, location_name, parameter, value, datetime
            - latitude, longitude, country, etc.
        """
        # Step 1: Find locations matching the geographic criteria
        locations = self._find_locations_by_region(
            bbox=bbox, center=center, radius=radius, parameters=parameters, **kwargs
        )

        if locations.empty:
            return pd.DataFrame()

        # Step 2: Get sensor IDs from locations
        sensor_ids = self._extract_sensor_ids(locations)

        if not sensor_ids:
            return pd.DataFrame()

        # Step 3: Query measurements for each sensor
        all_measurements = []
        for sensor_id in sensor_ids:
            measurements = self._get_sensor_measurements(
                sensor_id, date_from=date_from, date_to=date_to, limit=limit
            )
            if not measurements.empty:
                all_measurements.append(measurements)

        if not all_measurements:
            return pd.DataFrame()

        # Step 4: Combine and enrich measurement data
        combined_df = pd.concat(all_measurements, ignore_index=True)

        # Enrich with location data
        enriched_df = self._enrich_measurements_with_location_data(
            combined_df, locations
        )

        return enriched_df

    def query_measurements_by_parameter(
        self,
        parameter: str,
        country: Optional[str] = None,
        bbox: Optional[list[float]] = None,
        center: Optional[dict[str, float]] = None,
        radius: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: Optional[int] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """
        Query air quality measurements for a specific parameter.

        Args:
            parameter: Parameter name (e.g., "pm25", "no2", "o3")
            country: Country ISO code (e.g., "US", "FR")
            bbox: Bounding box as [min_lon, min_lat, max_lon, max_lat]
            center: Center point as {"lat": float, "lon": float}
            radius: Search radius in meters
            date_from: Start date
            date_to: End date
            limit: Maximum number of measurements
            **kwargs: Additional query parameters

        Returns:
            DataFrame containing measurement data
        """
        # Get parameter ID from parameter name
        parameter_id = self._get_parameter_id(parameter)
        if not parameter_id:
            raise ValueError(f"Parameter '{parameter}' not found")

        return self.query_measurements_by_region(
            bbox=bbox,
            center=center,
            radius=radius,
            parameters=[parameter],
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            iso=country,
            **kwargs,
        )

    def _find_locations_by_region(
        self,
        bbox: Optional[list[float]] = None,
        center: Optional[dict[str, float]] = None,
        radius: Optional[int] = None,
        parameters: Optional[Union[str, list[str]]] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Find locations matching geographic and parameter criteria."""
        params = {"limit": kwargs.get("limit", 1000)}

        # Add geographic filtering
        if bbox:
            # Convert [min_lon, min_lat, max_lon, max_lat] to OpenAQ format
            params["bbox"] = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"
        elif center is not None and radius is not None:
            if radius <= 0 or radius > 25000:
                raise ValueError(
                    "Invalid radius. Must be between 1 and 25000 meters "
                    "(OpenAQ API limit)."
                )
            params["coordinates"] = f"{center['lat']},{center['lon']}"
            params["radius"] = str(radius)

        # Add parameter filtering
        if parameters:
            if isinstance(parameters, str):
                parameters = [parameters]

            parameter_ids = []
            for param in parameters:
                param_id = self._get_parameter_id(param)
                if param_id:
                    parameter_ids.append(str(param_id))

            if parameter_ids:
                params["parameters_id"] = ",".join(parameter_ids)

        # Add other filters
        for key, value in kwargs.items():
            if key not in ["limit"] and value is not None:
                params[key] = str(value)

        # Query locations endpoint
        url = f"{self.base_url}/locations"
        response = self.session.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        if not data.get("results"):
            return pd.DataFrame()

        # Convert to DataFrame
        locations_data = []
        for location in data["results"]:
            location_info = {
                "location_id": location.get("id"),
                "location_name": location.get("name"),
                "latitude": location.get("coordinates", {}).get("latitude"),
                "longitude": location.get("coordinates", {}).get("longitude"),
                "country_code": location.get("country", {}).get("code"),
                "country_name": location.get("country", {}).get("name"),
                "timezone": location.get("timezone"),
                "locality": location.get("locality"),
                "sensors": location.get("sensors", []),
            }
            locations_data.append(location_info)

        return pd.DataFrame(locations_data)

    def _extract_sensor_ids(self, locations_df: pd.DataFrame) -> list[int]:
        """Extract sensor IDs from locations DataFrame."""
        sensor_ids = []

        for _, location in locations_df.iterrows():
            sensors = location.get("sensors", [])
            if isinstance(sensors, list):
                for sensor in sensors:
                    if isinstance(sensor, dict) and "id" in sensor:
                        sensor_ids.append(sensor["id"])

        return list(set(sensor_ids))  # Remove duplicates

    def _get_sensor_measurements(
        self,
        sensor_id: int,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        """Get measurements for a specific sensor."""
        params = {}

        if date_from:
            params["datetime_from"] = date_from
        if date_to:
            params["datetime_to"] = date_to
        if limit is not None:
            try:
                limit_int = int(limit)
                if 1 <= limit_int <= 10000:
                    params["limit"] = str(limit_int)
                else:
                    raise ValueError("Limit must be between 1 and 10000")
            except (ValueError, TypeError) as e:
                raise ValueError("Limit must be an integer between 1 and 10000") from e

        url = f"{self.base_url}/sensors/{sensor_id}/measurements"

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            measurements = data.get("results", [])

            if not measurements:
                return pd.DataFrame()

            # Convert to DataFrame
            measurements_data = []
            for measurement in measurements:
                measurement_info = {
                    "sensor_id": sensor_id,
                    "datetime": measurement.get("datetime"),
                    "value": measurement.get("value"),
                    "parameter": measurement.get("parameter", {}).get("name"),
                    "parameter_id": measurement.get("parameter", {}).get("id"),
                    "units": measurement.get("parameter", {}).get("units"),
                }
                measurements_data.append(measurement_info)

            return pd.DataFrame(measurements_data)

        except requests.RequestException as e:
            print(f"Warning: Failed to get measurements for sensor {sensor_id}: {e}")
            return pd.DataFrame()

    def _enrich_measurements_with_location_data(
        self, measurements_df: pd.DataFrame, locations_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Enrich measurements with location information."""
        if measurements_df.empty or locations_df.empty:
            return measurements_df

        # Create sensor to location mapping
        sensor_location_map = {}

        for _, location in locations_df.iterrows():
            sensors = location.get("sensors", [])
            if isinstance(sensors, list):
                for sensor in sensors:
                    if isinstance(sensor, dict) and "id" in sensor:
                        sensor_location_map[sensor["id"]] = {
                            "location_id": location["location_id"],
                            "location_name": location["location_name"],
                            "latitude": location["latitude"],
                            "longitude": location["longitude"],
                            "country_code": location["country_code"],
                            "country_name": location["country_name"],
                            "timezone": location["timezone"],
                            "locality": location["locality"],
                        }

        # Add location data to measurements
        location_data = []
        for _, measurement in measurements_df.iterrows():
            sensor_id = measurement["sensor_id"]
            location_info = sensor_location_map.get(sensor_id, {})

            enriched_measurement = {**measurement.to_dict(), **location_info}
            location_data.append(enriched_measurement)

        return pd.DataFrame(location_data)

    def _get_parameter_id(self, parameter_name: str) -> Optional[int]:
        """Get parameter ID from parameter name."""
        if self._parameters_cache is None:
            self._load_parameters()

        if self._parameters_cache is None:
            return None

        # Try exact match first
        for param in self._parameters_cache:
            if param.get("name", "").lower() == parameter_name.lower():
                return param.get("id")

        # Try partial match
        for param in self._parameters_cache:
            if parameter_name.lower() in param.get("name", "").lower():
                return param.get("id")

        return None

    def _load_parameters(self) -> None:
        """Load available parameters from the API."""
        try:
            url = f"{self.base_url}/parameters"
            response = self.session.get(url)
            response.raise_for_status()

            data = response.json()
            self._parameters_cache = data.get("results", [])
        except requests.RequestException as e:
            print(f"Warning: Failed to load parameters: {e}")
            self._parameters_cache = []

    def get_available_parameters(self) -> pd.DataFrame:
        """Get list of available air quality parameters."""
        if self._parameters_cache is None:
            self._load_parameters()

        if not self._parameters_cache:
            return pd.DataFrame()

        return pd.DataFrame(self._parameters_cache)

    def query(self, query: str, **kwargs: Any) -> pd.DataFrame:
        """
        General query interface for compatibility with base adapter.

        This method provides a simplified interface that routes to the
        appropriate specialized method based on the query string.

        Query formats:
        - "measurements?bbox=min_lon,min_lat,max_lon,max_lat&parameter=pm25"
        - "measurements?center=lat,lon&radius=5000&parameter=no2"
        - "parameter:pm25&country=US&limit=100"

        Args:
            query: Query string
            **kwargs: Additional parameters

        Returns:
            DataFrame containing results
        """
        # Parse query string
        if query.startswith("measurements"):
            return self._handle_measurements_query(query, **kwargs)
        elif "parameter:" in query:
            return self._handle_parameter_query(query, **kwargs)
        else:
            # Fall back to basic parameter search
            return self.query_measurements_by_parameter(query, **kwargs)

    def _handle_measurements_query(self, query: str, **kwargs: Any) -> pd.DataFrame:
        """Handle measurements query format."""
        # Parse query parameters
        if "?" in query:
            _, params_str = query.split("?", 1)
            params = dict(p.split("=") for p in params_str.split("&") if "=" in p)
        else:
            params = {}

        # Extract geographic parameters
        bbox = None
        center = None
        radius = None

        if "bbox" in params:
            bbox_str = params["bbox"]
            bbox = [float(x) for x in bbox_str.split(",")]

        if "center" in params:
            center_str = params["center"]
            lat, lon = center_str.split(",")
            center = {"lat": float(lat), "lon": float(lon)}

        if "radius" in params:
            radius = int(params["radius"])

        # Extract other parameters
        parameters_str = params.get("parameter")
        parameters: Optional[list[str]] = None
        if parameters_str:
            parameters = parameters_str.split(",")

        return self.query_measurements_by_region(
            bbox=bbox, center=center, radius=radius, parameters=parameters, **kwargs
        )

    def _handle_parameter_query(self, query: str, **kwargs: Any) -> pd.DataFrame:
        """Handle parameter-specific query format."""
        # Extract parameter name
        if "parameter:" in query:
            parts = query.split("parameter:")
            if len(parts) > 1:
                param_and_rest = parts[1]
                if "&" in param_and_rest:
                    parameter = param_and_rest.split("&")[0]
                else:
                    parameter = param_and_rest

                return self.query_measurements_by_parameter(parameter, **kwargs)

        return pd.DataFrame()

    def discover(self) -> dict[str, Any]:
        """
        Discover available parameters and capabilities.

        Returns:
            Dictionary containing adapter capabilities and available parameters
        """
        parameters_df = self.get_available_parameters()

        return {
            "adapter_type": "openaq",
            "base_url": self.base_url,
            "description": "OpenAQ Air Quality Data Adapter with geographic filtering",
            "capabilities": {
                "geographic_filtering": [
                    "bounding_box",
                    "center_point_radius",
                    "coordinates",
                ],
                "parameter_filtering": True,
                "temporal_filtering": True,
                "aggregation": False,
            },
            "query_methods": {
                "query_measurements_by_region": {
                    "description": "Query measurements by geographic region",
                    "parameters": [
                        "bbox",
                        "center",
                        "radius",
                        "parameters",
                        "date_from",
                        "date_to",
                        "limit",
                    ],
                },
                "query_measurements_by_parameter": {
                    "description": "Query measurements by air quality parameter",
                    "parameters": [
                        "parameter",
                        "country",
                        "bbox",
                        "center",
                        "radius",
                        "date_from",
                        "date_to",
                        "limit",
                    ],
                },
            },
            "available_parameters": parameters_df.to_dict("records")
            if not parameters_df.empty
            else [],
            "examples": [
                {
                    "description": "Get PM2.5 measurements in New York area",
                    "code": (
                        "adapter.query_measurements_by_parameter('pm25', "
                        "center={'lat': 40.7128, 'lon': -74.0060}, radius=10000)"
                    ),
                },
                {
                    "description": "Get all measurements in a bounding box",
                    "code": (
                        "adapter.query_measurements_by_region("
                        "bbox=[-74.1, 40.6, -73.9, 40.8])"
                    ),
                },
            ],
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert adapter to dictionary representation."""
        return {
            "adapter_type": "openaq",
            "base_url": self.base_url,
            "has_api_key": bool(self.api_key),
            "capabilities": {
                "geographic_filtering": True,
                "parameter_filtering": True,
                "temporal_filtering": True,
            },
        }
