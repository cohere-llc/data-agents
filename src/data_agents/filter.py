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

"""The Filter class and related functionality."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .feature import Feature
from .feature_collection import FeatureCollection


class Filter:
    """A class to filter data based on specified criteria."""

    def __init__(
        self,
        fn: Callable[[Feature], bool],
        join_fn: Callable[[Feature, list[Feature], str, str], list[Feature]]
        | None = None,
        **kwargs: Any,
    ):
        """Initialize the Filter with given criteria.

        Args:
            **kwargs: Arbitrary keyword arguments representing filter criteria.
        """
        self._type: str = "unknown"
        self._fn: Callable[[Feature], bool] = fn
        self._join_fn: (
            Callable[[Feature, list[Feature], str, str], list[Feature]] | None
        ) = join_fn
        self._match_key: str = "match_id"
        self._quality_key: str = "match_quality"
        self._feature_collection: FeatureCollection | None = None
        for key, value in kwargs.items():
            setattr(self, f"_{key.lstrip('_')}", value)

    def to_dict(self) -> dict[str, Any]:
        """Return the filter as a dictionary."""
        return self.__dict__

    def apply_feature_collection(self, feature_collection: FeatureCollection) -> Filter:
        """Apply a FeatureCollection to the filter for joined filters.

        Args:
            feature_collection (FeatureCollection): The feature collection to use.
        Returns:
            Filter: The updated Filter instance.
        """

        def default_fn(feature: Feature) -> bool:
            return True

        fn: Callable[[Feature], bool] = getattr(self, "_fn", default_fn)
        join_fn: Callable[[Feature, list[Feature], str, str], list[Feature]] | None = (
            getattr(self, "_join_fn", None)
        )

        # Copy all attributes except functions and feature_collection
        kwargs = {
            k.lstrip("_"): v
            for k, v in self.__dict__.items()
            if k not in ("_fn", "_join_fn", "_feature_collection")
        }

        new_filter = Filter(fn, join_fn, **kwargs)
        new_filter._feature_collection = feature_collection
        return new_filter

    def compute(self, features: list[Feature]) -> list[Feature]:
        """Apply the filter to a list of features.

        Args:
            features (list[Feature]): The list of features to filter.

        Returns:
            list[Feature]: The filtered list of features.
        """
        # Implement filtering logic based on the filter type and criteria
        filtered_features: list[Feature] = []
        if self._feature_collection is not None:
            right_features = self._feature_collection.features()
            if self._join_fn is None:
                raise ValueError(f"Invalid filter for join: {self._type}")
            for feature in features:
                filtered_features.extend(
                    self._join_fn(
                        feature,
                        right_features,
                        self._match_key,
                        self._quality_key,
                    )
                )
        else:
            for feature in features:
                if self._fn(feature):
                    filtered_features.append(feature)
        return filtered_features

    @staticmethod
    def eq(field: str, value: Any) -> Filter:
        """Create an equality filter.

        Args:
            field (str): The name of the field to compare.
            value (Any): The value to compare against.

        Returns:
            Filter: An instance of the Filter class.
        """

        def fn(feature: Feature) -> bool:
            props = feature["properties"]
            if props is None:
                return True
            return True if props[field] is None else props[field] == value

        return Filter(fn=fn, type="eq", field=field, value=value)

    @staticmethod
    def date(field: str, start: str, end: str) -> Filter:
        """Create a date filter.

        Args:
            field (str): The name of the date field.
            start (str): The start date in ISO format. (e.g., "YYYY-MM-DD")
            end (str): The end date in ISO format. (e.g., "YYYY-MM-DD")

        Returns:
            Filter: An instance of the Filter class.
        """

        def fn(feature: Feature) -> bool:
            return True  # Stub implementation

        return Filter(fn=fn, type="date", field=field, start=start, end=end)

    @staticmethod
    def within_distance(left_field: str, right_field: str, distance: float) -> Filter:
        """Create a filter that checks if two fields are within a certain distance.

        Args:
            left_field (str): The name of the left field.
            right_field (str): The name of the right field.
            distance (float): The distance threshold.

        Returns:
            Filter: An instance of the Filter class.
        """

        def fn(feature: Feature) -> bool:
            return True  # Stub implementation

        def join_fn(
            left: Feature,
            right_features: list[Feature],
            match_key: str,
            quality_key: str,
        ) -> list[Feature]:
            return right_features  # Stub implementation

        return Filter(
            fn=fn,
            join_fn=join_fn,
            type="within_distance",
            left_field=left_field,
            right_field=right_field,
            distance=distance,
        )
