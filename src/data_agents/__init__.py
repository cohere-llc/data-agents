"""Data Agents - A prototype for general data discovery and harmonization."""

__version__ = "0.1.0"

from . import adapters
from .adapters import TabularAdapter
from .core import Adapter, Router

__all__ = ["Adapter", "Router", "TabularAdapter", "adapters"]
