"""Concrete adapter implementations for data agents."""

from .rest_adapter import RESTAdapter
from .tabular_adapter import TabularAdapter

__all__ = ["TabularAdapter", "RESTAdapter"]
