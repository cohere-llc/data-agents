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

"""Test for the NASA POWER service module of data_agents package."""

from typing import Any

import pytest

import data_agents.services.nasa_power as nasa_power


def test_init_nasa_power_service():
    """Test the initialization of the NASA POWER service."""
    service = nasa_power.NasaPower(["NASA_POWER", "DAILY", "AG"])
    assert service is not None

    with pytest.raises(ValueError):
        nasa_power.NasaPower(["NASA_POWER", "MISSING_COMMUNITY"])

    with pytest.raises(ValueError):
        nasa_power.NasaPower(["NASA_POWER", "INVALID", "AG"])

    with pytest.raises(ValueError):
        nasa_power.NasaPower(["NASA_POWER", "DAILY", "INVALID"])

    with pytest.raises(ValueError):
        nasa_power.NasaPower(["NOT_NASA", "DAILY", "AG"])


def test_nasa_power_service_properties():
    """Test the properties of the NASA POWER service."""
    service = nasa_power.NasaPower(["NASA_POWER", "DAILY", "AG"])
    properties: dict[str, Any] = service.properties()
    assert "T2M_MAX" in properties  # Example property for maximum temperature
    assert "PRECTOTCORR" in properties  # Example property for total precipitation
    assert "temperature" in properties["T2M_MAX"]["name"].lower()

    temp_properties = service.properties(".*temper.*")
    assert "T2M_MAX" in temp_properties
    assert "T2M_MIN" in temp_properties
    assert "PRECTOTCORR" not in temp_properties

    temp_properties = service.properties(".*T2M.*")
    assert "T2M_MAX" in temp_properties
    assert "T2M_MIN" in temp_properties
    assert "PRECTOTCORR" not in temp_properties
