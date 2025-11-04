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
from typing import TYPE_CHECKING, Any

from .feature import Feature
from .geometry import Geometry

if TYPE_CHECKING:
    from .filter import Filter
    from .join import Join


class FeatureCollection:
    """A collection of features with associated geometries and properties in GeoJSON
    format."""

    def __init__(
        self, geo_json: dict[str, Any] | list[Feature] | FeatureCollection | Join
    ):
        from .join import Join  # Import here to avoid circular dependency

        self._type: str = "FeatureCollection"
        self._join: Join | None = None
        self._filters: list[Filter] = []
        self._features: list[Feature] = []
        if isinstance(geo_json, Join):
            self._join = geo_json
        elif isinstance(geo_json, FeatureCollection):
            self._type = geo_json._type
            self._features = (
                geo_json._features if hasattr(geo_json, "_features") else []
            )
            self._join = geo_json._join if hasattr(geo_json, "_join") else None
            self._filters = (
                geo_json._filters.copy() if hasattr(geo_json, "_filters") else []
            )
        elif isinstance(geo_json, list):
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

    def _compute_filters(self) -> FeatureCollection:
        """Apply all filters to the FeatureCollection."""
        features = self._features
        for filter in self._filters:
            features = filter.compute(features)
        new_fc = FeatureCollection(features)
        return new_fc

    def compute(self) -> FeatureCollection:
        """Compute the FeatureCollection by applying any joins and filters."""
        if self._join is not None:
            print("Computing join...")
            return self._join.compute(self._filters)
        if len(self._filters) > 0:
            print("Computing filters...")
            return self._compute_filters()
        return self

    def features(self) -> list[Feature]:
        """Return the list of features in the FeatureCollection."""
        return self._features

    def filter(self, filter: Filter | list[Filter]) -> FeatureCollection:
        """Apply a filter to the FeatureCollection.

        Args:
            filter (Filter): The filter to apply.

        Returns:
            FeatureCollection: A new FeatureCollection with the filter applied.
        """
        new_fc = FeatureCollection(self)
        new_fc._filters.extend(filter if isinstance(filter, list) else [filter])
        return new_fc

    def get_info(self) -> dict[str, Any]:
        """Return all information about the FeatureCollection."""
        print("Computing FeatureCollection...")
        return self.compute().to_dict()

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
