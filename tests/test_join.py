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

"""Tests for the Join module of data_agents package."""

import pytest

import data_agents as da


def test_join():
    jn = da.Join()
    with pytest.raises(ValueError):
        jn.compute([])


def test_save_best():
    jn = da.Join.save_best("foo", "bar")
    geo = da.Geometry({"type": "Point", "coordinates": [0, 0]})
    fc1 = da.FeatureCollection(
        [
            da.Feature(
                {"properties": {"id": "f1", "foo": 10, "bar": 5}, "geometry": geo}
            ),
            da.Feature(
                {"properties": {"id": "f2", "foo": 3, "bar": 8}, "geometry": geo}
            ),
            da.Feature(
                {"properties": {"id": "f3", "foo": 7, "bar": 7}, "geometry": geo}
            ),
        ]
    )
    fc2 = da.FeatureCollection(
        [
            da.Feature(
                {"properties": {"id": "f1", "foo": 15, "bar": 2}, "geometry": geo}
            ),
            da.Feature(
                {"properties": {"id": "f2", "foo": 1, "bar": 9}, "geometry": geo}
            ),
            da.Feature(
                {"properties": {"id": "f3", "foo": 6, "bar": 10}, "geometry": geo}
            ),
        ]
    )
    flt = da.Filter.date(".date", "2023-01-01", "2023-12-31")
    fc3 = jn.apply(fc1, fc2, flt)
    assert fc3 is not None
    with pytest.raises(ValueError):
        jn.compute([])
