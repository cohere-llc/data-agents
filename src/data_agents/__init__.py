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

"""Data Agents - A prototype for KBase external data integration."""

from .feature import Feature
from .feature_collection import FeatureCollection
from .filter import Filter
from .geometry import Geometry
from .join import Join
from .services import NewServiceAdapter

FeatureCollection.from_service = staticmethod(NewServiceAdapter)  # type: ignore

__version__ = "0.2.0"

# Public API
__all__ = [
    "Feature",
    "FeatureCollection",
    "Filter",
    "Geometry",
    "Join",
]


def Authenticate() -> None:
    """Authenticate user with external services."""

    return
