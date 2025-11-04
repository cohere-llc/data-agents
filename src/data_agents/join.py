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

"""The Join class and related functionality."""

from __future__ import annotations

from typing import Any

from .feature_collection import FeatureCollection
from .filter import Filter


class Join:
    """A class representing a join operation between two datasets."""

    def __init__(self, **kwargs: Any):
        """Initialize the Join instance.

        Args:
            **kwargs: Arbitrary keyword arguments.
        """
        self._left: FeatureCollection | None = None
        self._right: FeatureCollection | None = None
        self._filter: Filter | None = None
        for key, value in kwargs.items():
            setattr(self, f"_{key.lstrip('_')}", value)

    @staticmethod
    def save_best(
        matches_key: str | None = None, distance_key: str | None = None
    ) -> Join:
        """Create a save_best join.

        Args:
            matches_key (str | None): The key for matches.
            distance_key (str | None): The key for distance.

        Returns:
            Join: An instance of the Join class.
        """
        if matches_key is None:
            matches_key = "best_match"
        if distance_key is None:
            distance_key = "best_distance"
        return Join(
            type="save_best", matches_key=matches_key, distance_key=distance_key
        )

    def apply(
        self, left: FeatureCollection, right: FeatureCollection, filter: Filter
    ) -> FeatureCollection:
        """Apply the join operation to two feature collections.

        Args:
            left (FeatureCollection): The left feature collection.
            right (FeatureCollection): The right feature collection.
            filter (Filter): The filter to apply during the join.

        Returns:
            FeatureCollection: The resulting feature collection after the join.
        """
        self._left = left
        self._right = right
        self._filter = filter
        return FeatureCollection(self)

    def compute(self, filters: list[Filter]) -> FeatureCollection:
        """Compute the joined FeatureCollection.

        Returns:
            FeatureCollection: The resulting feature collection after the join.
        """
        if self._left is None or self._right is None or self._filter is None:
            raise ValueError(
                "Left, right, and filter must be set before computing the join."
            )
        left = self._left.filter(filters).compute()
        join_filter = self._filter.apply_feature_collection(left)
        return self._right.filter([join_filter, *filters]).compute()
