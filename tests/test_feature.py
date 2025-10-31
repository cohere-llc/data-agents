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

"""Test for feature module of data_agents package."""

from typing import Any

from data_agents import Feature


def test_feature_to_dict():
    """Test the to_dict method of Feature class."""
    feature_dict: dict[str, Any] = {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [102.0, 0.5]},
        "properties": {"prop0": "value0"},
    }
    feature = Feature(feature_dict)
    assert feature.to_dict() == feature_dict
    new_feature = Feature(feature)
    assert new_feature.to_dict() == feature_dict


def test_feature_getitem():
    """Test the __getitem__ method of Feature class."""
    feature_dict: Feature = Feature(
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [102.0, 0.5]},
            "properties": {"prop0": "value0"},
        }
    )
    feature = Feature(feature_dict)
    assert feature["type"] == "Feature"
    assert feature["geometry"] == {"type": "Point", "coordinates": [102.0, 0.5]}
    assert feature["properties"] == {"prop0": "value0"}
