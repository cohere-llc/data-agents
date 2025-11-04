# Copyright (c) 2025 The KBase Project and its Contributors
# Copyright (c) 2025 Cohere Consulting, LLC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE

"""NASA POWER service adapter"""

from __future__ import annotations

import re
from typing import Any

import requests

from ..feature_collection import FeatureCollection


class NasaPower(FeatureCollection):
    """Adapter for NASA POWER data as a FeatureCollection."""

    BASE_URL: str = "https://power.larc.nasa.gov/api/"

    COMMUNITIES: dict[str, str] = {"AG": "AG", "RE": "RE", "SU": "SU"}

    PRODUCTS: dict[str, Any] = {
        "HOURLY": {
            "description": "hourly averages",
            "path": "temporal/hourly",
            "OpenAPI": "temporal/hourly/openapi.json",
            "save_best_filter": {
                "endpoint": "point",
                "geometry": {
                    "type": "Point",
                    "coordinates": ["latitude", "longitude"],
                },
            },
        },
        "DAILY": {
            "description": "daily averages",
            "path": "temporal/daily",
            "OpenAPI": "temporal/daily/openapi.json",
            "save_best_filter": {
                "endpoint": "point",
                "geometry": {
                    "type": "Point",
                    "coordinates": ["latitude", "longitude"],
                },
            },
        },
        "MONTHLY": {
            "description": "monthly averages",
            "path": "temporal/monthly",
            "OpenAPI": "temporal/monthly/openapi.json",
            "save_best_filter": {
                "endpoint": "point",
                "geometry": {
                    "type": "Point",
                    "coordinates": ["latitude", "longitude"],
                },
            },
        },
        "CLIMATOLOGY": {
            "description": "climatology averages",
            "path": "temporal/climatology",
            "OpenAPI": "temporal/climatology/openapi.json",
            "save_best_filter": {
                "endpoint": "point",
                "geometry": {
                    "type": "Point",
                    "coordinates": ["latitude", "longitude"],
                },
            },
        },
    }

    def __init__(self, path: list[str], **kwargs: Any | None):
        # Here we would normally implement logic to fetch data from NASA POWER API
        # For this example, we'll simulate with a placeholder GeoJSON structure
        geo_json: dict[str, Any] = {"type": "FeatureCollection", "features": []}
        super().__init__(geo_json)

        if len(path) != 3:
            raise ValueError(
                "NasaPower paths must be in the format 'NASA_POWER/PRODUCT/COMMUNITY'"
            )

        if path[0] != "NASA_POWER":
            raise ValueError("Path must start with 'NASA_POWER'")
        product = path[1]
        if product not in self.PRODUCTS:
            raise ValueError(f"Unknown product '{product}' for NASA POWER")
        community = path[2]
        if community not in self.COMMUNITIES:
            raise ValueError(f"Unknown community '{community}' for NASA POWER")
        self._endpoint: str = f"{self.BASE_URL}{self.PRODUCTS[product]['path']}"
        self._product: str = product
        self._community: str = community
        self._session: requests.Session = requests.Session()
        self._properties_cache: dict[str, Any] | None = None

    def __finalize__(self) -> None:
        """Finalize the FeatureCollection."""
        self._session.close()

    def _compute_filters(self) -> FeatureCollection:
        """Apply all filters to the FeatureCollection."""
        
        return self

    def properties(self, regex: str | None = None) -> dict[str, Any]:
        """Return a dict of available properties for the NASA POWER
        FeatureCollection."""
        url = f"{self.BASE_URL}system/manager/parameters"
        params = {"community": self._community, "temporal": self._product.lower()}

        if self._properties_cache is None:
            try:
                response = self._session.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                self._properties_cache = self._structure_parameter_data(data)
            except requests.RequestException as e:
                raise RuntimeError(
                    f"Error fetching properties for NASA POWER: {e}"
                ) from e

        if regex is None:
            return self._properties_cache
        else:
            filtered_params: dict[str, Any] = {}
            for key, value in self._properties_cache.items():
                if re.search(regex, key, re.IGNORECASE):
                    filtered_params[key] = value
                elif isinstance(value, dict):
                    if re.search(regex, value.get("name", ""), re.IGNORECASE):  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]
                        filtered_params[key] = value
            return filtered_params

    def _structure_parameter_data(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        """
        Convert raw API response to structured parameter data.

        Args:
            raw_data: Raw response from System Manager API

        Returns:
            Structured parameter dictionary
        """
        structured: dict[str, Any] = {}

        for param_code, param_info in raw_data.items():
            if isinstance(param_info, dict) and "name" in param_info:
                structured[param_code] = {
                    "abbreviation": param_code,
                    "name": param_info["name"],
                    "description": param_info["definition"],
                    "units": param_info["units"],
                    "type": param_info["type"],
                    "temporal": param_info["temporal"],
                    "source": param_info["source"],
                    "community": param_info["community"],
                }

        return structured
