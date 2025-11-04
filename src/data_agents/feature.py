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

"""Definition of the Feature class and related functionality."""

from __future__ import annotations

from typing import Any

from .geometry import Geometry


class Feature:
    """A single feature with a geometry and properties in GeoJSON format."""

    def __init__(self, geo_json: dict[str, Any] | Feature):
        if isinstance(geo_json, Feature):
            self._type: str = geo_json._type
            self._geometry: Geometry = geo_json._geometry
            self._properties: dict[str, Any] = geo_json._properties
        else:
            self._type = geo_json["type"] if "type" in geo_json else "Feature"
            self._geometry = Geometry(geo_json["geometry"])
            self._properties = geo_json["properties"]

    def to_dict(self) -> dict[str, Any]:
        """Return the feature as a dictionary."""
        return {
            "type": self._type,
            "geometry": self._geometry.to_dict(),
            "properties": self._properties,
        }

    def __getitem__(self, key: str) -> Any:
        return self.to_dict()[key]
