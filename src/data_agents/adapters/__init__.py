"""Concrete adapter implementations for data agents."""

from .gbif_occurrence_adapter import GBIFOccurrenceAdapter
from .nasa_power_adapter import NasaPowerAdapter
from .openaq_adapter import OpenAQAdapter
from .rest_adapter import RESTAdapter
from .tabular_adapter import TabularAdapter

__all__ = [
    "TabularAdapter",
    "RESTAdapter",
    "NasaPowerAdapter",
    "GBIFOccurrenceAdapter",
    "OpenAQAdapter",
]
