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

"""Integration tests for data_agents package."""

import data_agents as da


def test_nasa_power_example():
    da.Authenticate()

    muri_coring_fc = da.FeatureCollection.from_csv(
        "etc/nasa_power_example/muri_coring_locations.csv",
        da.Geometry.to_point(["Latitude", "Longitude"]),
    )

    # print all contents of the feature collection
    print(muri_coring_fc.get_info())

    # print just the properties available in the feature collection
    print(list(muri_coring_fc.properties().keys()))

    nasa_power_fc = da.FeatureCollection.from_service("NASA_POWER/DAILY/AG")

    # print the properties available from the NASA POWER FeatureCollection related to
    # temperature and precipitation
    print(
        [
            (key, val["name"])
            for key, val in nasa_power_fc.properties(".*temp.*").items()
        ]
    )
    print(
        [
            (key, val["name"])
            for key, val in nasa_power_fc.properties(".*precip.*").items()
        ]
    )

    # define a distance-based spatial filter to use with a join to match points within
    # 5 km
    spatial_filter = da.Filter.within_distance(
        left_field=".geo",
        right_field=".geo",
        distance=5000,  # distance in meters
    )

    # define a join that saves the best (closest) match only
    save_best_join = da.Join.save_best(
        matches_key="best_nasa_measurement", distance_key="distance"
    )

    # apply the join to link each feature in the Muri Coring collection to NASA POWER
    # features within 5 km and within the year 2024
    joined_fc = save_best_join.apply(
        muri_coring_fc, nasa_power_fc, spatial_filter
    ).filter(da.Filter.date(".date", "2024-01-01", "2024-12-31"))

    # plot the results
    print(joined_fc.get_info())
