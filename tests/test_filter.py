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

"""Tests for the filter module of data_agents package."""

import data_agents as da


def test_filter_within_distance():
    """Test the within_distance filter."""
    filter = da.Filter.within_distance(
        left_field="geo1", right_field="geo2", distance=1500
    )
    assert filter is not None
    out_dict = filter.to_dict()
    assert out_dict["_fn"] is not None
    del out_dict["_fn"]  # Remove the function for comparison
    assert out_dict["_join_fn"] is not None
    del out_dict["_join_fn"]  # Remove the function for comparison
    assert filter.to_dict() == {
        "_type": "within_distance",
        "_left_field": "geo1",
        "_right_field": "geo2",
        "_distance": 1500,
        "_feature_collection": None,
        "_match_key": "match_id",
        "_quality_key": "match_quality",
    }


def test_filter_eq():
    """Test the Eq filter."""
    filter = da.Filter.eq(field="status", value="active")
    assert filter is not None
    geo = da.Geometry({"type": "Point", "coordinates": [-122.4194, 37.7749]})
    fc = da.FeatureCollection(
        [
            da.Feature(
                {
                    "properties": {"id": "f1", "status": "active", "other": "value1"},
                    "geometry": geo,
                }
            ),
            da.Feature(
                {
                    "properties": {"id": "f2", "status": "inactive", "other": "value2"},
                    "geometry": geo,
                }
            ),
        ]
    )
    fc2 = fc.filter(filter).compute()
    assert len(fc2.features()) == 1
    assert fc2.features()[0]["properties"]["id"] == "f1"


def test_filter_date():
    """Test the Date filter."""
    filter = da.Filter.date(field="date_field", start="2023-01-01", end="2023-12-31")
    assert filter is not None
    out_dict = filter.to_dict()
    assert out_dict["_fn"] is not None
    del out_dict["_fn"]  # Remove the function for comparison
    assert filter.to_dict() == {
        "_type": "date",
        "_field": "date_field",
        "_start": "2023-01-01",
        "_end": "2023-12-31",
        "_feature_collection": None,
        "_match_key": "match_id",
        "_quality_key": "match_quality",
        "_join_fn": None,
    }


def test_filter_apply_feature_collection():
    """Test applying a FeatureCollection to a filter."""
    fc = da.FeatureCollection([])
    filter = da.Filter.date(field="date_field", start="2023-01-01", end="2023-12-31")
    assert filter is not None
    out_dict = filter.to_dict()
    assert out_dict["_fn"] is not None
    del out_dict["_fn"]  # Remove the function for comparison
    assert out_dict == {
        "_type": "date",
        "_field": "date_field",
        "_start": "2023-01-01",
        "_end": "2023-12-31",
        "_feature_collection": None,
        "_match_key": "match_id",
        "_quality_key": "match_quality",
        "_join_fn": None,
    }
    applied_filter = filter.apply_feature_collection(fc)
    assert applied_filter is not None
    out_dict = applied_filter.to_dict()
    assert out_dict["_fn"] is not None
    del out_dict["_fn"]  # Remove the function for comparison
    assert out_dict == {
        "_type": "date",
        "_field": "date_field",
        "_start": "2023-01-01",
        "_end": "2023-12-31",
        "_feature_collection": fc,
        "_match_key": "match_id",
        "_quality_key": "match_quality",
        "_join_fn": None,
    }
