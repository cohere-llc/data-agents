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

"""Definition of the Geometry class and related functionality."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


class Geometry:
    """A geometric object representing spatial data."""

    def __init__(self, geo_json: dict[str, Any] | Geometry):
        if isinstance(geo_json, Geometry):
            self._type: str = geo_json._type
            self._coordinates: list[float] = geo_json._coordinates
        else:
            self._type = geo_json["type"]
            self._coordinates = geo_json["coordinates"]

    def to_dict(self) -> dict[str, Any]:
        """Return the geometry as a dictionary."""
        return {
            "type": self._type,
            "coordinates": self._coordinates,
        }

    def __getitem__(self, key: str) -> Any:
        return self.to_dict()[key]

    @staticmethod
    def to_point(coords: list[str]) -> Callable[[dict[str, Any]], Geometry]:
        """Returns a lambda that looks up named coordinates from a dict and returns a
           Geometry.

        Args:
            latitude: The key name for the latitude value.
            longitude: The key name for the longitude value.

        Returns:
            A Lambda function that takes a dict and returns a Geometry.
        """
        return lambda data_set: Geometry(
            {
                "type": "Point",
                "coordinates": [float(data_set[coord]) for coord in coords],
            }
        )
