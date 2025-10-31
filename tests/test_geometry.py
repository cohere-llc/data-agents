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

"""Test for geometry module of data_agents package."""

from collections.abc import Callable
from typing import Any

from data_agents import Geometry


def test_geometry_to_dict():
    """Test the to_dict method of Geometry class."""
    geom_dict: dict[str, Any] = {"type": "Point", "coordinates": [102.0, 0.5]}
    geometry = Geometry(geom_dict)
    assert geometry.to_dict() == geom_dict
    new_geometry = Geometry(geometry)
    assert new_geometry.to_dict() == geom_dict


def test_geometry_getitem():
    """Test the __getitem__ method of Geometry class."""
    geom_dict: Geometry = Geometry({"type": "Point", "coordinates": [102.0, 0.5]})
    geometry = Geometry(geom_dict)
    assert geometry["type"] == "Point"
    assert geometry["coordinates"] == [102.0, 0.5]


def test_geometry_to_point():
    """Test the to_point method of Geometry class."""
    geom_fn: Callable[[dict[str, Any]], Geometry] = Geometry.to_point(["lat", "lon"])
    geometry = geom_fn({"foo": "A", "lon": 102.0, "bar": "B", "lat": "0.5"})
    expected_geom: Geometry = Geometry({"type": "Point", "coordinates": [0.5, 102.0]})
    assert geometry.to_dict() == expected_geom.to_dict()
