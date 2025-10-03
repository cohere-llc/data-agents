"""Data Agents - A prototype for general data discovery and harmonization."""

__version__ = "0.1.0"

from .core import Adapter, Router
from .adapters import TabularAdapter
from . import adapters

__all__ = ["Adapter", "Router", "TabularAdapter", "adapters"]
