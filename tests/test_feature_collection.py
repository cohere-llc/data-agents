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

"""Test for the feature_collection module of data_agents package."""

import tempfile
from typing import Any

from data_agents import Feature, FeatureCollection, Geometry


def test_feature_collection_to_dict():
    """Test the to_dict method of FeatureCollection class."""
    feature_dict: dict[str, Any] = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [102.0, 0.5]},
                "properties": {"prop0": "value0"},
            }
        ],
    }
    feature_collection = FeatureCollection(feature_dict)
    assert feature_collection.to_dict() == feature_dict
    new_feature_collection = FeatureCollection(feature_collection)
    assert new_feature_collection.to_dict() == feature_dict


def test_feature_collection_from_feature_list():
    """Test creating FeatureCollection from a list of Feature objects."""
    feature1 = Feature(
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [102.0, 0.5]},
            "properties": {"prop0": "value0"},
        }
    )
    feature2 = Feature(
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [103.0, 1.5]},
            "properties": {"prop1": "value1"},
        }
    )
    feature_collection = FeatureCollection([feature1, feature2])
    expected_dict: dict[str, Any] = {
        "type": "FeatureCollection",
        "features": [feature1.to_dict(), feature2.to_dict()],
    }
    assert feature_collection.to_dict() == expected_dict


def test_feature_collection_getitem():
    """Test the __getitem__ method of FeatureCollection class."""
    feature_collection_dict: FeatureCollection = FeatureCollection(
        {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [102.0, 0.5]},
                    "properties": {"prop0": "value0"},
                }
            ],
        }
    )
    feature_collection = FeatureCollection(feature_collection_dict)
    assert feature_collection["type"] == "FeatureCollection"
    assert feature_collection["features"] == [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [102.0, 0.5]},
            "properties": {"prop0": "value0"},
        }
    ]


def test_feature_collection_get_info():
    """Test the get_info method of FeatureCollection class."""
    feature_collection_dict: dict[str, Any] = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [102.0, 0.5]},
                "properties": {"prop0": "value0"},
            }
        ],
    }
    feature_collection = FeatureCollection(feature_collection_dict)
    assert feature_collection.get_info() == feature_collection_dict


def test_feature_collection_properties():
    """Test the properties method of FeatureCollection class."""
    feature_collection_dict: dict[str, Any] = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [102.0, 0.5]},
                "properties": {"prop0": "value0", "temperature": 25},
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [103.0, 1.5]},
                "properties": {"prop1": "value1", "temp_avg": 22, "propA": 100},
            },
        ],
    }
    feature_collection = FeatureCollection(feature_collection_dict)
    all_properties = feature_collection.properties()
    expected_all_properties = {
        "prop0": None,
        "temperature": None,
        "prop1": None,
        "temp_avg": None,
        "propA": None,
    }
    assert all_properties == expected_all_properties

    temp_properties = feature_collection.properties("temp")
    expected_temp_properties = {"temperature": None, "temp_avg": None}
    assert temp_properties == expected_temp_properties

    # Test with a non-matching regex
    non_matching_properties = feature_collection.properties("non_matching")
    expected_non_matching_properties = {}
    assert non_matching_properties == expected_non_matching_properties

    # Test with digit regex
    digit_properties = feature_collection.properties("prop\\d")
    expected_digit_properties = {"prop0": None, "prop1": None}
    assert digit_properties == expected_digit_properties


def test_feature_collection_from_dict():
    """Test the from_dict static method of FeatureCollection class."""
    data: list[dict[str, Any]] = [
        {"id": 1, "name": "Feature 1", "lat": 0.5, "lon": 102.0},
        {"id": 2, "name": "Feature 2", "lat": 1.5, "lon": 103.0},
    ]

    def geometry_fn(item: dict[str, Any]) -> Geometry:
        return Geometry(
            {
                "type": "Point",
                "coordinates": [item["lat"], item["lon"]],
            }
        )

    feature_collection = FeatureCollection.from_dict(data, geometry_fn)
    expected_dict: dict[str, Any] = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [0.5, 102.0],
                },
                "properties": {"id": 1, "name": "Feature 1", "lat": 0.5, "lon": 102.0},
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [1.5, 103.0],
                },
                "properties": {"id": 2, "name": "Feature 2", "lat": 1.5, "lon": 103.0},
            },
        ],
    }
    assert feature_collection.to_dict() == expected_dict


def test_feature_collection_from_csv():
    """Test the from_csv static method of FeatureCollection class."""
    import csv

    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".csv") as tmpfile:
        csv_file = tmpfile.name
        writer = csv.DictWriter(tmpfile, fieldnames=["id", "name", "lat", "lon"])
        writer.writeheader()
        writer.writerow({"id": 1, "name": "Feature 1", "lat": 0.5, "lon": 102.0})
        writer.writerow({"id": 2, "name": "Feature 2", "lat": 1.5, "lon": 103.0})

    def geometry_fn(item: dict[str, Any]) -> Geometry:
        return Geometry(
            {
                "type": "Point",
                "coordinates": [float(item["lat"]), float(item["lon"])],
            }
        )

    feature_collection = FeatureCollection.from_csv(str(csv_file), geometry_fn)
    expected_dict: dict[str, Any] = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [0.5, 102.0],
                },
                "properties": {
                    "id": "1",
                    "name": "Feature 1",
                    "lat": "0.5",
                    "lon": "102.0",
                },
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [1.5, 103.0],
                },
                "properties": {
                    "id": "2",
                    "name": "Feature 2",
                    "lat": "1.5",
                    "lon": "103.0",
                },
            },
        ],
    }
    assert feature_collection.to_dict() == expected_dict
