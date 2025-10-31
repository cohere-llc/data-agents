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

"""Definition of the FeatureCollection class and related functionality."""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

from .feature import Feature
from .geometry import Geometry


class FeatureCollection:
    """A collection of features with associated geometries and properties in GeoJSON
    format."""

    def __init__(self, geo_json: dict[str, Any] | list[Feature] | FeatureCollection):
        if isinstance(geo_json, FeatureCollection):
            self._type: str = geo_json._type
            self._features: list[Feature] = geo_json._features
        elif isinstance(geo_json, list):
            self._type = "FeatureCollection"
            self._features = geo_json
        else:
            self._type = geo_json["type"]
            self._features = [Feature(feature) for feature in geo_json["features"]]

    def to_dict(self) -> dict[str, Any]:
        """Return the feature collection as a dictionary."""
        return {
            "type": self._type,
            "features": [feature.to_dict() for feature in self._features],
        }

    def __getitem__(self, key: str) -> Any:
        return self.to_dict()[key]

    def get_info(self) -> dict[str, Any]:
        """Return all information about the FeatureCollection."""
        return self.to_dict()

    def properties(self, regex: str | None = None) -> dict[str, Any]:
        """Return a dictionary of all property names in the FeatureCollection.
        Args:
            regex: If provided, only return property names that match this
                    regular expression.
        Returns:
            A dictionary with property names as keys and any associated metadata as
            values.
        """

        prop_set: set[Any] = set()
        for feature in self._features:
            for key in feature["properties"].keys():
                if regex is None or re.search(regex, key):
                    prop_set.add(key)
        return dict.fromkeys(prop_set)

    @staticmethod
    def from_dict(
        data: list[dict[str, Any]],
        geometry_fn: Callable[[dict[str, Any]], Geometry],
    ) -> FeatureCollection:
        """Create a FeatureCollection from a list of property dictionaries and a
           geometry function.

        Args:
            data: A list of dictionaries representing feature properties.
            geometry_fn: A function that takes a property dictionary and returns a
                         geometry dictionary.
        """
        features: list[Feature] = []
        for item in data:
            geometry: Geometry = geometry_fn(item)
            feature: Feature = Feature(
                {
                    "type": "Feature",
                    "geometry": geometry,
                    "properties": item,
                }
            )
            features.append(feature)
        return FeatureCollection(features)

    @staticmethod
    def from_csv(
        csv_file: str,
        geometry_fn: Callable[[dict[str, Any]], Geometry],
    ) -> FeatureCollection:
        """Create a FeatureCollection from a CSV file and a geometry function.

        Args:
            csv_file: Path to the CSV file.
            geometry_fn: A function that takes a property dictionary and returns a
                         geometry dictionary.
        """
        import csv

        features: list[Feature] = []
        with open(csv_file) as f:
            reader = csv.DictReader(f)
            for row in reader:
                geometry: Geometry = geometry_fn(row)
                feature: Feature = Feature(
                    {
                        "type": "Feature",
                        "geometry": geometry,
                        "properties": row,
                    }
                )
                features.append(feature)
        return FeatureCollection(features)

    @staticmethod
    def from_service(path: str, **kwargs: Any) -> FeatureCollection:
        """Create a FeatureCollection from a service path.

        Args:
            path: The service path string.
            **kwargs: Additional keyword arguments to pass to the service adapter.
        Returns:
            A FeatureCollection instance.
        """
        return FeatureCollection({})
